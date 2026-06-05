"""Shared low-level parsing utilities."""

import re
from collections.abc import Callable
from typing import Literal, NamedTuple

from .settings import Config


class StatementParts(NamedTuple):
    statements: list[str]


def split_statements(line: str, end_of_line_comment: str | None = None) -> StatementParts:
    """Split a line into individual statements, handling semicolons and comments.

    Returns a list of statements where the last statement includes any
    end-of-line comment that was present.
    """
    statements = [stmt.strip() for stmt in line.split(";")]
    if end_of_line_comment is not None:
        statements[-1] = f"{statements[-1]}#{end_of_line_comment}"
    return StatementParts(statements=statements)


class StripSyntaxResult(NamedTuple):
    just_imports: list[str]


def extract_import_names(import_string: str) -> StripSyntaxResult:
    """Extract import module/attribute names from an import string.

    Uses strip_syntax to remove Python syntax characters, then splits
    into individual import name tokens. Handles the {|/|} placeholder
    conversion for curly braces.
    """
    just_imports = [
        item.replace("{|", "{ ").replace("|}", " }")
        for item in strip_syntax(import_string).split()
    ]
    return StripSyntaxResult(just_imports=just_imports)


class AliasInfo(NamedTuple):
    module: str
    attribute: str | None
    alias: str
    is_from_import: bool


class AliasParseResult(NamedTuple):
    aliases: list[AliasInfo]
    remaining_imports: list[str]
    top_level_module: str


def parse_aliases(
    just_imports: list[str],
    type_of_import: str,
) -> AliasParseResult:
    """Parse 'as' aliases from a list of import names.

    Returns the list of aliases found, the remaining import names
    (with aliases removed), and the top-level module for from-imports.
    """
    aliases: list[AliasInfo] = []
    remaining = list(just_imports)
    top_level_module = ""

    while "as" in remaining and (remaining.index("as") + 1) < len(remaining):
        as_index = remaining.index("as")
        if type_of_import == "from":
            attribute = remaining[as_index - 1]
            top_level_module = remaining[0]
            alias = remaining[as_index + 1]
            remaining.remove(attribute)
            remaining.remove(alias)
            remaining.remove("as")
            aliases.append(AliasInfo(
                module=top_level_module,
                attribute=attribute,
                alias=alias,
                is_from_import=True,
            ))
        else:
            module = remaining[as_index - 1]
            alias = remaining[as_index + 1]
            remaining.remove(alias)
            remaining.remove("as")
            remaining.remove(module)
            aliases.append(AliasInfo(
                module=module,
                attribute=None,
                alias=alias,
                is_from_import=False,
            ))

    return AliasParseResult(
        aliases=aliases,
        remaining_imports=remaining,
        top_level_module=top_level_module,
    )


class AliasInfoWithModule(AliasInfo):
    """AliasInfo that includes the full dotted module name."""


class AliasParseResultWithModule(NamedTuple):
    aliases: list[AliasInfoWithModule]
    remaining_imports: list[str]
    top_level_module: str


def parse_aliases_with_full_module(
    just_imports: list[str],
    type_of_import: str,
) -> AliasParseResultWithModule:
    """Parse 'as' aliases, returning full dotted module names for from-imports.

    This variant is used by parse.py which needs the full module path
    (e.g., 'os.path' instead of just 'os') for comment tracking.
    """
    aliases: list[AliasInfoWithModule] = []
    remaining = list(just_imports)
    top_level_module = ""

    while "as" in remaining and (remaining.index("as") + 1) < len(remaining):
        as_index = remaining.index("as")
        if type_of_import == "from":
            attribute = remaining[as_index - 1]
            top_level_module = remaining[0]
            alias = remaining[as_index + 1]
            remaining.remove(attribute)
            remaining.remove(alias)
            remaining.remove("as")
            aliases.append(AliasInfoWithModule(
                module=top_level_module + "." + attribute,
                attribute=attribute,
                alias=alias,
                is_from_import=True,
            ))
        else:
            module = remaining[as_index - 1]
            alias = remaining[as_index + 1]
            remaining.remove(alias)
            remaining.remove("as")
            remaining.remove(module)
            aliases.append(AliasInfoWithModule(
                module=module,
                attribute=None,
                alias=alias,
                is_from_import=False,
            ))

    return AliasParseResultWithModule(
        aliases=aliases,
        remaining_imports=remaining,
        top_level_module=top_level_module,
    )


def is_cimport(import_string: str) -> bool:
    """Check if an import string uses cimport syntax."""
    return " cimport " in import_string or import_string.startswith("cimport")


class NormalizeLineResult(NamedTuple):
    normalized_line: str
    raw_line: str


def normalize_line(raw_line: str) -> NormalizeLineResult:
    """Normalizes import related statements in the provided line."""
    line = re.sub(r"from(\.+)cimport ", r"from \g<1> cimport ", raw_line)
    line = re.sub(r"from(\.+)import ", r"from \g<1> import ", line)
    line = line.replace("import*", "import *")
    line = re.sub(r" (\.+)import ", r" \g<1> import ", line)
    line = re.sub(r" (\.+)cimport ", r" \g<1> cimport ", line)
    line = line.replace("\t", " ")
    return NormalizeLineResult(normalized_line=line, raw_line=raw_line)


def strip_syntax(import_string: str) -> str:
    import_string = import_string.replace("_import", "[[i]]")
    import_string = import_string.replace("_cimport", "[[ci]]")
    for remove_syntax in ["\\", "(", ")", ","]:
        import_string = import_string.replace(remove_syntax, " ")
    import_list = import_string.split()
    for key in ("from", "import", "cimport"):
        if key in import_list:
            import_list.remove(key)
    import_string = " ".join(import_list)
    import_string = import_string.replace("[[i]]", "_import")
    import_string = import_string.replace("[[ci]]", "_cimport")
    return import_string.replace("{ ", "{|").replace(" }", "|}")


class SkipLineResult(NamedTuple):
    should_skip: bool
    in_quote: str


# Ignore DeepSource cyclomatic complexity check for this function.
# skipcq: PY-R1000
def skip_line(line: str, in_quote: str, needs_import: bool = True) -> SkipLineResult:
    """Determine if a given line should be skipped."""
    should_skip = bool(in_quote)
    if '"' in line or "'" in line:
        char_index = 0
        while char_index < len(line):
            if line[char_index] == "\\":
                char_index += 1
            elif in_quote:
                if line[char_index : char_index + len(in_quote)] == in_quote:
                    in_quote = ""
            elif line[char_index] in ("'", '"'):
                long_quote = line[char_index : char_index + 3]
                if long_quote in ('"""', "'''"):
                    in_quote = long_quote
                    char_index += 2
                else:
                    in_quote = line[char_index]
            elif line[char_index] == "#":
                break
            char_index += 1

    if ";" in line.split("#")[0] and needs_import:
        for part in (part.strip() for part in line.split(";")):
            if (
                part
                and not part.startswith("from ")
                and not part.startswith(("import ", "cimport "))
            ):
                should_skip = True

    return SkipLineResult(should_skip=bool(should_skip or in_quote), in_quote=in_quote)


class ExtraLine(NamedTuple):
    line: str
    comment: str | None


class ImportContinuationResult(NamedTuple):
    final_line: str
    complete_import_string: str
    extra_lines: list[ExtraLine]


def collect_import_continuation(
    line: str,
    import_string: str,
    get_next_line: Callable[[], tuple[str, str | None]],
    line_separator: str = "\n",
) -> ImportContinuationResult:
    r"""Collect continuation lines for a multi-line import statement.

    Handles both parenthesised imports ``from X import (`` + newline + ``    Y, Z)``
    and backslash-continued imports ``import Y, \\`` + newline + ``    Z``.
    """
    extra_lines: list[ExtraLine] = []

    if "(" in line.split("#", 1)[0]:
        while not line.split("#")[0].strip().endswith(")"):
            try:
                line, comment = get_next_line()
            except StopIteration:
                break
            extra_lines.append(ExtraLine(line=line, comment=comment))
            import_string += line_separator + line
    else:
        while line.strip().endswith("\\"):
            try:
                line, comment = get_next_line()
            except StopIteration:
                break
            line = line.lstrip()

            # Still need to check for parentheses after an escaped line
            if "(" in line.split("#")[0] and ")" not in line.split("#")[0]:
                extra_lines.append(ExtraLine(line=line, comment=comment))
                import_string += line_separator + line

                while not line.split("#")[0].strip().endswith(")"):
                    try:
                        line, comment = get_next_line()
                    except StopIteration:
                        break
                    extra_lines.append(ExtraLine(line=line, comment=comment))
                    import_string += line_separator + line
            else:
                if import_string.strip().endswith(
                    (" import", " cimport")
                ) or line.strip().startswith(("import ", "cimport ")):
                    extra_lines.append(ExtraLine(line=line, comment=comment))
                    import_string += line_separator + line
                else:
                    extra_lines.append(ExtraLine(line=line, comment=comment))
                    import_string = import_string.rstrip().rstrip("\\") + " " + line.lstrip()

    return ImportContinuationResult(
        final_line=line,
        complete_import_string=import_string,
        extra_lines=extra_lines,
    )


def normalize_from_import_string(import_string: str) -> str:
    """Normalize a ``from … import …`` string, handling line-continuation characters.

    Removes ``import(``, backslash continuations and embedded newlines, then
    reconstructs the canonical ``from X import Y, Z`` form.
    """
    import_string = (
        import_string.replace("import(", "import (").replace("\\", " ").replace("\n", " ")
    )
    cimports = " cimport " in import_string
    parts = import_string.split(" cimport " if cimports else " import ")
    from_import = parts[0].split(" ")
    return (" cimport " if cimports else " import ").join(
        [from_import[0] + " " + "".join(from_import[1:]), *parts[1:]]
    )


# TODO: Return a `StrEnum` once we no longer support Python 3.10.
def import_type(
    line: str, config: Config
) -> Literal["from", "straight", "lazy_from", "lazy_straight"] | None:
    """If the current line is an import line it will return its type."""
    if config.honor_noqa and line.lower().rstrip().endswith("noqa"):
        return None
    if "isort:skip" in line or "isort: skip" in line or "isort: split" in line:
        return None
    if line.startswith(("import ", "cimport ")):
        return "straight"
    if line.startswith("from "):
        return "from"
    if line.startswith("lazy import "):
        return "lazy_straight"
    if line.startswith("lazy from "):
        return "lazy_from"
    return None

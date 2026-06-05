"""Fast stream based import identification.
Eventually this will likely replace parse.py
"""

from collections.abc import Iterator
from functools import partial
from pathlib import Path
from typing import NamedTuple, TextIO

from ._parse_utils import (
    collect_import_continuation,
    extract_import_names,
    import_type,
    is_cimport,
    normalize_from_import_string,
    normalize_line,
    parse_aliases,
    skip_line,
    split_statements,
)
from .comments import parse as parse_comments
from .settings import DEFAULT_CONFIG, Config

STATEMENT_DECLARATIONS: tuple[str, ...] = ("def ", "cdef ", "cpdef ", "class ", "@", "async def")


class Import(NamedTuple):
    line_number: int
    indented: bool
    module: str
    attribute: str | None = None
    alias: str | None = None
    cimport: bool = False
    file_path: Path | None = None

    def statement(self) -> str:
        import_cmd = "cimport" if self.cimport else "import"
        if self.attribute:
            import_string = f"from {self.module} {import_cmd} {self.attribute}"
        else:
            import_string = f"{import_cmd} {self.module}"
        if self.alias:
            import_string += f" as {self.alias}"
        return import_string

    def __str__(self) -> str:
        return (
            f"{self.file_path or ''}:{self.line_number} "
            f"{'indented ' if self.indented else ''}{self.statement()}"
        )


# Ignore DeepSource cyclomatic complexity check for this function.
# skipcq: PY-R1000
def imports(
    input_stream: TextIO,
    config: Config = DEFAULT_CONFIG,
    file_path: Path | None = None,
    top_only: bool = False,
) -> Iterator[Import]:
    """Parses a python file taking out and categorizing imports."""
    in_quote = ""

    indexed_input = enumerate(input_stream)
    for index, raw_line in indexed_input:
        (skipping_line, in_quote) = skip_line(raw_line, in_quote=in_quote)

        if top_only and not in_quote and raw_line.startswith(STATEMENT_DECLARATIONS):
            break
        if skipping_line:
            continue

        stripped_line = raw_line.strip().split("#")[0]
        if stripped_line.startswith(("raise", "yield")):
            if stripped_line == "yield":
                while not stripped_line or stripped_line == "yield":
                    try:
                        index, next_line = next(indexed_input)
                    except StopIteration:
                        break

                    stripped_line = next_line.strip().split("#")[0]
            while stripped_line.endswith("\\"):
                try:
                    index, next_line = next(indexed_input)
                except StopIteration:
                    break

                stripped_line = next_line.strip().split("#")[0]
            continue  # pragma: no cover

        line, *end_of_line_comment = raw_line.split("#", 1)
        statements = split_statements(
            line, end_of_line_comment[0] if end_of_line_comment else None
        ).statements

        for statement in statements:
            line, _raw_line = normalize_line(statement)
            type_of_import = import_type(line, config)
            if type_of_import is None:
                continue  # pragma: no cover

            import_string, _ = parse_comments(line)

            identified_import = partial(
                Import,
                index + 1,  # line numbers use 1 based indexing
                raw_line.startswith((" ", "\t")),
                file_path=file_path,
            )

            _, import_string, _ = collect_import_continuation(
                line,
                import_string,
                # We can disregard `index` here because it is no longer accessed after this line.
                lambda: parse_comments(next(indexed_input)[1]),
            )

            if type_of_import == "from":
                import_string = normalize_from_import_string(import_string)

            cimports: bool = is_cimport(import_string)

            identified_import = partial(identified_import, cimport=cimports)

            import_names_result = extract_import_names(import_string)
            just_imports = import_names_result.just_imports

            direct_imports = just_imports[1:]
            top_level_module = ""
            if "as" in just_imports and (just_imports.index("as") + 1) < len(just_imports):
                alias_result = parse_aliases(just_imports, type_of_import)
                top_level_module = alias_result.top_level_module
                for alias_info in alias_result.aliases:
                    if alias_info.is_from_import:
                        if alias_info.attribute == alias_info.alias and config.remove_redundant_aliases:
                            yield identified_import(alias_info.module, alias_info.attribute)
                        else:
                            yield identified_import(alias_info.module, alias_info.attribute, alias=alias_info.alias)
                    else:
                        if alias_info.module == alias_info.alias and config.remove_redundant_aliases:
                            yield identified_import(alias_info.module)
                        else:
                            yield identified_import(alias_info.module, alias=alias_info.alias)
                just_imports = alias_result.remaining_imports

            if just_imports:
                if type_of_import == "from":
                    module = just_imports.pop(0)
                    for attribute in just_imports:
                        yield identified_import(module, attribute)
                else:
                    for module in just_imports:
                        yield identified_import(module)

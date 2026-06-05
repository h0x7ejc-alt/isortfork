import isort.literal
from isort.settings import Config

print(isort.literal.assignment('y = {"z": "a", "b": "c"}', "dict", "py"))

import json
from isort.settings import Config

c = Config()
print(json.dumps(c.sources, indent=2))

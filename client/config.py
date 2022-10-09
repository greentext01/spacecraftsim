"Reads the config file"
import json
from pathlib import Path


config: dict = json.loads((Path(".") / "client_config.json").read_text())
if not isinstance(config, dict):
    raise TypeError("Invalid config file: The root should be a JSON object.")

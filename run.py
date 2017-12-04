import yaml
import io
from HomeBase.Server import start

config = None
with io.open("config.yaml.demo") as f:
  config = yaml.load(f)

start(config)
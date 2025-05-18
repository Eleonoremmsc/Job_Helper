import yaml
from yaml.loader import SafeLoader

def load_auth_config(path="config.yaml"):
    with open(path) as file:
        return yaml.load(file, Loader=SafeLoader)

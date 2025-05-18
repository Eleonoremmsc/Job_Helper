# auth_config.py
import yaml
from yaml.loader import SafeLoader

def load_auth_config(path=".streamlit/config.yaml"):
    with open(path) as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

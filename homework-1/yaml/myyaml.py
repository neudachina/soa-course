import yaml

from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from lib import object
from lib import create
from lib import support


def deserialized(yamlstr):
    obj = object.Object()
    return obj.update(yaml.load(yamlstr, yaml.BaseLoader))


create.create_server(support.yamlName, yaml.dump, deserialized)

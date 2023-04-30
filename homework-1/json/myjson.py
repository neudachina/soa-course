import json

from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from lib import object
from lib import create
from lib import support


def serialize(obj):
    return json.dumps(obj.__dict__)


def deserialize(jsonstr):
    obj = object.Object()
    return obj.update(json.loads(jsonstr))


create.create_server(support.jsonName, serialize, deserialize)

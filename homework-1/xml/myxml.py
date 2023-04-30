import dict2xml
import xmltodict

from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from lib import object
from lib import create
from lib import support


wrapping = 'object'


def serialize(obj):
    return dict2xml.dict2xml(obj.__dict__, wrap=wrapping)


def deserialize(xmlstr):
    parsed = xmltodict.parse(xmlstr)
    obj = object.Object()
    return obj.update(parsed[wrapping])


create.create_server(support.xmlName, serialize, deserialize)

import schema_pb2

from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from lib import create
from lib import support


def serialize(_value):
    obj = schema_pb2.Object()
    obj.integer = 42
    obj.floating = 3.1415
    obj.str = "hello, world!"
    obj.list.extend([1, 2, 3])
    for value in ['a', 'b', 'c']:
        obj.dictionary[value] = value

    return obj.SerializeToString()


def deserialize(protobufstr):
    return schema_pb2.Object().ParseFromString(protobufstr)


create.create_server(support.protobufName, serialize, deserialize)

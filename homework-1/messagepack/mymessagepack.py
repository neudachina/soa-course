import msgpack

from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from lib import create
from lib import support


def serialize(obj):
    return msgpack.dumps(obj.__dict__)


create.create_server(support.messagepackName, serialize, msgpack.loads)


import pickle

from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from lib import create
from lib import support


create.create_server(support.nativeName, pickle.dumps, pickle.loads)
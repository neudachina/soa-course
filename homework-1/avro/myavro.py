import avro
from avro.io import DatumWriter, BinaryEncoder, DatumReader, BinaryDecoder
from io import BytesIO

from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from lib import object
from lib import create
from lib import support


definition = avro.schema.parse(support.avroDefinition)

def serialize(obj):
    out = BytesIO()
    encoder = BinaryEncoder(out)
    writer = DatumWriter(definition)
    writer.write(obj.__dict__, encoder)
    return out.getvalue()


def deserialize(avrostr):
    in_bytes = BytesIO(avrostr)
    decoder = BinaryDecoder(in_bytes)
    reader = DatumReader(definition)

    obj = object.Object()
    obj.update(reader.read(decoder))
    return obj


create.create_server(support.avroName, serialize, deserialize)

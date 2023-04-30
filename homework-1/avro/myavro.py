import socket
import avro
from avro.io import DatumWriter, BinaryEncoder, DatumReader, BinaryDecoder
from io import BytesIO

from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from lib import testing
from lib import support
from lib import object

import struct
import select

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

socket_unicast = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socket_multicast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

socket_unicast.bind((support.localIP, support.avroPort))
socket_multicast.bind((support.multicastIP, support.multicastPort))

mreq = struct.pack("=4sl", socket.inet_aton(support.multicastIP), socket.INADDR_ANY)
socket_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

sockets = [socket_unicast, socket_multicast]

while True:
    ready_sockets, _, _ = select.select(sockets, [], [])
    for sock in ready_sockets:
        message, address = sock.recvfrom(support.bufferSize)
        if message == support.defaultMessage:
            answer = testing.test(serialize, deserialize, 'avro')
            sock.sendto(answer.encode(), address)

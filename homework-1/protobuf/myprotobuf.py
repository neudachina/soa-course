import socket
import schema_pb2

from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from lib import testing
from lib import support

import struct
import select


def serialized(_value):
    obj = schema_pb2.Object()
    obj.integer = 42
    obj.floating = 3.1415
    obj.str = "hello, world!"
    obj.list.extend([1, 2, 3])
    for value in ['a', 'b', 'c']:
        obj.dictionary[value] = value

    return obj.SerializeToString()


def deserialized(protobufstr):
    return schema_pb2.Object().ParseFromString(protobufstr)

socket_unicast = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socket_multicast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

socket_unicast.bind((support.localIP, support.protobufPort))
socket_multicast.bind((support.multicastIP, support.multicastPort))

mreq = struct.pack("=4sl", socket.inet_aton(support.multicastIP), socket.INADDR_ANY)
socket_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

sockets = [socket_unicast, socket_multicast]

while True:
    ready_sockets, _, _ = select.select(sockets, [], [])
    for sock in ready_sockets:
        message, address = sock.recvfrom(support.bufferSize)
        if message == support.defaultMessage:
            answer = testing.test(serialized, deserialized, 'protobuf')
            sock.sendto(answer.encode(), address)
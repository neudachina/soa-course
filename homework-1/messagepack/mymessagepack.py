import socket
import msgpack

from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from lib import testing
from lib import support

import struct
import select


def serialize(obj):
    return msgpack.dumps(obj.__dict__)



socket_unicast = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socket_multicast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

socket_unicast.bind((support.localIP, support.messagepackPort))
socket_multicast.bind((support.multicastIP, support.multicastPort))

mreq = struct.pack("=4sl", socket.inet_aton(support.multicastIP), socket.INADDR_ANY)
socket_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

sockets = [socket_unicast, socket_multicast]

while True:
    ready_sockets, _, _ = select.select(sockets, [], [])
    for sock in ready_sockets:
        message, address = sock.recvfrom(support.bufferSize)
        if message == support.defaultMessage:
            answer = testing.test(serialize, msgpack.loads, 'message pack')
            sock.sendto(answer.encode(), address)

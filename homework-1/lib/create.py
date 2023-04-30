import socket
import struct
import select

from pathlib import Path
import sys
path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

from lib import testing
from lib import support


def create_server(server_name, serialization_func, deserialization_func):
    socket_unicast = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    socket_multicast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    socket_unicast.bind((support.localIP, support.addresses[server_name][1]))
    socket_multicast.bind(support.addresses[support.allRequest])

    mreq = struct.pack("=4sl", socket.inet_aton(support.multicastIP), socket.INADDR_ANY)
    socket_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    sockets = [socket_unicast, socket_multicast]

    while True:
        ready_sockets, _, _ = select.select(sockets, [], [])
        for sock in ready_sockets:
            message, address = sock.recvfrom(support.bufferSize)
            if message == support.defaultMessage:
                answer = testing.test(serialization_func, deserialization_func, server_name)
                sock.sendto(answer.encode(), address)

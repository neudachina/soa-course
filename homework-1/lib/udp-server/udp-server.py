import socket

from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

import support

socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
socket.bind((support.localIP, support.serverPort))

while True:
    message, address = socket.recvfrom(support.bufferSize)
    request, serialization_type = message.strip().split(b' ')[:2]
    if request == support.getRequest:
        if serialization_type in list(support.addresses.keys()):
            addr = support.addresses[serialization_type]
            socket.sendto(support.defaultMessage, addr)
            if serialization_type == support.allRequest:
                for _ in range(support.formats):
                    answer, _ = socket.recvfrom(support.bufferSize)
                    socket.sendto(answer, address)
                continue
            else:
                answer = socket.recv(support.bufferSize)
        else:
            answer = support.unknownSerializationTypeMessage
    else:
        answer = support.unknownRequestTypeMessage

    socket.sendto(answer, address)

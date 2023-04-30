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
    message = message.strip().split(b' ')
    if message[0] == support.getRequest:
        if message[1] == support.nativeRequest:
            addr = (support.nativeIP, support.nativePort)
            socket.sendto(support.defaultMessage, addr)
        elif message[1] == support.xmlRequest:
            addr = (support.xmlIP, support.xmlPort)
            socket.sendto(support.defaultMessage, addr)
        elif message[1] == support.jsonRequest:
            addr = (support.jsonIP, support.jsonPort)
            socket.sendto(support.defaultMessage, addr)
        elif message[1] == support.yamlRequest:
            addr = (support.yamlIP, support.yamlPort)
            socket.sendto(support.defaultMessage, addr)
        elif message[1] == support.messagepackRequest:
            addr = (support.messagepackIP, support.messagepackPort)
            socket.sendto(support.defaultMessage, addr)
        elif message[1] == support.protobufRequest:
            addr = (support.protobufIP, support.protobufPort)
            socket.sendto(support.defaultMessage, addr)
        elif message[1] == support.avroRequest:
            addr = (support.avroIP, support.avroPort)
            socket.sendto(support.defaultMessage, addr)
        elif message[1] == support.allRequest:
            addr = (support.multicastIP, support.multicastPort)
            socket.sendto(support.defaultMessage, addr)
        else:
            answer = support.unknownSerializationTypeMessage
            socket.sendto(answer, address)
    else:
        answer = support.unknownRequestTypeMessage
        socket.sendto(answer, address)

    if message[1] == support.allRequest:
        for _ in range(support.formats):
            answer, _ = socket.recvfrom(support.bufferSize)
            socket.sendto(answer, address)
    else:
        answer = socket.recv(support.bufferSize)
        socket.sendto(answer, address)

import os

bufferSize = 1024
formats = 7

defaultMessage = b'get_time'
unknownSerializationTypeMessage = b'unknown serialization type\n'
unknownRequestTypeMessage = b'unknown request type\n'

getRequest = b'get_result'

serverIP = 'server'
nativeIP = 'native'
xmlIP = 'xml'
jsonIP = 'json'
yamlIP = 'yaml'
messagepackIP = 'messagepack'
protobufIP = 'protobuf'
avroIP = 'avro'

localIP = "0.0.0.0"
multicastIP = os.getenv("multicastIP", default="224.0.0.0")

serverPort = 2000
nativePort = 2001
multicastPort = 2002
jsonPort = 2003
yamlPort = 2004
messagepackPort = 2005
protobufPort = 2006
avroPort = 2007
xmlPort = 2008

clientPort = 3000

addresses = {
    b'ALL': (multicastIP, multicastPort),
    b'NATIVE': (nativeIP, nativePort),
    b'XML': (xmlIP, xmlPort),
    b'JSON': (jsonIP, jsonPort),
    b'YAML': (yamlIP, yamlPort),
    b'MESSAGEPACK': (messagepackIP, messagepackPort),
    b'PROTOBUF': (protobufIP, protobufPort),
    b'AVRO': (avroIP, avroPort)
}

avroDefinition = """{
    "namespace": "object.avro",
    "type": "record",
    "name": "Object",
    "fields": [
        {"name": "integer", "type": "int"},
        {"name": "floating", "type": "float"},
        {"name": "str", "type": "string"},
        { "name": "list", "type": {"type": "array", "items": "int"}},
        {"name": "dictionary", "type": {"type": "map", "values": "string"}}
    ]
}
"""
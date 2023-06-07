from __future__ import print_function
from signal import signal, SIGINT

import grpc
import time

from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

import protos.mafia_pb2_grpc as mafia_pb2_grpc
import protos.mafia_pb2 as mafia_pb2

import threading
import random

class Client:
    def __init__(self):
            # def handle_sigterm(*_):
            #     self.disconnect()

            # signal(SIGINT, handle_sigterm)
            self.name = ''
            self.session: int = 100001234352467
            with grpc.insecure_channel('localhost:50051') as channel:
                self.stub = mafia_pb2_grpc.MafiaStub(channel)
                client_str = input('enter "1" if you want to enter automatic mode, otherwise enter "0"\n')
                while True:
                    if client_str != '0' and client_str != '1':
                        client_str = input('invalid input. try again, please\n') 
                    else:
                        self.bot = bool(int(client_str))
                        break
                if self.bot:
                    print(f'\nBOT MODE ENABLED')
                self.connect()
                
                    
    # def generate_disconnect(self):
    #     print('DISCONNECTED\n\n')
    #     return mafia_pb2.ConnectionClientRequest(
    #         name=self.name,
    #         session=self.session
    #     )
                        
    def disconnect(self):
        # print('DISCONNECT')
        self.stub.disconnect(mafia_pb2.DisconnectClientRequest(
            name=self.name,
            session=self.session
        ))
        print('\nDISCONNECTED\n')
            

    def generate_connection_name_info(self):
        yield mafia_pb2.ConnectionClientRequest(
            name=self.name
        )

    def connect(self):
        try:
            if not self.bot:
                print('\nhello, player! introduce yourself please: ', end='')
            game_starts = False
            while not game_starts:
                if self.bot:
                    self.name = 'bot' + str(random.randint(1, 1000))
                else:
                    self.name = input().strip()
                    print('')
                responses = self.stub.connect(self.generate_connection_name_info())
                for response in responses:
                    if response.type == mafia_pb2.ConnectionMessageType.INFO:
                        print(response.message)
                    elif response.type == mafia_pb2.ConnectionMessageType.SESSION_NUMBER:
                        self.session = int(response.session_number)
                    else:
                        print(response.message)
                        if response.type == mafia_pb2.ConnectionMessageType.GAME_BEGINS:
                            game_starts = True
                        break

            self.day()
        except:
            # print('\n\ndisconnected in connect')
            self.disconnect()
            # pass

    def day(self):
        game_ends = False
        responses = self.stub.day(self.generate_day_message(mafia_pb2.DayClientCommand.INIT))
        
        if not self.bot:
            input_required, day_ends = True, False
            while not day_ends:
                for response in responses:
                    if response.message != '':
                        print(response.message)
                    if response.type == mafia_pb2.DayMessageType.DAY_ENDS:
                        day_ends = True
                        game_ends = response.ending
                        break

                    if response.type == mafia_pb2.DayMessageType.INFO_NO_INPUT:
                        input_required = False
                        
                    while input_required:
                        commands = input('YOUR INPUT: ').lstrip().strip().split()
                        while len(commands) == 0:
                                print('\nyou haven\'t endtered any command. choose one from the list, please')
                                tmp = input().lstrip().strip().split()
                                if len(tmp) != 0:
                                    commands.append(tmp[0])
                        print(f'CHOSEN COMMAND: {commands[0]}', end='')
                        if commands[0] == 'execute':
                            while len(commands) == 1:
                                print('\nyou haven\'t endtered any name. choose one from the list, please')
                                tmp = input().lstrip().strip().split()
                                if len(tmp) != 0:
                                    commands.append(tmp[0])
                            print(f'\nCHOSEN PLAYER: {commands[1]}\n')
                            for response in responses:
                                if response.message != '':
                                    print(response.message)
                            responses = self.stub.day(self.generate_day_message(
                                command=mafia_pb2.DayClientCommand.EXECUTE,
                                info=commands[1]
                            ))
                        elif commands[0] == 'reveal':
                            print('\n')
                            for response in responses:
                                if response.message != '':
                                    print(response.message)
                            responses = self.stub.day(self.generate_day_message(mafia_pb2.DayClientCommand.REVEAL))
                        elif commands[0] == 'end':
                            print('\n')
                            for response in responses:
                                print(response.message)
                            responses = self.stub.day(self.generate_day_message(mafia_pb2.DayClientCommand.ENDING))
                            input_required = False
                            break
                        else:
                            print('\nincorrect input. try again, please\n')
                    
        else:
            alive, commands = list(), list()

            input_required, day_ends = True, False
            while not day_ends:
                for response in responses:
                    if not alive and not commands:
                        msg = response.message.lstrip().strip().split('\n')[1:]
                        alive = list(map(str.strip, msg[0].split(':')[1].split(',')))
                        commands = ' '.join(msg[1:]).split('"')[1::2]
                    if response.message != '':
                        print(response.message)
                        # time.sleep(2)
                    if response.type == mafia_pb2.DayMessageType.DAY_ENDS:
                        day_ends = True
                        game_ends = response.ending
                        break

                    if response.type == mafia_pb2.DayMessageType.INFO_NO_INPUT:
                        input_required = False
                            
                    if input_required:
                        random.shuffle(commands)
                        command = commands[0]
                        print(f'CHOSEN COMMAND: {command}', end='')
                        commands.pop(0)
                        if command == 'execute':
                            random.shuffle(alive)
                            print(f'\nCHOSEN PLAYER: {alive[0]}\n')
                            for response in responses:
                                if response.message != '':
                                    print(response.message)
                                    # time.sleep(2)
                            responses = self.stub.day(self.generate_day_message(
                                command=mafia_pb2.DayClientCommand.EXECUTE,
                                info=alive[0]
                            ))
                        elif command == 'reveal':
                            print('\n')
                            for response in responses:
                                if response.message != '':
                                    print(response.message)
                                    # time.sleep(2)
                            responses = self.stub.day(self.generate_day_message(mafia_pb2.DayClientCommand.REVEAL))
                        elif command == 'end':
                            print('\n')
                            # print('in end')
                            for response in responses:
                                print(response.message)
                                # time.sleep(2)
                            responses = self.stub.day(self.generate_day_message(mafia_pb2.DayClientCommand.ENDING))
                            input_required = False
                            break

        if not game_ends:
            self.night()
        
    def night(self):

        responses = self.stub.night(self.generate_day_message(mafia_pb2.NightClientCommand.INIT_NIGHT))
        input_required, night_ends, game_ends = True, False, False
        if not self.bot:
            while not night_ends:
                for response in responses:
                    print(response.message)
                    if response.type == mafia_pb2.NightMessageType.NIGHT_ENDS:
                        night_ends = True
                        game_ends = response.ending
                        break

                    if response.type == mafia_pb2.NightMessageType.INFO_NO_INPUT_NIGHT:
                        input_required = False
                        break
                        
                    if input_required:
                        commands = input().strip().split()
                        responses = self.stub.night(self.generate_night_message(
                            command=mafia_pb2.NightClientCommand.PLAYING,
                            info=commands[0]
                        ))
                        break
                    
        else:
            alive, commands = list(), list()
            while not night_ends:
                for response in responses:
                    print(response.message)
                    # time.sleep(2)
                    if response.type == mafia_pb2.NightMessageType.NIGHT_ENDS:
                        night_ends = True
                        game_ends = response.ending
                        # time.sleep(2)
                        break

                    if response.type == mafia_pb2.NightMessageType.INFO_NO_INPUT_NIGHT:
                        input_required = False
                        break
                        
                    if input_required:
                        alive = list(map(str.strip, response.message.lstrip().strip().split('\n')[1].split(':')[1].split(',')))
                        random.shuffle(alive)
                        print(f'CHOSEN PLAYER: {alive[0]}\n')
                        responses = self.stub.night(self.generate_night_message(
                            command=mafia_pb2.NightClientCommand.PLAYING,
                            info=alive[0]
                        ))
                        break
                        
        if not game_ends:
            self.day()
        
    def generate_night_message(self, command, info=None):
        if info is None:
            return mafia_pb2.DayClientRequest(
                command=command,
                name=self.name,
                session_number=self.session
            )
        else:
            return mafia_pb2.DayClientRequest(
                command=command,
                additional=info,
                name=self.name,
                session_number=self.session
            )

    def generate_day_message(self, command, info=None):
        if info is None:
            return mafia_pb2.DayClientRequest(
                command=command,
                name=self.name,
                session_number=self.session
            )
        else:
            return mafia_pb2.DayClientRequest(
                command=command,
                additional=info,
                name=self.name,
                session_number=self.session
            )


if __name__ == '__main__':
    Client()

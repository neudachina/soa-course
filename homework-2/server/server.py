from concurrent import futures

import time
import random
# import queue
import asyncio

import copy

import grpc

import sys
sys.stdout.flush()


from pathlib import Path
import sys

path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

import protos.mafia_pb2 as mafia_pb2
import protos.mafia_pb2_grpc as mafia_pb2_grpc

class MafiaService(mafia_pb2_grpc.MafiaServicer):

    class Session:
        class Player:
            def __init__(self):
                self.role = ''
                self.alive = True
                self.message_queue = asyncio.Queue()

        def __init__(self):
            self.alive = list()
            self.players: dict[str, MafiaService.Session.Player] = dict()
            self.votes: dict[str, str] = dict()
            self.want_to_end = 0
            self.mafia = ''
            self.first_day = True
            self.message_night = ''
            self.night = 0
            self.dead = ''

    def __init__(self):
        self.sessions: dict[int, MafiaService.Session] = dict()
        self.counter = 0

    def put_message_to_everybody(self, message, session, to_self=True, name=None):
        players = self.sessions[session].players.keys()
        for player in players:
            if to_self or player != name:
                print(f'in put message {message} for {player} in session {session}', flush=True)
                self.sessions[session].players[player].message_queue.put_nowait(copy.deepcopy(message))

    def put_message(self, message, name, session):
        self.sessions[session].players[name].message_queue.put_nowait(copy.deepcopy(message))

    def connect(self, request_iterator, context):
            if self.counter == len(self.sessions):
                self.sessions[self.counter] = MafiaService.Session()

            counter = self.counter
            current_session = self.sessions[counter]
            connected = False
            name = ''
            while not connected:
                for message in request_iterator:
                    name = message.name
                    if name in list(current_session.players.keys()):
                        yield mafia_pb2.ConnectionServerResponse(
                            type=mafia_pb2.ConnectionMessageType.NOT_UNIQUE_NAME,
                            message='the name you entered already exists. try again, please:'
                        )
                    else:
                        current_session.players[name] = MafiaService.Session.Player()
                        current_session.alive.append(name)
                        connected = True

                        response = f"hooray! connection of new player {name} succeeded!"
                        self.put_message_to_everybody(
                            message=mafia_pb2.ConnectionServerResponse(
                                type=mafia_pb2.ConnectionMessageType.INFO,
                                message=response
                            ), session=counter
                        )

                        players = list(current_session.players.keys())
                        players.remove(name)
                        length = len(players)
                        if length != 0:
                            response = f"player{'s' if length > 1 else ''} " \
                                        f"{', '.join(players)}" \
                                        f"{' are' if length > 1 else ' is'} already connected"
                        else:
                            response = "you were the first, waiting for new players to connect..."

                        self.put_message(
                            message=mafia_pb2.ConnectionServerResponse(
                                type=mafia_pb2.ConnectionMessageType.INFO,
                                message=response
                            ), name=name, session=counter
                        )

                        self.put_message(
                            message=mafia_pb2.ConnectionServerResponse(
                                type=mafia_pb2.ConnectionMessageType.SESSION_NUMBER,
                                session_number=self.counter
                            ), name=name, session=counter
                        )

                        if length == 3:
                            self.counter = len(self.sessions.keys())
                            players = list(current_session.players.keys())
                            random.shuffle(players)
                            roles = ['mafia', 'sheriff', 'innocent', 'innocent']
                            for i in range(len(roles)):
                                current_session.players[players[i]].role = roles[i]
                                
                            self.put_message_to_everybody(
                            message=mafia_pb2.ConnectionServerResponse(
                                type=mafia_pb2.ConnectionMessageType.GAME_BEGINS,
                                message=f'4 players are connected! let the game begin...'
                            ), session=counter
                        )
                        break

            player = current_session.players[name]
            while True:
                try:
                    msg = player.message_queue.get_nowait()
                    if msg.type == mafia_pb2.ConnectionMessageType.GAME_BEGINS:
                        msg.message += f'\n\nyou role is... {player.role}!\n'
                        yield msg
                        return
                    yield msg
                except:
                    time.sleep(1)
            
    # def my_disconnect(self, name, session):
    #     print('DISCONNECT IN SERVER')
    #     if session == 100001234352467:
    #         session = self.counter
    #     current_session = self.sessions[session]
    #     if name in current_session.alive:
    #         current_session.players[name].alive = False
    #         current_session.alive.remove(name)
    #         del current_session.players[name]
            

    def day(self, message, context):
        name, session = message.name, int(message.session_number)
        
        player_alive = True

        current_session = self.sessions[session]
        
        player = current_session.players[name]

        print('got message from', name, session, message.command)
        player_command = message.command
        if player_command == mafia_pb2.DayClientCommand.INIT:
            message_text = '\nnew day started!\n' + 'alive players: ' + ', '.join(current_session.alive) + '\n'
            if player.alive:
                if player.role == 'sheriff' and current_session.mafia != '':
                    message_text += 'print \"reveal\" if you want to reveal mafia name\n'
                if not current_session.first_day:
                    message_text += 'print \"execute\" and player name if you want to execute him today\n'
                message_text += 'print \"end\" if you want to end current day\n'
                yield mafia_pb2.DayServerResponse(
                    type=mafia_pb2.DayMessageType.INFO_INPUT,
                    message=message_text
                )
            else:
                player_alive = False
                yield mafia_pb2.DayServerResponse(
                    type=mafia_pb2.DayMessageType.INFO_NO_INPUT,
                    message=message_text
                )

        elif player_command == mafia_pb2.DayClientCommand.REVEAL:
            print("REVEAL")
            if player.role == 'sheriff' and current_session.mafia != '':
                self.put_message_to_everybody(
                    message=mafia_pb2.DayServerResponse(
                        type=mafia_pb2.DayMessageType.INFO_INPUT,
                        message='sheriff wants to reveal mafia name...it\'s ' + current_session.mafia + '!'
                    ), session=session
                )
            else:
                self.put_message(
                    message=mafia_pb2.DayServerResponse(
                        type=mafia_pb2.DayMessageType.INFO_INPUT,
                        message=''
                    ), name=name, session=session
                )
        
        elif player_command == mafia_pb2.DayClientCommand.EXECUTE:
            print("EXECUTE")
            print(f'{name} wants to execute {message.additional}')
            print(f'alive: {" ".join(current_session.alive)}')
            if message.additional not in current_session.alive:
                print('name not in alive')
                self.put_message(
                    message=mafia_pb2.DayServerResponse(
                        type=mafia_pb2.DayMessageType.INFO_INPUT,
                        message='you\'ve entered invalid player name, try again please'
                    ), name=name, session=session
                )
            else:
                current_session.votes[name] = message.additional
                self.put_message_to_everybody(
                    message=mafia_pb2.DayServerResponse(
                        type=mafia_pb2.DayMessageType.INFO_INPUT,
                        message=name + ' voted for ' + message.additional
                    ), session=session
                )
                
        elif player_command == mafia_pb2.DayClientCommand.ENDING:
            print("ENDING")
            print('ending for', name)
            self.put_message_to_everybody(
                message=mafia_pb2.DayServerResponse(
                    type=mafia_pb2.DayMessageType.INFO_INPUT,
                    message=name + ' wants to end current day'
                ), session=session
            )
            print('after put message')
            current_session.want_to_end += 1
            print('alive:', len(current_session.alive))
            print('want to end:', current_session.want_to_end)
            if current_session.want_to_end == len(current_session.alive):
                message_text = 'another day ends'
                print(f'{name} ending the day')
                current_session.mafia = ''
                votes = dict.fromkeys(current_session.alive, 0)
                for vote in current_session.votes.values():
                    votes[vote] += 1
                dead_name, at_least = '', int(len(current_session.alive) / 2) + (len(current_session.alive) % 2 != 0)
                pizdets = False
                for n, v in votes.items():
                    if v >= at_least:
                        if dead_name != '':
                            pizdets = True
                        else:
                            dead_name = n
                if not pizdets and dead_name != '':
                    # self.put_message_to_everybody(
                    #     message=mafia_pb2.DayServerResponse(
                    #         type=mafia_pb2.DayMessageType.INFO_INPUT,
                    #         message=dead_name + ' was executed'
                    #     ), session=session)
                    message_text += f' and {dead_name} was executed\n'
                    current_session.alive.remove(dead_name)
                    current_session.players[dead_name].alive = False
                else:
                    # self.put_message_to_everybody(
                    #     message=mafia_pb2.DayServerResponse(
                    #         type=mafia_pb2.DayMessageType.INFO_INPUT,
                    #         message='nobody died today'
                    #     ), session=session
                    # )
                    message_text += f' and nobody died today\n'
                current_session.votes.clear()
                current_session.mafia = ''
                current_session.first_day = False
                current_session.want_to_end = 0
                
                state = self.check_game_ending(session)
                # мирные выиграли -- 0
                # мафия выиграла -- 1
                # продолжаем игру -- 2
                print(f'STATE {state}')
                if state == 0:
                    state = True
                    message_text += '\ngame ends. mafia lost this time'
                elif state == 1:
                    state = True
                    message_text += '\ngame ends. mafia won this time'
                else:
                    state = False
                
                self.put_message_to_everybody(
                    message=mafia_pb2.DayServerResponse(
                        type=mafia_pb2.DayMessageType.DAY_ENDS,
                        message=message_text,
                        ending=state
                    ), session=session
                )
                current_session.night = 0
            print('before while')
            player_alive = False
            print('end of ending for', name)  
        else:
            print('UNCATCHED CASE........................................................')
        # while len(player.message_queue) > 0:
        while True:
            print(f'in message queue for {name}')
            # print(player.message_queue[0].message)
            # yield player.message_queue[0]
            # player.message_queue.pop(0)
            try:
                yield player.message_queue.get_nowait()
            except:
                break
                
        
        if not player_alive:
            print('not alive')
            while True:
                try:
                    message = player.message_queue.get_nowait()
                    yield message
                    if message.type == mafia_pb2.DayMessageType.DAY_ENDS:
                        return
                except:
                    time.sleep(1)
                
                
                
    def night(self, message, context):
        name, session = message.name.strip(), int(message.session_number)
        print(f'MY NAME {name} IS IN PLAYERS {name in self.sessions[session].players.keys()}')
        
        current_session = self.sessions[session]
        player = current_session.players[name]
        
        player_alive = False

        print('got message from', name, session, message.command)
        player_command = message.command
        if player_command == mafia_pb2.NightClientCommand.INIT_NIGHT:
            message_type = mafia_pb2.NightMessageType.INFO_NO_INPUT_NIGHT
            message_text = '\nit’s nighttime. everyone is falling asleep\nalive players: ' + ', '.join(current_session.alive) + '\nmafia and sheriff wake up\n'
            if player.alive:
                if player.role == 'sheriff':
                    message_text += 'sheriff, you can now choose player to check...\n'
                    message_type = mafia_pb2.NightMessageType.INFO_INPUT_NIGHT
                    player_alive = True
                if player.role == 'mafia':
                    message_text += 'mafia, you can now choose your victim...\n'
                    message_type = mafia_pb2.NightMessageType.INFO_INPUT_NIGHT
                    player_alive = True
            yield mafia_pb2.NightServerResponse(
                type=message_type,
                message=message_text
            )


        elif player_command == mafia_pb2.NightClientCommand.PLAYING:
            player_alive = False 
            print(f'in playing for {name}')
            if message.additional not in current_session.alive:
                yield mafia_pb2.NightServerResponse(
                        type=mafia_pb2.NightMessageType.INFO_INPUT_NIGHT,
                        message='you have entered invalid name. try again, please'
                        )
                player_alive = True
                        
            if player.role == 'sheriff':
                if current_session.players[message.additional].role == 'mafia':
                    current_session.mafia = message.additional
                    current_session.message_night += 'sheriff chose the right player to check'
                else:
                    current_session.message_night += 'sheriff chose the wrong player to check'
                self.put_message_to_everybody(
                    message=mafia_pb2.NightServerResponse(
                        type=mafia_pb2.NightMessageType.INFO_NO_INPUT_NIGHT,
                        message='sheriff made his choice'
                    ), session=session
                )
                
            elif player.role == 'mafia':
                self.put_message_to_everybody(
                    message=mafia_pb2.NightServerResponse(
                        type=mafia_pb2.NightMessageType.INFO_NO_INPUT_NIGHT,
                        message='mafia made his choice'
                    ), session=session
                )
                current_session.dead = message.additional
                flag = 1
                for pl in current_session.alive:
                    if current_session.players[pl].role == 'sheriff':
                        flag -= 1
                current_session.night += flag
                
            current_session.night += 1
            
            if current_session.night == 2:
                current_session.players[current_session.dead].alive = False
                current_session.alive.remove(current_session.dead)
                if current_session.message_night != '':
                    current_session.message_night += ' and '
                current_session.message_night += f'mafia killed {current_session.dead}'
                
                current_session.message_night += '\n'
                
                state = self.check_game_ending(session)
                # мирные выиграли -- 0
                # мафия выиграла -- 1
                # продолжаем игру -- 2
                if state == 0:
                    state = True
                    current_session.message_night += '\ngame ends. mafia lost this time'
                elif state == 1:
                    state = True
                    current_session.message_night += '\ngame ends. mafia won this time'
                else:
                    state = False

                self.put_message_to_everybody(
                    message=mafia_pb2.NightServerResponse(
                        type=mafia_pb2.NightMessageType.NIGHT_ENDS,
                        message='night ends. today ' + current_session.message_night,
                        ending=state
                    ), session=session
                )
                current_session.message_night = ''
                current_session.night = 3
                current_session.dead = ''
        
        print(f'alive is {player_alive} for {name}')
        while not player_alive:
            try:
                msg = self.sessions[session].players[name].message_queue.get_nowait()
                yield msg
                if msg.type == mafia_pb2.NightMessageType.NIGHT_ENDS:
                    print(f'ending message queue for {name}')
                    return
            except:
                continue
        
    def check_game_ending(self, session):
        current_session = self.sessions[session]
        mafia, not_mafia = 0, 0
        for player in current_session.alive:
            if current_session.players[player].role == 'mafia':
                mafia += 1
            else:
                not_mafia += 1
                
        if mafia == 0:
            # мирные выиграли
            return 0
        if mafia >= not_mafia:
            # мафия выиграла
            return 1
        # продолжаем игру
        return 2
    
    def disconnect(self, message, context):
        name, session = message.name.strip(), int(message.session)
        print('DISCONNECT IN SERVER', name, session)
        if session == 100001234352467:
            session = self.counter
        current_session = self.sessions[session]
        if name in current_session.alive:
            current_session.players[name].alive = False
            current_session.alive.remove(name)
            del current_session.players[name]
        return mafia_pb2.google_dot_protobuf_dot_empty__pb2.Empty()



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mafia_pb2_grpc.add_MafiaServicer_to_server(MafiaService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()


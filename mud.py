# -*- coding: utf-8 -*-
from user import User
from user import UserDB
from room import Room
from room import RoomDB
from server import WebSocketServer
from message import Message
from handler import UserHandlers
from handler import LoginHandler

class MudService(object):
  DEFAULT_PROMPT = Message('> ', 'white')
  def __init__(self):
    RoomDB.add(Room(0))

  def enter(self, socket):
    new_user = User(socket, self.DEFAULT_PROMPT)
    self._send_title(new_user)
    UserDB.add(socket, new_user)
    UserHandlers.set_handler(new_user, LoginHandler(new_user))
    UserDB.flush_send_buffer()

  def _send_title(self, user):
    message = Message('\n')
    message.add('  ****************************** \n', 'yellow')
    message.add(' *                              * \n', 'yellow')
    message.add('*  Welcome to the Fantasy World  *\n', 'yellow')
    message.add(' *                              * \n', 'yellow')
    message.add('  ****************************** \n\n\n', 'yellow')
    user.send(message);

  def leave(self, socket):
    user = UserDB.find_by_socket(socket)
    UserHandlers.leave(user)
    UserHandlers.delete(user)
    UserDB.remove_by_socket(socket)
    UserDB.flush_send_buffer()

  def receve(self, socket, data):
    user = UserDB.find_by_socket(socket)
    if data: UserHandlers.handle(user, data)
    else   : user.send(Message(''))
    UserDB.flush_send_buffer()

if __name__ == '__main__':
  WebSocketServer(MudService()).run(7001)

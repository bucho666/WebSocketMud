# -*- coding: utf-8 -*-
from avatar import Avatar
from avatar import AvatarDB
from room import Room
from room import RoomDB
from server import WebSocketServer
from message import Message
from handler import AvatarHandlers
from handler import LoginHandler

class MudService(object):
  DEFAULT_PROMPT = Message('> ', 'white')
  def __init__(self):
    Room('村の広場', 0).connect(Room('洞窟の入り口', 1), '東')

  def enter(self, socket):
    new_avatar = Avatar(socket, self.DEFAULT_PROMPT)
    self._send_title(new_avatar)
    AvatarDB.add(socket, new_avatar)
    AvatarHandlers.set_handler(new_avatar, LoginHandler(new_avatar))
    AvatarDB.flush_send_buffer()

  def _send_title(self, avatar):
    message = Message('\n')
    message.add('  ****************************** \n', 'yellow')
    message.add(' *                              * \n', 'yellow')
    message.add('*  Welcome to the Fantasy World  *\n', 'yellow')
    message.add(' *                              * \n', 'yellow')
    message.add('  ****************************** \n\n\n', 'yellow')
    avatar.send(message);

  def leave(self, socket):
    avatar = AvatarDB.find_by_socket(socket)
    AvatarHandlers.leave(avatar)
    AvatarHandlers.delete(avatar)
    AvatarDB.remove_by_socket(socket)
    AvatarDB.flush_send_buffer()

  def receve(self, socket, data):
    avatar = AvatarDB.find_by_socket(socket)
    if data: AvatarHandlers.handle(avatar, data)
    else   : avatar.send(Message(''))
    AvatarDB.flush_send_buffer()

if __name__ == '__main__':
  WebSocketServer(MudService()).run(7001)

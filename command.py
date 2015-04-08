# -*- coding: utf-8 -*-
import re
from room import RoomDB
from message import Message
from room import Direction

class AvatarCommand(object):
  def __init__(self, avatar):
    self._avatar = avatar
    self._in_room = None

  def __call__(self, command=''):
    self._update_in_room()
    self._action(command)

  def _action(self, command):
    pass

  def _update_in_room(self):
    self._in_room = RoomDB.find_by_avatar(self._avatar)

  def match(self, command):
    return False

class SayCommand(AvatarCommand):
  def __init__(self, avatar):
    AvatarCommand.__init__(self, avatar)

  def _action(self, command):
    if not command: return
    self._in_room.send_all(Message(self._avatar.name(), 'white').add(': ').add(command).add('\n'))

class MoveCommand(AvatarCommand):
  _command_re = re.compile('(.+)(に|へ)移動')

  def __init__(self, avatar):
    AvatarCommand.__init__(self, avatar)

  def _action(self, command):
    match = self._command_re.match(command)
    if not match:
      self._avatar.send(Message('?', 'maroon'))
      return
    direction = match.group(1)
    if not Direction.name_is(direction):
      self._avatar.send(Message('方向を指定してください。\n', 'maroon'))
      return
    if not self._in_room.exists_exit(direction):
      self._avatar.send(Message('そっちに道はない。\n', 'maroon'))
      return
    self._in_room.move_avatar(self._avatar, direction)
    LookCommand(self._avatar)()

  def match(cls, command):
    return cls._command_re.match(command)

class LookCommand(AvatarCommand):
  def __init__(self, avatar):
    AvatarCommand.__init__(self, avatar)

  def _action(self, command):
    message = Message('[%s]\n' % self._in_room.name(), 'white');
    other_character_list = self._other_character_list()
    if other_character_list:
      message += self._character_list_message(other_character_list)
    exits = self._in_room.exits()
    if exits:
      message += self._exits_message(exits)
    self._avatar.send(message)

  def _other_character_list(self):
    return [avatar for avatar in self._in_room.avatars() if avatar != self._avatar]

  def _character_list_message(self, character_list):
    message = Message("ここには、\n", 'olive')
    for num, avatar in enumerate(character_list):
      message.add(avatar.name().ljust(8), 'olive')
      if num % 4 == 3:
        message.add('\n')
    message.add('がいる。\n', 'olive')
    return message

  def _exits_message(self, exits):
    message = Message('[出口]\n')
    for direction, room_name in exits:
      message.add('  %s: %s\n' % (direction, room_name))
    return message

  def match(cls, command):
    return command == '見る'

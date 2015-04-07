# -*- coding: utf-8 -*-
import re
from avatar import AvatarDB
from avatar import AvatarName
from room import RoomDB
from message import Message

class LoginHandler(object):
  INVALID_NAME_CHARACTER = u' 　!"#$%&\'()-=^~\\|@`[{;+:*]},<.>/?_'
  NAME_MAX_LENGTH = 16

  def __init__(self, avatar):
    self._avatar = avatar

  def enter(self):
    self._avatar.send(Message('\n名前を入力してください。\n', 'white'));

  def handle(self, message):
    name = message
    if not self._check_name(name):
      self.enter()
      return
    self._avatar.rename(name)
    AvatarHandlers.set_handler(self._avatar, ConfirmHandler(self._avatar))

  def leave(self):
    pass

  def _check_name(self, name):
    avatar_name = AvatarName(name)
    if avatar_name.using_invalid_character():
      self._avatar.send(Message('名前に記号や空白は使用できません。\n', 'maroon'))
      return False
    if avatar_name.is_too_long():
      self._avatar.send(Message('%d文字(byte)以上の名前は使用できません。\n' % avatar_name.max_length(), 'maroon'))
      return False
    if AvatarDB.find_by_name(name):
      self._avatar.send(Message('既にその名前は使用されています。\n', 'maroon'))
      return False
    return True

class ConfirmHandler(object):
  def __init__(self, avatar):
    self._avatar = avatar

  def enter(self):
    message = Message('\n名前は "%s" でよろしいですか？' % (self._avatar.name()), 'white').add('(はい/いいえ)\n', 'yellow');
    self._avatar.send(message)

  def leave(self):
    pass

  def handle(self, message):
    if message == 'はい':
      AvatarHandlers.set_handler(self._avatar, MudHandler(self._avatar))
      return
    if message == 'いいえ':
      self._avatar.rename('')
      AvatarHandlers.set_handler(self._avatar, LoginHandler(self._avatar))
      return
    self.enter()

class MudHandler(object):
  def __init__(self, avatar):
    self._avatar = avatar
    self._in_room = RoomDB.find_by_id(0)
    self._commands = (
        MoveCommand(self._avatar),
        LookCommand(self._avatar),
        )
  def enter(self):
    self._in_room.send_all(Message(self._avatar.name(), 'yellow').add(' が入室しました。\n', 'olive'))
    self._in_room.add_avatar(self._avatar)
    LookCommand(self._avatar)()

  def leave(self):
    self._update_in_room()
    self._in_room.send_all(Message(self._avatar.name(), 'yellow').add(' が退室しました。\n', 'olive'))
    self._in_room.remove_avatar(self._avatar)

  def handle(self, message):
    for command in self._commands:
      if command.match(message):
        command(message)
        return
    SayCommand(self._avatar)(message)

  def _update_in_room(self):
    self._in_room = RoomDB.find_by_avatar(self._avatar)

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
  directions = ('東','西','南','北')
  _command_re = re.compile('(.+)(に|へ)移動')

  def __init__(self, avatar):
    AvatarCommand.__init__(self, avatar)

  def _action(self, command):
    match = self._command_re.match(command)
    if not match:
      self._avatar.send(Message('?', 'maroon'))
      return
    direction = match.group(1)
    if direction not in self.directions:
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

  def match(cls, command):
    return command == '見る'

class AvatarHandlers(object):
  _handler = dict()

  @classmethod
  def set_handler(cls, avatar, handler):
    cls._handler[avatar] = handler
    cls._handler[avatar].enter()

  @classmethod
  def delete(cls, avatar):
    del cls._handler[avatar]

  @classmethod
  def leave(cls, avatar):
    cls._handler[avatar].leave()

  @classmethod
  def handle(cls, avatar, data):
    cls._handler[avatar].handle(data)

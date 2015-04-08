# -*- coding: utf-8 -*-
from avatar import AvatarDB
from avatar import AvatarName
from room import RoomDB
from message import Message
from command import SayCommand
from command import MoveCommand
from command import LookCommand

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

# -*- coding: utf-8 -*-
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
    AvatarHandlers.set_handler(self._avatar, ChoiceColorHandler(self._avatar))

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

class ChoiceColorHandler(object):
  _colors = (
      'red', 'maroon',
      'yellow', 'olive',
      'lime', 'green',
      'aqua', 'teal',
      'blue', 'navy',
      'fuchsia', 'purple')

  def __init__(self, avatar):
    self._avatar = avatar

  def enter(self):
    self._avatar.send(Message("\n名前の色を選択してください。\n", 'white'));
    for num, color in enumerate(self._colors):
      color_tag = '%s ' % color
      self._avatar.send(Message(color_tag.ljust(8), color))
      if num % 4 == 3:
          self._avatar.send(Message('\n'))

  def leave(self):
    pass

  def handle(self, message):
    choose_color = message.lower()
    if not choose_color in self._colors:
      self._avatar.send(Message('リストの中の色を入力してください。\n', 'maroon'))
      self.enter()
      return
    self._avatar.change_name_color(choose_color)
    AvatarHandlers.set_handler(self._avatar, ConfirmHandler(self._avatar))

class ConfirmHandler(object):
  def __init__(self, avatar):
    self._avatar = avatar

  def enter(self):
    message = Message('\nこの名前と色でよろしいですか？', 'white').add('(yes/no)\n', 'yellow');
    message.add('%s\n' % self._avatar.name(), self._avatar.name_color()).add('\n')
    self._avatar.send(message)

  def leave(self):
    pass

  def handle(self, message):
    if message == 'yes':
      AvatarHandlers.set_handler(self._avatar, MudHandler(self._avatar))
      return
    if message == 'no':
      self._avatar.rename('')
      AvatarHandlers.set_handler(self._avatar, LoginHandler(self._avatar))
      return
    self.enter()

class MudHandler(object):
  def __init__(self, avatar):
    self._avatar = avatar
    self._in_room = RoomDB.find_by_id(0)

  def enter(self):
    self._in_room.add_avatar(self._avatar)
    self._avatar.send(Message('[%s]\n' % self._in_room.name(), 'white'))
    self._in_room.send_all(Message(self._avatar.name(), self._avatar.name_color()).add(' が入室しました。\n', 'olive'))

  def leave(self):
    self._update_in_room()
    self._in_room.send_all(Message(self._avatar.name(), self._avatar.name_color()).add(' が退室しました。\n', 'olive'))
    self._in_room.remove_avatar(self._avatar)

  def handle(self, message):
    self._update_in_room()
    if message == 'who':
      self._send_avatar_list()
    elif message == '移動':
      self._in_room.remove_avatar(self._avatar)
      next_room = self._in_room.next_room('東')
      next_room.add_avatar(self._avatar)
      self._update_in_room()
      self._avatar.send(Message('[%s]\n' % self._in_room.name(), 'white'))
    else:
      self._in_room.send_all(Message(self._avatar.name(), self._avatar.name_color()).add(': ').add(message).add('\n'))

  def _send_avatar_list(self):
    self._update_in_room()
    message = Message("avatar list:\n", 'white')
    for num, avatar in enumerate(self._in_room.avatars()):
      message.add(avatar.name().ljust(8), avatar.name_color())
      if num % 4 == 3:
        message.add('\n')
    message.add('\n')
    self._avatar.send(message)

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

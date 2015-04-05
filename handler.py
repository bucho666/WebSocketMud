# -*- coding: utf-8 -*-
from user import UserDB
from user import UserName
from room import RoomDB
from message import Message

class LoginHandler(object):
  INVALID_NAME_CHARACTER = u' 　!"#$%&\'()-=^~\\|@`[{;+:*]},<.>/?_'
  NAME_MAX_LENGTH = 16

  def __init__(self, user):
    self._user = user

  def enter(self):
    self._user.send(Message('\n名前を入力してください。\n', 'white'));

  def handle(self, message):
    name = message
    if not self._check_name(name):
      self.enter()
      return
    self._user.rename(name)
    UserHandlers.set_handler(self._user, ChoiceColorHandler(self._user))

  def leave(self):
    pass

  def _check_name(self, name):
    user_name = UserName(name)
    if user_name.using_invalid_character():
      self._user.send(Message('名前に記号や空白は使用できません。\n', 'maroon'))
      return False
    if user_name.is_too_long():
      self._user.send(Message('%d文字(byte)以上の名前は使用できません。\n' % user_name.max_length(), 'maroon'))
      return False
    if UserDB.find_by_name(name):
      self._user.send(Message('既にその名前は使用されています。\n', 'maroon'))
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

  def __init__(self, user):
    self._user = user

  def enter(self):
    self._user.send(Message("\n名前の色を選択してください。\n", 'white'));
    for num, color in enumerate(self._colors):
      color_tag = '%s ' % color
      self._user.send(Message(color_tag.ljust(8), color))
      if num % 4 == 3:
          self._user.send(Message('\n'))

  def leave(self):
    pass

  def handle(self, message):
    choose_color = message.lower()
    if not choose_color in self._colors:
      self._user.send(Message('リストの中の色を入力してください。\n', 'maroon'))
      self.enter()
      return
    self._user.change_name_color(choose_color)
    UserHandlers.set_handler(self._user, ConfirmHandler(self._user))

class ConfirmHandler(object):
  def __init__(self, user):
    self._user = user

  def enter(self):
    message = Message('\nこの名前と色でよろしいですか？', 'white').add('(yes/no)\n', 'yellow');
    message.add('%s\n' % self._user.name(), self._user.name_color()).add('\n')
    self._user.send(message)

  def leave(self):
    pass

  def handle(self, message):
    if message == 'yes':
      UserHandlers.set_handler(self._user, ChatHandler(self._user))
      return
    if message == 'no':
      self._user.rename('')
      UserHandlers.set_handler(self._user, LoginHandler(self._user))
      return
    self.enter()

class ChatHandler(object):
  def __init__(self, user):
    self._user = user
    self._start_room = RoomDB.find_by_id(0)

  def enter(self):
    self._start_room.add_user(self._user)
    in_room = RoomDB.find_by_user(self._user)
    self._user.send(Message('[%s]\n' % in_room.name(), 'white'))
    self._send_all(Message(self._user.name(), self._user.name_color()).add(' が入室しました。', 'olive'))

  def leave(self):
    in_room = RoomDB.find_by_user(self._user)
    self._send_all(Message(self._user.name(), self._user.name_color()).add(' が退室しました。', 'olive'))
    in_room.remove_user(self._user)

  def handle(self, message):
    if message == 'who':
      self._send_user_list()
    else:
      self._send_all(Message(self._user.name(), self._user.name_color()).add(': ').add(message)) 

  def _send_user_list(self):
    in_room = RoomDB.find_by_user(self._user)
    message = Message("user list:\n", 'white')
    for num, user in enumerate(in_room.users()):
      message.add(user.name().ljust(8), user.name_color())
      if num % 4 == 3:
        message.add('\n')
    message.add('\n')
    self._user.send(message)

  def _send_all(self, message):
    in_room = RoomDB.find_by_user(self._user)
    message.add('\n')
    in_room.send_all(message)

class UserHandlers(object):
  _handler = dict()

  @classmethod
  def set_handler(cls, user, handler):
    cls._handler[user] = handler
    cls._handler[user].enter()

  @classmethod
  def delete(cls, user):
    del cls._handler[user]

  @classmethod
  def leave(cls, user):
    cls._handler[user].leave()

  @classmethod
  def handle(cls, user, data):
    cls._handler[user].handle(data)

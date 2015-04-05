# -*- coding: utf-8 -*-

class RoomDB(object):
  _rooms = dict()

  @classmethod
  def clear(cls):
    cls._rooms = dict()

  @classmethod
  def add(cls, room):
    cls._rooms[room.object_id()] = room

  @classmethod
  def find_by_id(cls, room_id):
    return cls._rooms[room_id]

  @classmethod
  def find_by_avatar(cls, avatar):
    for room in cls._rooms.values():
      if room.in_avatar(avatar): return room
    return None

class Room(object):
  def __init__(self, name, object_id):
    self._object_id = object_id
    self._name = name
    self._avatars = []
    self._exit = dict()
    RoomDB.add(self)

  def connect(self, room, direction):
    self._exit[direction] = room.object_id()

  def next_room(self, direction):
    return RoomDB.find_by_id(self._exit[direction])

  def exists_exit(self, direction):
    return direction in self._exit

  def name(self):
    return self._name

  def object_id(self):
    return self._object_id

  def add_avatar(self, avatar):
    self._avatars.append(avatar)

  def remove_avatar(self, avatar):
    self._avatars.remove(avatar)

  def send_all(self, message):
    for avatar in self._avatars:
      avatar.send(message)

  def avatars(self):
    return list(self._avatars)

  def in_avatar(self, avatar):
    return avatar in self._avatars

  def move_avatar(self, avatar, direction):
    self.remove_avatar(avatar)
    self.next_room(direction).add_avatar(avatar)

if __name__ == '__main__':
  import unittest

  class RoomDBTest(unittest.TestCase):
    def setUp(self):
      RoomDB.clear()
      self._room_a = Room('test room A', 0)
      self._avatar_a = object()
      self._room_a.add_avatar(self._avatar_a)
      self._room_b = Room('test room B', 1)
      self._avatar_b = object()
      self._room_b.add_avatar(self._avatar_b)

    def testFindByAvatar(self):
      self.assertEqual(RoomDB.find_by_avatar(self._avatar_a), self._room_a)
      self.assertEqual(RoomDB.find_by_avatar(self._avatar_b), self._room_b)

    def testFindByAvatarNotExists(self):
      self.assertEqual(RoomDB.find_by_avatar(object()), None)

  class RoomTest(unittest.TestCase):
    def setUp(self):
      RoomDB.clear()
      self._room_a = Room('test room A', 0)
      self._room_b = Room('test room A', 1)
      self._direction = 'north'
      self._avatar = object()
      self._room_a.connect(self._room_b, self._direction)
      self._room_a.add_avatar(self._avatar)

    def testConnectRoom(self):
      self.assertEqual(self._room_a.next_room(self._direction), self._room_b)

    def testExistsExit(self):
      self.assertTrue(self._room_a.exists_exit(self._direction))

    def testNoExistsExit(self):
      self.assertFalse(self._room_a.exists_exit('south'))

    def testInAvatar(self):
      self.assertTrue(self._room_a.in_avatar(self._avatar))

    def testNotInAvatar(self):
      self.assertFalse(self._room_b.in_avatar(self._avatar))
      self.assertFalse(self._room_a.in_avatar(object()))

    def testMoveAvatar(self):
      self._room_a.move_avatar(self._avatar, self._direction)
      self.assertFalse(self._room_a.in_avatar(self._avatar))
      self.assertTrue(self._room_b.in_avatar(self._avatar))

  unittest.main()

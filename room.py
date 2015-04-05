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

class Room(object):
  def __init__(self, name, object_id):
    self._object_id = object_id
    self._name = name
    self._users = []
    self._exits = dict()
    RoomDB.add(self)

  def connect(self, room, direction):
    self._exits[direction] = room.object_id()

  def next_room(self, direction):
    return RoomDB.find_by_id(self._exits[direction])

  def exists_exit(self, direction):
    return direction in self._exits

  def name(self):
    return self._name

  def object_id(self):
    return self._object_id

  def add_user(self, user):
    self._users.append(user)

  def remove_user(self, user):
    self._users.remove(user)

  def send_all(self, message):
    for user in self._users:
      user.send(message)

  def users(self):
    return list(self._users)

  def in_user(self, user):
    return user in self._users

if __name__ == '__main__':
  import unittest

  class RoomTest(unittest.TestCase):
    def setUp(self):
      RoomDB.clear()
      self._room_a = Room('test room A', 0)
      self._room_b = Room('test room A', 1)
      self._direction = 'north'
      self._user = object()
      self._room_a.connect(self._room_b, self._direction)
      self._room_a.add_user(self._user)

    def testConnectRoom(self):
      self.assertEqual(self._room_a.next_room(self._direction), self._room_b)

    def testExistsExit(self):
      self.assertTrue(self._room_a.exists_exit(self._direction))

    def testNoExistsExit(self):
      self.assertFalse(self._room_a.exists_exit('south'))

    def testInUser(self):
      self.assertTrue(self._room_a.in_user(self._user))

    def testNotInUser(self):
      self.assertFalse(self._room_b.in_user(self._user))
      self.assertFalse(self._room_a.in_user(object()))

  unittest.main()


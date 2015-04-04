# -*- coding: utf-8 -*-

class Message(object):
  def __init__(self, message, color='Silver'):
    self._messages = [(message, color)]

  def add(self, message, color='Silver'):
    self._messages.append((message, color))
    return self

  def __str__(self):
    string = ''.join(['<font color=%s>%s</font>' % (color, message.replace(' ', '&nbsp;'))\
        for (message, color) in self._messages])
    return string.replace('\n', '<br>')

from abc import ABC, abstractmethod

class Campo():
  def __init__(self, value):
    self._value = value

#  @abstractmethod
  def toValue(self):
    pass



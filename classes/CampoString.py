from Campo import Campo

class CampoString(Campo):
  def toValue(self):
    return self.value() # Stripping

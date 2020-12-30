import re
from classes.Campo import Campo


class CampoRegex(Campo):
    def __init__(self, value, pattern, groupNumber=0):
        super().__init__(value)
        self.pattern = pattern
        self.groupNumber = groupNumber
    
    def toValue(self):
        return self.search()

    def search(self):
        result = re.search(self.pattern, self._value)
        return result.groups()[self.groupNumber] if result is not None else None
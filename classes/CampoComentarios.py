import re
from classes.Campo import Campo


class CampoComentarios(Campo):
    def __init__(self, value, contentIsHTML=True):
        super().__init__(value)
        self.contentIsHTML = contentIsHTML

    def toValue(self):
        if self.contentIsHTML:
            return self.parseFromHTML()

    def parseFromHTML(self):
        placeholders = {
            "opinion": "Opinion:",
            "img_opinion": '<img width=16 height=16 src="/cece2013/img/sistema/usuario-1.png"/>',
        }
        splitted = re.split(placeholders['opinion'], self._value)
        comentarios = [match[1].strip() for match in re.findall(
            "(<img.+?\/>:)(.+?)(?=<)", splitted[1])]
        return comentarios

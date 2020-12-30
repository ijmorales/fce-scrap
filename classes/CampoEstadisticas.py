from classes.Campo import Campo
from bs4 import BeautifulSoup

class CampoEstadisticas(Campo):
    def __init__(self, value, contentIsHTML=True):
        super().__init__(value)
        self.contentIsHTML = contentIsHTML

    def toValue(self):
        if self.contentIsHTML:
            return self.parseFromHTML()

    def parseFromHTML(self):
        stats_row = BeautifulSoup(self._value, 'lxml').find_all('tr')
        estadisticas = []
        for row in stats_row:
            stats = row.find_all('td')
            if stats:
                estadisticas.append({
                    "anio": int(stats[0].string.strip()),
                    "cuatrimestre": int(stats[1].string.strip()),
                    "inscriptos": int(stats[2].b.string),
                    "ausentes": int(stats[3].b.string),
                    "aprobados": int(stats[4].b.string),
                    "regularizados": int(stats[5].b.string),
                    "reprobados": int(stats[6].b.string),
                })
        return estadisticas




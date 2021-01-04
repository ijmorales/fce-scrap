import regex as re
from classes.Campo import Campo


class CampoComentarios(Campo):
    def __init__(self, value, contentIsHTML=True):
        super().__init__(value)
        self.contentIsHTML = contentIsHTML

    def toValue(self):
        if self.contentIsHTML:
            return self.parseFromHTML()

    def parseFromHTML(self):
        patterns = {
            "opinion": "Opinion:",
            "year": "<br>(\d{4})<br>"
        }
        years = [match for match in re.findall(patterns['year'], self._value)]
        comentarios_by_year = re.split(patterns['year'], self._value)
        comentarios = {}

        for year in years:
            year_idx = comentarios_by_year.index(year)
            comentarios[year] = [match.strip() for match in re.findall("(?<=<img.+?\/>:)[^<]+", comentarios_by_year[year_idx + 1])]

        return comentarios


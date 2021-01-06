from classes.Campo import Campo
from bs4 import BeautifulSoup
from helpers import get_dia_completo
import re


class CampoHorario(Campo):
    def __init__(self, horas, dias, sabado):
        self.dias = dias
        self.horas = horas
        self.sabado = sabado

    def toValue(self):
        dias = [get_dia_completo(abv) for abv in re.split(r"\\", self.dias)]
        self.horas = re.search(
            r"(\d{2}:\d{2}-\d{2}:\d{2})", self.horas).groups()[0]
        horario = [{'dia': dia, 'hora': self.horas}
                   for dia in dias if dia != None]
        if self.sabado:
            horario.append({'dia': 'sábado', 'hora': self.sabado})

        return horario

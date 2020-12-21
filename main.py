import requests
import configparser
import json
import uuid
import re
from bs4 import BeautifulSoup

class CECE:
    def __init__(self, conf):
        self.url = conf['BaseURL']
        self.auth_url = conf['AuthURL']
        self.curso_detalle_url = conf['DetalleCursoURL']
        self.cursos_url = conf['CursosURL']
        self.user = conf['Username']
        self.pw = conf['Password']

    def auth(self):
        try:
            self.session = requests.Session()
            self.session.post(self.url, data={"usuario2": self.user, "clave2": self.pw})
            self.session.post(self.auth_url)
        except Exception as e:
            print(e)
    
    def get_cursos(self):
        res = self.session.get(self.cursos_url)
        oferta = json.loads(res.text)
        for curso in oferta:
            curso['detalle'] = self.get_detalle(curso['id'])

        with open(f"files/{uuid.uuid1()}.json", "w", encoding='utf-8') as f:
            json.dump(oferta, f, ensure_ascii=False)

    def get_detalle(self, curso_id):
        res = self.session.post(self.curso_detalle_url, data={
            "id_nro": curso_id
        })
        detalle = CECE.limpiar_detalle(res.content.decode('utf-8'))
        return detalle
    
    def limpiar_detalle(content):
        placeholders = {
            "corte": "Corte de Rank. y Reg. 2020:",
            "estadisticas": "Estadisticas:",
            "puntaje": "Puntaje:",
            "opinion": "Opinion:",
            "img_opinion": '<img width=16 height=16 src="/cece2013/img/sistema/usuario-1.png"/>',
        }
        max_usuario = 7

        splitted = re.split(placeholders['opinion'], content)
        datos = splitted[0]
        matches = re.findall("(<img.+?\/>:)(.+?)(?=<)", splitted[1])
        comentarios = [match[1].strip() for match in re.findall("(<img.+?\/>:)(.+?)(?=<)", splitted[1])]

        stats = BeautifulSoup(datos, 'lxml').find_all('td')
        estadisticas = {
            "anio": int(stats[0].string.strip()),
            "cuatrimestre": int(stats[1].string.strip()),
            "inscriptos": int(stats[2].b.string),
            "ausentes": int(stats[3].b.string),
            "aprobados": int(stats[4].b.string),
            "regularizados": int(stats[5].b.string),
            "reprobados": int(stats[6].b.string)
        } if stats else None

        detalle = {
            "comentarios": comentarios,
            "estadisticas": estadisticas
        }

        return detalle


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    cece = CECE(config['DEFAULT'])
    cece.auth()
    cursos = cece.get_cursos()

if __name__ == "__main__":
    main()
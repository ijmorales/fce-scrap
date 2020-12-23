import requests
import configparser
import json
import uuid
import re
import logging
from bs4 import BeautifulSoup
from requests.sessions import default_headers


class CECE:
    def __init__(self, conf, logger):
        self.url = conf['BaseURL']
        self.login = conf['LoginURL']
        self.auth_url = conf['AuthURL']
        self.curso_detalle_url = conf['DetalleCursoURL']
        self.cursos_url = conf['CursosURL']
        self.user = conf['Username']
        self.pw = conf['Password']
        self.logger = logger

        self.logger.info(f"{'*'*50}")
        self.logger.info(f"Inicializando script")

    def auth(self):
        try:
            self.session = requests.Session()
            self.session.headers = {
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Accept': '*/*',
                'Host': 'www.cece.org'
            }

            # Abrir la conexion y obtener la cookie inicial
            self.logger.info("Obteniendo PHPSESSID")
            self.session.get(self.login)
            # Autenticacion
            self.logger.info("Autenticando PHPSESSID")
            self.session.post(self.auth_url, data={
                              "usuario2": self.user, "clave2": self.pw})
        except Exception as e:
            self.logger.error(e)

    def get_cursos(self):
        self.logger.info("Trayendo cursos")
        res = self.session.get(self.cursos_url, headers={
                               'Content-Type': 'application/json'})
        oferta = json.loads(res.text)

        self.logger.info(
            f"{round(len(res.content)/1024, 2)}KB fetcheados de {self.cursos_url}")
        self.logger.info("Trayendo detalles")

        for curso in oferta:
            curso['detalle'] = self.get_detalle(curso['id'])

        with open(f"files/{uuid.uuid1()}.json", "w", encoding='utf-8') as f:
            self.logger.info(f"Guardando oferta en '{f.name}'")
            json.dump(oferta, f, ensure_ascii=False, sort_keys=True, indent=2)

    def get_detalle(self, curso_id):
        res = self.session.post(self.curso_detalle_url,
                                data={'id_nro': curso_id})
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
        comentarios = [match[1].strip() for match in re.findall(
            "(<img.+?\/>:)(.+?)(?=<)", splitted[1])]

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
    logging.basicConfig(filename="cece.log",
                        encoding='utf-8',
                        format='%(asctime)s: %(levelname)s - %(message)s',
                        level=logging.INFO
                        )
    appLogger = logging.getLogger("FetchCECE")
    cece = CECE(config['DEFAULT'], logger=appLogger)
    cece.auth()
    cursos = cece.get_cursos()


if __name__ == "__main__":
    main()

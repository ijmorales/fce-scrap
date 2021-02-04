import requests
import configparser
import json
import uuid
import re
import logging
import os
import helpers
from bs4 import BeautifulSoup
from requests.sessions import default_headers
from classes.CampoEstadisticas import CampoEstadisticas
from classes.CampoComentarios import CampoComentarios
from classes.CampoRegex import CampoRegex
from classes.CampoHorario import CampoHorario


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
            try:
                curso['horario'] = CampoHorario(
                    curso['horario'], curso['dias'], curso['sabado']).toValue() if curso['horario'] else None
                helpers.strip_strings(curso)
                curso['id'] = int(curso['id'])
                curso['detalle'] = self.get_detalle(curso['id'])
                curso['docente'] = curso['docente'] if curso['docente'] != "" else None
            except Exception as e:
                self.logger.error(e)

        return oferta

    def get_detalle(self, curso_id):
        res = self.session.post(self.curso_detalle_url,
                                data={'id_nro': curso_id})
        detalle = CECE.limpiar_detalle(res.content.decode('utf-8'))
        return detalle

    def limpiar_detalle(content):
        placeholders = {
            "corte": "Corte.+?(?:<\/b>)(.+?(?=\\n))",
            "estadisticas": "Estadisticas:",
            "puntaje": "Puntaje:",
        }

        puntaje = CampoRegex(
            value=content, pattern='(Puntaje:)(.+?(?:\\n))(\d+?\.\d)', groupNumber=2).toValue()
        estadisticas = CampoEstadisticas(content).toValue()
        comentarios = CampoComentarios(content).toValue()
        corte = CampoRegex(
            value=content, pattern='(Min\. Ranking:)(.+?(?:<b>))(\w{3})', groupNumber=2).toValue()
        maxRegistro = CampoRegex(
            value=content, pattern='(Max\. Registro:)(.+?(?:<b>))(\w{6})', groupNumber=2).toValue()

        detalle = {
            "comentarios": comentarios,
            "estadisticas": estadisticas if len(estadisticas) > 0 else None,
            "corte": int(corte) if corte is not None else None,
            "maxRegistro": int(maxRegistro) if maxRegistro is not None else None,
            "porcentajeAprobados": CECE.calcular_porcentaje_aprobados(estadisticas),
            "puntaje": float(puntaje) if puntaje else None
        }

        return detalle

    def calcular_porcentaje_aprobados(estadisticas):
        aprobados = 0
        inscriptos = 0
        for estadistica in estadisticas:
            aprobados += estadistica['aprobados']
            inscriptos += estadistica['inscriptos']
        if aprobados == 0:
            return None
        elif inscriptos == 0:
            return None
        return round(aprobados / inscriptos, 2)


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    logging.basicConfig(filename="cece.log",
                        format='%(asctime)s: %(levelname)s - %(message)s',
                        level=logging.INFO,
                        filemode="w"
                        )
    appLogger = logging.getLogger("FetchCECE")
    cece = CECE(config['DEFAULT'], logger=appLogger)
    cece.auth()
    oferta = cece.get_cursos()
    appLogger.info(f"{len(oferta)} cursos extraidos")

    filename = config['DEFAULT']['Filename'] if config[
        'DEFAULT']['Filename'] else f"{uuid.uuid1()}.json"

    # Chequea que exista la carpeta de guardado, sino la crea
    if not os.path.isdir(config['DEFAULT']['SaveFolder']):
        os.mkdir(config['DEFAULT']['SaveFolder'])

    with open(os.path.join(config['DEFAULT']['SaveFolder'], filename), "w", encoding='utf-8') as f:
        appLogger.info(f"Guardando oferta en '{f.name}'")
        json.dump(oferta, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

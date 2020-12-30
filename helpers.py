import re


def strip_strings(value):
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in value.keys():
            value[key] = strip_strings(value[key])
    return value

def get_dia_completo(abreviatura):
    abreviatura = abreviatura.lower()
    switcher = {
        "lu": "lunes",
        "ma": "martes",
        "mi": "miercoles",
        "ju": "jueves",
        "vi": "viernes"
    }
    return switcher.get(abreviatura)

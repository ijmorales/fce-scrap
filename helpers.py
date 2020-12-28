import re


def strip_strings(value):
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in value.keys():
            value[key] = strip_strings(value[key])
        return value


def regex_search_value(pattern, string, groupNumber=0):
    result = re.search(pattern, string)
    if result is not None:
        return result.groups()[groupNumber]
    else:
        return None

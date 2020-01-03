from xml.etree import ElementTree
import _io
import re

class Constants:
    STRIP = 1
    REPLACE_WITH_UNDERSCORES = 2
    STRIP_CAPITALIZE = 3
    IGNORE_TAGS = 4
    USE_NAME_FUNCTION = 5


def strip_namespace(s: str):
    p = s.find('}')
    if p > 0:
        return s[p+1:]
    return s


def strip_illegal_chars_capitalize(s: str):
    res = ''
    cap = False
    for c in s:
        if c in ['-', '.']:
            cap = True
        else:
            res = res + (c.upper() if cap else c)
            cap = False
    return res


def replace_illegal_chars_with(s: str, ch: str):
    return re.sub('[-\.]', ch, s)


def strip_illegal_chars(s: str):
    return replace_illegal_chars_with(s, '')


class XmlSlurper:

    def __init__(self, value):
        self._value = value
        self._illegal_chars = Constants.REPLACE_WITH_UNDERSCORES

    def __len__(self):
        return len(self._value)

    def __getattribute__(self, key: str):
        try:
            return super.__getattribute__(self, key)
        except:
            localValue = object.__getattribute__(self, "_value")
            if key == "_value":
                return localValue
            if isinstance(localValue, (list, dict)):
                if key in localValue:
                    result = localValue[key]
                    if isinstance(result, (list, dict)):
                        return XmlSlurper(result)
                    else:
                        return result
                else:
                    raise KeyError(key)
            return localValue # or raise KeyError(key)??

    def __getitem__(self, key: str):
        try:
            return super.__getitem__(self, key)
        except:
            localValue = self._value
            if isinstance(localValue, (list, dict)):
                result = localValue[key]
                if isinstance(result, (list, dict)):
                    return XmlSlurper(result)
                else:
                    return result
            return localValue

    def __str__(self):
        return str(self._value)

    @classmethod
    def create(cls, data=None, file_name: str = None, illegal_chars: int = Constants.REPLACE_WITH_UNDERSCORES, name_func = None):
        options = {'illegal_chars': illegal_chars, 'name_func': name_func}
        if file_name is not None:
            return XmlSlurper(cls._get_map(ElementTree.parse(file_name).getroot(), options))
        if isinstance(data, str):
            return XmlSlurper(cls._get_map(ElementTree.fromstring(data), options))
        if isinstance(data, _io._TextIOBase):
            return XmlSlurper(cls._get_map(ElementTree.fromstring(data.read()), options))
        if isinstance(data, ElementTree.Element):
            return XmlSlurper(cls._get_map(data, options))
        raise TypeError('Illegal input argument [data]')

    @classmethod
    def _extract_name(cls, elem, _illegal_chars, name_func):
        result = elem.tag
        result = strip_namespace(result)
        if ('-' in result) or ('.' in result):
            if _illegal_chars == Constants.REPLACE_WITH_UNDERSCORES:
                result = replace_illegal_chars_with(result, '_')
            elif _illegal_chars == Constants.STRIP_CAPITALIZE:
                result = strip_illegal_chars_capitalize(result)
            elif _illegal_chars == Constants.STRIP:
                result = strip_illegal_chars(result)
            elif _illegal_chars == Constants.IGNORE_TAGS:
                result = None
        result = result if name_func is None else name_func(result)
        return result

    @classmethod
    def _get_map(cls, elem, options: dict):
        if len(elem) == 0:
            return elem.text
        else:
            result = {}
            illegal_chars = options['illegal_chars']
            name_func = options['name_func']
            for child in elem:
                child_name = cls._extract_name(child, illegal_chars, name_func)
                if not (child_name is None):
                    child_map = cls._get_map(child, options)
                    if child_name in result:
                        if isinstance(result[child_name], list):
                            result[child_name].append(child_map)
                        else:
                            result[child_name] = [result[child_name], child_map]
                    else:
                        result[child_name] = child_map
            for attr in elem.attrib:
                child_name = attr
                child_map = elem.attrib[attr]
                if child_name in result:
                    if isinstance(result[child_name], list):
                        result[child_name].append(child_map)
                    else:
                        result[child_name] = [result[child_name], child_map]
                else:
                    result[child_name] = child_map
            return result



if __name__ == "__main__":
    pass
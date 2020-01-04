from xml.etree import ElementTree
import _io
import re
import json
from abc import ABCMeta, abstractmethod


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


class AbstractSlurper(metaclass=ABCMeta):
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


class AbstractSlurperBuilder(metaclass=ABCMeta):

    def __init__(self, data=None, file_name: str = None, options: dict = None):
        self.data = data
        self.file_name = file_name
        self.options = options

    @abstractmethod
    def fromFile(self):
        return None

    @abstractmethod
    def fromString(self):
        return None

    @abstractmethod
    def fromStream(self):
        return None

    @abstractmethod
    def _get_map(self, elem, options: dict):
        pass

    def _extract_name(self, childName: str, illegal_chars, name_func):
        result = childName
        if ('-' in result) or ('.' in result):
            if illegal_chars == Constants.REPLACE_WITH_UNDERSCORES:
                result = replace_illegal_chars_with(result, '_')
            elif illegal_chars == Constants.STRIP_CAPITALIZE:
                result = strip_illegal_chars_capitalize(result)
            elif illegal_chars == Constants.STRIP:
                result = strip_illegal_chars(result)
            elif illegal_chars == Constants.IGNORE_TAGS:
                result = None
        result = result if name_func is None else name_func(result)
        return result


class XmlSlurperBuilder(AbstractSlurperBuilder):

    def fromFile(self):
        return self._fromTree(ElementTree.parse(self.file_name).getroot())

    def fromString(self):
        return self._fromTree(ElementTree.fromstring(self.data))

    def fromStream(self):
        return self._fromTree(ElementTree.fromstring(self.data.read()))

    def fromTree(self):
        return self._fromTree(self.data)

    def _fromTree(self, tree):
        return XmlSlurper(self._get_map(tree, self.options))

    def _get_map(self, elem, options: dict):
        if len(elem) == 0:
            return elem.text
        else:
            result = {}
            illegal_chars = options['illegal_chars']
            name_func = options['name_func']
            for child in elem:
                child_name = self._extract_name(strip_namespace(child.tag), illegal_chars, name_func)
                if not (child_name is None):
                    child_map = self._get_map(child, options)
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


class JsonSlurperBuilder(AbstractSlurperBuilder):

    def fromFile(self):
        with open(self.file_name, "r") as f:
            return JsonSlurper(self._get_map(json.loads(f.read()), self.options))

    def fromString(self):
        return JsonSlurper(self._get_map(json.loads(self.data), self.options))

    def fromStream(self):
        return JsonSlurper(self._get_map(json.loads(self.data.read()), self.options))

    def _get_map(self, tree, options: dict):
        if isinstance(tree, dict):
            result = {}
            illegal_chars = options['illegal_chars']
            name_func = options['name_func']
            for child in tree:
                child_name = self._extract_name(str(child), illegal_chars, name_func)
                if not (child_name is None):
                    child_map = self._get_map(tree[child], options)
                    if child_name in result:
                        if isinstance(result[child_name], list):
                            result[child_name].append(child_map)
                        else:
                            result[child_name] = [result[child_name], child_map]
                    else:
                        result[child_name] = child_map
            return result
        elif isinstance(tree, list):
            result = []
            for i in range(len(tree)):
                child_map = self._get_map(tree[i], options)
                result.append(child_map)
            return result
        else:
            return tree


class XmlSlurper(AbstractSlurper):

    @classmethod
    def create(cls, data=None, file_name: str = None, illegal_chars: int = Constants.REPLACE_WITH_UNDERSCORES, name_func = None):
        options = {
            'illegal_chars': illegal_chars, 
            'name_func': name_func
        }
        builder = XmlSlurperBuilder(data, file_name, options)
        if file_name is not None:
            return builder.fromFile()
        if isinstance(data, str):
            return builder.fromString()
        if isinstance(data, _io._TextIOBase):
            return builder.fromStream()
        if isinstance(data, ElementTree.Element):
            return builder.fromTree()
        raise TypeError('Illegal input argument [data]')


class JsonSlurper(AbstractSlurper):

    @classmethod
    def create(cls, data=None, file_name: str = None, illegal_chars: int = Constants.REPLACE_WITH_UNDERSCORES, name_func = None):
        options = {
            'illegal_chars': illegal_chars, 
            'name_func': name_func
        }
        builder = JsonSlurperBuilder(data, file_name, options)
        if file_name is not None:
            return builder.fromFile()
        if isinstance(data, str):
            return builder.fromString()
        if isinstance(data, _io._TextIOBase):
            return builder.fromStream()
        raise TypeError('Illegal input argument [data]')


if __name__ == "__main__":
    pass
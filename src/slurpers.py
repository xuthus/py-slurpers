# -*- coding: utf-8 -*-

import _io
import configparser
import json
import re
from abc import ABCMeta, abstractmethod
from xml.etree import ElementTree


class Constants:
    """Constants for slurpers"""
    STRIP = 1
    """Strip illegal characters in a tag name: 'birth-date' -> 'birthdate'"""
    REPLACE_WITH_UNDERSCORES = 2
    """(Default action) Replace illegal characters in a tag name with underscores: 'birth-date' -> 'birth_date'"""
    STRIP_CAPITALIZE = 3
    """Strip illegal characters in a tag name and capitalize next character: 'birth-date' -> 'birthDate'"""
    IGNORE_NAMES = 4
    """Ignore tags whose names contain illegal characters"""
    USE_NAME_FUNCTION = 5
    """Use `name_func` function to convert tag name to field name (see `AbstractSlurperBuilder._extract_name()`)"""


def strip_namespace(s: str):
    p = s.find('}')
    if p > 0:
        return s[p + 1:]
    return s


def strip_illegal_chars_capitalize(s: str, illegal_chars: tuple = ('-', '.')):
    res = ''
    cap = False
    for c in s:
        if c in illegal_chars:
            cap = True
        else:
            res = res + (c.upper() if cap else c)
            cap = False
    return res


def replace_illegal_chars_with(s: str, ch: str, illegal_chars_mask: str = '[-.]'):
    return re.sub(illegal_chars_mask, ch, s)


def strip_illegal_chars(s: str, illegal_chars_mask: str = '[-.]'):
    return replace_illegal_chars_with(s, '', illegal_chars_mask)


class AbstractSlurper(metaclass=ABCMeta):
    def __init__(self, value):
        self._value = value
        self._illegal_chars_action = Constants.REPLACE_WITH_UNDERSCORES

    def __len__(self):
        return len(self._value)

    def __getattribute__(self, key: str):
        try:
            return super.__getattribute__(self, key)
        except:
            local_value = object.__getattribute__(self, "_value")
            if key == "_value":
                return local_value
            if isinstance(local_value, (list, dict)):
                if key in local_value:
                    result = local_value[key]
                    if isinstance(result, (list, dict)):
                        return XmlSlurper(result)
                    else:
                        return result
                else:
                    raise KeyError(key)
            return local_value  # or raise KeyError(key)??

    def __getitem__(self, key: str):
        try:
            return super.__getitem__(self, key)
        except:
            local_value = self._value
            if isinstance(local_value, (list, dict)):
                result = local_value[key]
                if isinstance(result, (list, dict)):
                    return XmlSlurper(result)
                else:
                    return result
            return local_value

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

    @staticmethod
    def _extract_name(child_name: str, illegal_chars_action, name_func=None, illegal_chars: tuple = ('-', '.'),
                      illegal_chars_mask: str = '[-.]'):
        result = child_name
        has_illegal_chars = False
        for c in illegal_chars:
            has_illegal_chars = has_illegal_chars or c in result
        if has_illegal_chars:
            if illegal_chars_action == Constants.REPLACE_WITH_UNDERSCORES:
                result = replace_illegal_chars_with(result, '_', illegal_chars_mask=illegal_chars_mask)
            elif illegal_chars_action == Constants.STRIP_CAPITALIZE:
                result = strip_illegal_chars_capitalize(result, illegal_chars=illegal_chars)
            elif illegal_chars_action == Constants.STRIP:
                result = strip_illegal_chars(result, illegal_chars_mask=illegal_chars_mask)
            elif illegal_chars_action == Constants.IGNORE_NAMES:
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
            illegal_chars_action = options['illegal_chars_action']
            name_func = options['name_func']
            for child in elem:
                child_name = self._extract_name(strip_namespace(child.tag), illegal_chars_action, name_func)
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
        with open(self.file_name, "r", encoding=self.options['file_charset']) as f:
            return JsonSlurper(self._get_map(json.loads(f.read()), self.options))

    def fromString(self):
        return JsonSlurper(self._get_map(json.loads(self.data), self.options))

    def fromStream(self):
        return JsonSlurper(self._get_map(json.loads(self.data.read()), self.options))

    def _get_map(self, tree, options: dict):
        if isinstance(tree, dict):
            result = {}
            illegal_chars_action = options['illegal_chars_action']
            name_func = options['name_func']
            for child in tree:
                child_name = self._extract_name(str(child), illegal_chars_action, name_func)
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


class ConfigSlurperBuilder(AbstractSlurperBuilder):

    def fromFile(self):
        config = configparser.ConfigParser()
        with open(self.file_name, "r", encoding=self.options['file_charset']) as f:
            config.read_file(f)
        return ConfigSlurper(self._get_map(config, self.options))

    def fromString(self):
        config = configparser.ConfigParser()
        config.read_string(self.data)
        return ConfigSlurper(self._get_map(config, self.options))

    def fromStream(self):
        config = configparser.ConfigParser()
        config.read_file(self.data)
        return ConfigSlurper(self._get_map(config, self.options))

    def _get_map(self, tree, options: dict):
        result = {}
        illegal_chars_action = options['illegal_chars_action']
        name_func = options['name_func']
        illegal_chars = ('-', ' ', '.', '/', '#')
        illegal_chars_mask = '[-\.\/#\s]'
        for section in tree.sections():
            section_name = self._extract_name(section, illegal_chars_action, name_func, illegal_chars=illegal_chars,
                                              illegal_chars_mask=illegal_chars_mask)
            if not (section_name is None):
                child_map = {}
                options = tree.options(section)
                for option in options:
                    option_name = self._extract_name(option, illegal_chars_action, name_func,
                                                     illegal_chars=illegal_chars, illegal_chars_mask=illegal_chars_mask)
                    child_map[option_name] = tree.get(section, option)
                result[section_name] = child_map
        return result


class XmlSlurper(AbstractSlurper):
    """
    Object representation for Xml document\n
    Object can be used for read purposes only - xml modification is not available at all.
    Illegal characters for json tags are: `-` (hyphen), and `.` (dot).
    """
    @classmethod
    def create(cls, data=None, file_name: str = None, illegal_chars_action: int = Constants.REPLACE_WITH_UNDERSCORES,
               name_func=None, file_charset: str = "UTF8"):
        """
        Create python object from the given xml document.\n
        The method converts each xml-tag to corresponding field and assigns its value.

        **data** (optional) - xml-formatted source: string, text stream or ElementTree.Element\n
        **file_name** (optional) - file name for xml document\n
        **illegal_chars_action** (default: `REPLACE_WITH_UNDERSCORES`) - action applied to tags whose names contain illegal characters\n
        **name_func** (optional) - function (or `lambda`) used to convert tag name to field name\n
        **file_charset** (default: `UTF8`) - source file charset
        """
        options = {
            'illegal_chars_action': illegal_chars_action,
            'name_func': name_func,
            'file_charset': file_charset
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
    """
    Object representation for Json document\n
    Object can be used for read purposes only - json modification is not available at all.
    Illegal characters for json tags are: `-` (hyphen), and `.` (dot).
    """
    @classmethod
    def create(cls, data=None, file_name: str = None, illegal_chars_action: int = Constants.REPLACE_WITH_UNDERSCORES,
               name_func=None, file_charset: str = "UTF8"):
        """
        Create python object from the given json document.\n
        The method converts each json-tag to corresponding field and assigns its value.

        **data** (optional) - json-formatted source: string or text stream\n
        **file_name** (optional) - file name for json document\n
        **illegal_chars_action** (default: `REPLACE_WITH_UNDERSCORES`) - action applied to tags whose names contain illegal characters\n
        **name_func** (optional) - function (or `lambda`) used to convert tag name to field name\n
        **file_charset** (default: `UTF8`) - source file charset
        """
        options = {
            'illegal_chars_action': illegal_chars_action,
            'name_func': name_func,
            'file_charset': file_charset
        }
        builder = JsonSlurperBuilder(data, file_name, options)
        if file_name is not None:
            return builder.fromFile()
        if isinstance(data, str):
            return builder.fromString()
        if isinstance(data, _io._TextIOBase):
            return builder.fromStream()
        raise TypeError('Illegal input argument [data]')


class ConfigSlurper(AbstractSlurper):
    """
    Object representation for config (or ini) file\n
    Object can be used for read purposes only - file modification is not available at all.\n\n
    Illegal characters for config parameters are: `-` (hyphen), `.` (dot), ` ` (blank space), `/` (slash), and `#` (sharp).
    """
    @classmethod
    def create(cls, data=None, file_name: str = None, illegal_chars_action: int = Constants.REPLACE_WITH_UNDERSCORES,
               name_func=None, file_charset: str = "UTF8"):
        """
        Create python object from the given config file.\n
        The method converts each config section and parameter to corresponding field and assigns its value.

        **data** (optional) - config (ini) source: string or text stream\n
        **file_name** (optional) - file name for config file\n
        **illegal_chars_action** (default: `REPLACE_WITH_UNDERSCORES`) - action applied to parameters whose names contain illegal characters\n
        **name_func** (optional) - function (or `lambda`) used to convert parameter name to field name\n
        **file_charset** (default: `UTF8`) - source file charset
        """
        options = {
            'illegal_chars_action': illegal_chars_action,
            'name_func': name_func,
            'file_charset': file_charset
        }
        builder = ConfigSlurperBuilder(data, file_name, options)
        if file_name is not None:
            return builder.fromFile()
        if isinstance(data, str):
            return builder.fromString()
        if isinstance(data, _io._TextIOBase):
            return builder.fromStream()
        raise TypeError('Illegal input argument [data]')


if __name__ == "__main__":
    pass

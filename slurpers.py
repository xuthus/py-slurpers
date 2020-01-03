import xml.etree.ElementTree as ET
import _io
import re

class Constants:
    STRIP = 1
    REPLACE_WITH_UNDERSCORES = 2
    STRIP_CAPITALIZE = 3
    IGNORE_TAGS = 4
    USE_NAME_FUNCTION = 5


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
            return XmlSlurper(cls._get_map(ET.parse(file_name).getroot(), options))
        if isinstance(data, str):
            return XmlSlurper(cls._get_map(ET.fromstring(data), options))
        if isinstance(data, _io._TextIOBase):
            return XmlSlurper(cls._get_map(ET.fromstring(data.read()), options))
        if isinstance(data, ET.Element):
            return XmlSlurper(cls._get_map(data, options))
        raise TypeError('Illegal input argument [data]')

    @classmethod
    def _extract_name(cls, elem, _illegal_chars, name_func):
        result = elem.tag
        p = result.find('}')
        if p > 0:
            result = result[p+1:]
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
            return result


tree = ET.parse('testdata/beatles.xml')
root = tree.getroot()
xml = XmlSlurper.create(root)

for m in xml.man:
    print(m)

xml = XmlSlurper.create(file_name = 'testdata/beatles.xml')
for beatle in xml.man:
    print(beatle.surname)
    #print('{} {} born at {} in {}'.format(' '.join(beatle.name) if isinstance(beatle.name, list) else beatle.name, beatle.surname, beatle.born.year, beatle.born.place))


xml = XmlSlurper.create("<data><name>Sergey</name></data>")
print(xml.name)

xml = XmlSlurper.create("<name>Singletag</name>")
print(xml)

xml = XmlSlurper.create("<root><man><name>John</name><surname>Lennon</surname><surname>Smith</surname></man><man><name>Mark</name><surname>Twain</surname></man><born><place>Russia</place><year>2018</year></born></root>")
print(xml.born.place)


with open('testdata/singletag.xml', 'r') as f:
    xml = XmlSlurper.create(f)
    print(xml)

with open('testdata/test1.xml', 'r') as f:
    xml = XmlSlurper.create(f)
    print(xml.born.place)

xml = XmlSlurper.create(file_name='testdata/test1.xml')
print(xml.born.place)

try:
    xml = XmlSlurper.create("<name>Singletag</name")
    print('Failed')
except:
    print('OK: Wrong xml handled')
    pass


xml = XmlSlurper.create("<name>Singletag</name>")
try:
    print(xml.Name)
    print('Failed')
except:
    print('OK: Wrong tag name handled')
    pass


xml = XmlSlurper.create("<name>Singletag</name>")
try:
    print(xml.name[0])
    print('Failed')
except:
    print('OK: Wrong tag index handled')
    pass

# # test files
xml = XmlSlurper.create(file_name='testdata/logback.xml')
print(xml.appender[0].encoder.pattern)
print(xml.appender[0].filter.level)
print(len(xml.appender))

xml = XmlSlurper.create(file_name='testdata/test.xml')
print(xml)
print(xml.movie[0])
print(len(xml.movie))
for movie in xml.movie:
    print(movie)
    #print(movie, movie.namespace)

xml = XmlSlurper.create("<name>Singletag</name>")
print(xml)

xml = XmlSlurper.create(file_name = 'testdata/beatles.xml')
for man in xml.man:
    print('{} {} born at {} in {}'.format(' '.join(man.name), man.surname, man.born.year, man.born.place))

xml = XmlSlurper.create(file_name = 'testdata/tags-illegals.xml')
print(xml.tag_one)
print(xml.tag_two)

xml = XmlSlurper.create(file_name = 'testdata/tags-illegals.xml', illegal_chars = Constants.STRIP)
print(xml.tagone)
print(xml.tagtwo)

xml = XmlSlurper.create(file_name = 'testdata/tags-illegals.xml', illegal_chars = Constants.IGNORE_TAGS)
try:
    print(xml.tag_one)
    print('failed IGNORE_TAGS')
except:
    print('ok IGNORE_TAGS')
    pass

xml = XmlSlurper.create(file_name = 'testdata/tags-illegals.xml', illegal_chars = Constants.REPLACE_WITH_UNDERSCORES)
print(xml.tag_one)
print(xml.tag_two)

print(strip_illegal_chars_capitalize('test-tag'))
print(strip_illegal_chars_capitalize('test-t.ag'))
print(strip_illegal_chars_capitalize('test-.-tag'))
print(strip_illegal_chars_capitalize('testtag'))
print(strip_illegal_chars_capitalize('_'))

xml = XmlSlurper.create(file_name = 'testdata/tags-illegals.xml', illegal_chars = Constants.STRIP_CAPITALIZE)
print(xml.tagOne)
print(xml.tagTwo)

xml = XmlSlurper.create(file_name = 'testdata/tags-illegals.xml', illegal_chars = Constants.USE_NAME_FUNCTION, name_func = lambda x: strip_illegal_chars(x) + '__')
print(xml.tagone__)
print(xml.tagtwo__)



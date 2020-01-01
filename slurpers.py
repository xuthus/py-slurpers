import xml.etree.ElementTree as ET
import _io


class XmlSlurper:
    def __init__(self, value):
        self._value = value

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
    def create(cls, data=None, file_name: str = None):
        if file_name is not None:
            return XmlSlurper(cls._get_map(ET.parse(file_name).getroot()))
        if isinstance(data, str):
            return XmlSlurper(cls._get_map(ET.fromstring(data)))
        if isinstance(data, _io._TextIOBase):
            return XmlSlurper(cls._get_map(ET.fromstring(data.read())))
        if isinstance(data, ET.Element):
            return XmlSlurper(cls._get_map(data))
        raise TypeError('Illegal input argument [data]')

    @classmethod
    def _extract_name(cls, elem):
        result = elem.tag
        p = result.find('}')
        if p > 0:
            return result[p+1:]
        return result

    @classmethod
    def _get_map(cls, elem):
        if len(elem) == 0:
            return elem.text
        else:
            result = {}
            for child in elem:
                child_map = cls._get_map(child)
                child_name = cls._extract_name(child)
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

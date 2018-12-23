import xml.etree.ElementTree as ET
import _io


class XmlSlurper:
    options = {
        'strip_namespace': True
    }

    def __init__(self, value=None, namespace: str = None):
        self._value = value
        self.namespace = namespace
        return

    def __str__(self):
        localValue = object.__getattribute__(self, "_value")
        if isinstance(localValue, str):
            return "::" + localValue
        else:
            return super.__str__(self)

    def __getattribute__(self, key: str):
        try:
            return super.__getattribute__(self, key)
        except:
            localValue = object.__getattribute__(self, "_value")
            if key == "_value":
                return localValue
            if isinstance(localValue, (list, dict)):
                if key in localValue:
                    return localValue[key]
                else:
                    raise KeyError(key)
            return localValue

    @staticmethod
    def extract_name(element: ET.Element):
        name = element.tag
        if '}' in name:
            namespace = name[name.index('{') + 1:name.index('}') - 1]
            name = name[name.index('}') + 1:]
        else:
            namespace = None
        return name, namespace

    @staticmethod
    def _add_element_to_dict(element: ET.Element, map: dict):
        tag, namespace = __class__.extract_name(element)
        value = __class__._get_childs(element)
        #value.namespace = namespace
        if tag in map:
            item = map[tag]
            if item is list:
                item.append(value)
            else:
                map[tag] = [item, value]
        else:
            map[tag] = value

    @staticmethod
    def _get_childs(element: ET.Element):
        if len(element) == 0:
            return element.text
        else:
            map = {}
            for child in element:
                __class__._add_element_to_dict(child, map)
            return __class__(value=map)

    @classmethod
    def create(cls, data=None, file_name: str = None):
        if file_name is not None:
            return cls._get_childs(ET.parse(file_name).getroot())
        if isinstance(data, str):
            return cls._get_childs(ET.fromstring(data))
        if isinstance(data, _io._TextIOBase):
            return cls._get_childs(ET.fromstring(data.read()))
        if isinstance(data, ET.Element):
            return cls._get_childs(data)
        raise TypeError('Illegal input argument [data]')


tree = ET.parse('testdata/test1.xml')
root = tree.getroot()
xml = XmlSlurper.create(root)

print(xml.man)

for man in xml.man:
    print(man.name)
    print(man.surname[0])
print(xml.born.place)
print(xml.born.year)

xml = XmlSlurper.create("<data><name>Sergey</name></data>")
print(xml.name)

xml = XmlSlurper.create("<name>Singletag</name>")
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

# test files
xml = XmlSlurper.create(file_name='testdata/logback.xml')
print(xml.appender[0].encoder.pattern)
print(xml.appender[0].filter.level)
print(len(xml.appender))

xml = XmlSlurper.create(file_name='testdata/test.xml')
print(xml.movie[0])
print(len(xml.movie))
for movie in xml.movie:
    print(movie)
    #print(movie, movie.namespace)

import unittest
from slurpers import *
from xml.etree.ElementTree import ParseError


class TestSlurperFunctions(unittest.TestCase):
    def test_strip_illegal_chars_capitalize(self):
        self.assertEqual('numberOfTracks', strip_illegal_chars_capitalize('number-of-tracks'))
        self.assertEqual('testone', strip_illegal_chars_capitalize('testone'))
        self.assertEqual('testone', strip_illegal_chars_capitalize('testone-'))
        self.assertEqual('testOne', strip_illegal_chars_capitalize('test-one'))
        self.assertEqual('testOne', strip_illegal_chars_capitalize('test.one'))
        self.assertEqual('testOne', strip_illegal_chars_capitalize('test-.-one'))
        self.assertEqual('testOne', strip_illegal_chars_capitalize('test..--one'))
        self.assertEqual('testOne', strip_illegal_chars_capitalize('test-.-one-.-'))

    def test_replace_illegal_chars_with(self):
        self.assertEqual('testone', replace_illegal_chars_with('testone', '/'))
        self.assertEqual('test/one', replace_illegal_chars_with('test-one', '/'))
        self.assertEqual('test/one', replace_illegal_chars_with('test.one', '/'))
        self.assertEqual('test///one', replace_illegal_chars_with('test-.-one', '/'))
        self.assertEqual('test////one', replace_illegal_chars_with('test..--one', '/'))
        self.assertEqual('test///one///', replace_illegal_chars_with('test-.-one-.-', '/'))

    def test_strip_illegal_chars(self):
        self.assertEqual('testone', strip_illegal_chars('testone'))
        self.assertEqual('testone', strip_illegal_chars('test-one'))
        self.assertEqual('testone', strip_illegal_chars('test.one'))
        self.assertEqual('testone', strip_illegal_chars('test-.-one'))
        self.assertEqual('testone', strip_illegal_chars('test--..one'))

    def test_strip_namespace(self):
        self.assertEqual('test', strip_namespace('test'))
        self.assertEqual('test', strip_namespace('{http://localhost:8080}test'))
        self.assertEqual('', strip_namespace('{http://localhost:8080}'))


class TestXmlSlurper(unittest.TestCase):
    def test_Beatles(self):
        tree = ElementTree.parse('testdata/beatles.xml')
        root = tree.getroot()
        xml = XmlSlurper.create(root)

        self.assertEqual(4, len(xml.man))

        xml = XmlSlurper.create(file_name = 'testdata/beatles.xml')
        for beatle in xml.man:
            self.assertTrue(beatle.surname in ['Lennon', 'McCartney', 'Starr', 'Harrison'])
    
        xml = XmlSlurper.create(file_name = 'testdata/beatles.xml')
        res = []
        for man in xml.man:
            res.append('{} {} born at {} in {}'.format(' '.join(man.name), man.surname, man.born.year, man.born.place))
        self.assertEqual(
            'John Winston Lennon born at 1940 in Liverpool\nJames Paul McCartney born at 1942 in Liverpool\nR i n g o Starr born at 1940 in Liverpool\nG e o r g e Harrison born at 1943 in Liverpool',
            '\n'.join(res)
        )

    def test_simple(self):
        xml = XmlSlurper.create("<data><name>Sergey</name></data>")
        self.assertEqual('Sergey', xml.name)

    def test_single_tag(self):
        xml = XmlSlurper.create("<name>Singletag</name>")
        self.assertEqual('Singletag', str(xml))

    def test_second_level(self):
        xml = XmlSlurper.create("<root><man><name>John</name><surname>Lennon</surname><surname>Smith</surname></man><man><name>Mark</name><surname>Twain</surname></man><born><place>Russia</place><year>2018</year></born></root>")
        self.assertEqual('Russia', xml.born.place)
        self.assertEqual('2018', xml.born.year)

    def test_wrong_xml(self):
        with self.assertRaises(ParseError):
            xml = XmlSlurper.create("<name>John</name")
        with self.assertRaises(ParseError):
            xml = XmlSlurper.create("<name>John</Name>")
        with self.assertRaises(ParseError):
            xml = XmlSlurper.create("<name ame>John</name ame>")

    def test_wrong_tag(self):
        xml = XmlSlurper.create("<root><name>John</name></root>")
        with self.assertRaises(KeyError):
            print(xml.Name)

    def test_wrong_index(self):
        xml = XmlSlurper.create("<root><man><name>John</name></man></root>")
        with self.assertRaises(KeyError):
            print(xml.man[0])
        xml = XmlSlurper.create("<root><man><name>John</name></man><man><name>Paul</name></man></root>")
        self.assertEqual('John', xml.man[0].name)
        self.assertEqual('Paul', xml.man[1].name)
        with self.assertRaises(IndexError):
            print(xml.man[2])

    def test_logback_xml(self):
        xml = XmlSlurper.create(file_name='testdata/logback.xml')
        self.assertEqual('%d{HH:mm:ss} %-5level: %msg%n', xml.appender[0].encoder.pattern)
        self.assertEqual('INFO', xml.appender[0].filter.level)
        self.assertEqual('STDOUT', xml.appender[0].name)
        self.assertEqual(2, len(xml.appender))

    def test_illegals(self):
        xml = XmlSlurper.create(file_name = 'testdata/tags-illegals.xml')
        self.assertEqual('value 1', xml.tag_one)
        self.assertEqual('value 2', xml.tag_two)

        xml = XmlSlurper.create(file_name = 'testdata/tags-illegals.xml', illegal_chars = Constants.STRIP)
        self.assertEqual('value 1', xml.tagone)
        self.assertEqual('value 2', xml.tagtwo)

        xml = XmlSlurper.create(file_name = 'testdata/tags-illegals.xml', illegal_chars = Constants.REPLACE_WITH_UNDERSCORES)
        self.assertEqual('value 1', xml.tag_one)
        self.assertEqual('value 2', xml.tag_two)

        xml = XmlSlurper.create(file_name = 'testdata/tags-illegals.xml', illegal_chars = Constants.STRIP_CAPITALIZE)
        self.assertEqual('value 1', xml.tagOne)
        self.assertEqual('value 2', xml.tagTwo)

        xml = XmlSlurper.create(file_name = 'testdata/tags-illegals.xml', illegal_chars = Constants.USE_NAME_FUNCTION, name_func = lambda x: strip_illegal_chars(x) + '__')
        self.assertEqual('value 1', xml.tagone__)
        self.assertEqual('value 2', xml.tagtwo__)

        xml = XmlSlurper.create(file_name = 'testdata/tags-illegals.xml', illegal_chars = Constants.IGNORE_TAGS)
        with self.assertRaises(KeyError):
            print(xml.tag_one)

        xml = XmlSlurper.create(file_name = 'testdata/cdata.xml')
        self.assertEqual('text value', xml.tag1)
        self.assertEqual('text <message> with CDATA </message>', xml.tag2)
        with self.assertRaises(KeyError):
            print(xml.tag3)

    def test_attributes(self):
        xml = XmlSlurper.create(file_name = 'testdata/attributes.xml')
        res = []
        for country in xml.country:
            res.append("{}: {}".format(country.name, country.population))
        self.assertEqual(
            'Russia: 100\nSpain: 30',
            '\n'.join(res)
        )


class TestJsonSlurper(unittest.TestCase):

    def test_baez(self):
        json = JsonSlurper.create(file_name = "testdata/baez.json", illegal_chars = Constants.STRIP_CAPITALIZE)
        self.assertEqual("Joan", json.name)
        self.assertEqual("Baez", json.surname)
        self.assertEqual(1941, json.born)
        self.assertEqual(5, len(json.albums))
        self.assertEqual("Farewell, Angelina", json.albums[4].name)
        self.assertEqual(14, json.albums[4].numberOfTracks)

    def test_strings(self):
        json = JsonSlurper.create(
            data = '{"name": "Joan", "surname": "Baez", "born": 1941, "albums": [{"name": "Folksingers \'Round Harvard Square", "year": 1959}, {"name": "Joan Baez", "year": 1960}]}', 
            illegal_chars = Constants.STRIP_CAPITALIZE
        )
        self.assertEqual("Joan", json.name)
        self.assertEqual("Baez", json.surname)
        self.assertEqual(1941, json.born)
        self.assertEqual(2, len(json.albums))
        self.assertEqual("Joan Baez", json.albums[1].name)

    def test_streams(self):
        with open("testdata/baez.json", "r") as f:
            json = JsonSlurper.create(data = f, illegal_chars = Constants.STRIP_CAPITALIZE)
            self.assertEqual("Joan", json.name)
            self.assertEqual("Baez", json.surname)
            self.assertEqual(1941, json.born)
            self.assertEqual(5, len(json.albums))
            self.assertEqual("Folksingers 'Round Harvard Square", json.albums[0].name)
            self.assertEqual(18, json.albums[0].numberOfTracks)



class TestCharsets(unittest.TestCase):

    def test_charsets_xml(self):
        xml = XmlSlurper.create(file_name = 'testdata/balalaika.xml', file_charset="windows-1251")
        self.assertEqual("Гагарин", xml.spaceman[0].surname)

    def test_charsets_json(self):
        xml = JsonSlurper.create(file_name = 'testdata/balalaika.json', file_charset="windows-1251")
        self.assertEqual("Юрий", xml.spacemans[0].name)


if __name__ == "__main__":
    unittest.main()
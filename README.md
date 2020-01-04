### Python slurpers for XML, JSON, configs (or .ini) and so on

> Inspired by Groovy's XmlSlurper

Slurper is a object that encapsulates access to structured document file using its dynamic fields as file tags.

## JSON example:

Json document:

```json
{
	"name": "Joan",
	"surname": "Baez",
	"born": 1941,
	"albums": [
		{
			"name": "Folksingers 'Round Harvard Square",
			"year": 1959,
			"number-of-tracks": 18
		},
		{
			"name": "Joan Baez",
			"year": 1960,
			"number-of-tracks": 16
		},
		{
			"name": "Joan Baez, Vol. 2",
			"year": 1961,
			"number-of-tracks": 17
		},
		{
			"name": "Joan Baez/5",
			"year": 1964,
			"number-of-tracks": 14
		},
		{
			"name": "Farewell, Angelina",
			"year": 1965,
			"number-of-tracks": 14
		}
	]
}
```

code:

```python
json = JsonSlurper.create(file_name = "testdata/baez.json", illegal_chars = Constants.STRIP_CAPITALIZE)
self.assertEqual("Joan", json.name)
self.assertEqual("Baez", json.surname)
self.assertEqual(1941, json.born)
self.assertEqual(5, len(json.albums))
self.assertEqual("Farewell, Angelina", json.albums[4].name)
self.assertEqual(14, json.albums[4].numberOfTracks)
```

## Config example:

Sample config file:

```ini
[Database]
host: mysql.google.com
database: search_index

[Security]
auth provider: google

# and so on...
```

code:

```python
config = ConfigSlurper.create(file_name = "testdata/google.config", illegal_chars = Constants.REPLACE_WITH_UNDERSCORES)
self.assertEqual("mysql.google.com", config.Database.host)
self.assertEqual("google", config.Security.auth_provider)
```

## XML example:

Xml document (see in `testdata/test1.xml`):
```xml
<?xml version="1.0" encoding="utf-8"?>
<beatles>
  <man>
    <name>John</name>
    <name>Winston</name>
    <surname>Lennon</surname>
    <born>
        <place>Liverpool</place>
        <year>1940</year>
    </born>
  </man>
  <man>
    <name>James</name>
    <name>Paul</name>
    <surname>McCartney</surname>
    <born>
        <place>Liverpool</place>
        <year>1942</year>
    </born>
  </man>
  <man>
    <name>Ringo</name>
    <surname>Starr</surname>
    <born>
        <place>Liverpool</place>
        <year>1940</year>
    </born>
  </man>
  <man>
    <name>George</name>
    <surname>Harrison</surname>
    <born>
        <place>Liverpool</place>
        <year>1943</year>
    </born>
  </man>
</beatles>
```

Python code:
```python
xml = XmlSlurper.create('testdata/test1.xml')
for man in xml.man:
    print('{} {} born at {} in {}'.format(' '.join(man.name), man.surname, man.born.year, man.born.place))
```

Output:
```
John Winston Lennon born at 1940 in Liverpool
James Paul McCartney born at 1942 in Liverpool
R i n g o Starr born at 1940 in Liverpool
G e o r g e Harrison born at 1943 in Liverpool
```
Starr and Harrison don't have second name, so `man.name` for them is a single string, so `' '.join()` concatenates each char in it.

Lennon and McCartney are *doublenamed*, so `man.name` for them is list.

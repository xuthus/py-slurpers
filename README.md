### Python slurpers for XML, JSON, properties and so on

*Work in progress*

> Inspired by Groovy's XmlSlurper

Slurper is a object that encapsulates access to structured document file using its dynamic fields as file tags.

For example:

Xml document:
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
```
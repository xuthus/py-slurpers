from pyslurpers import XmlSlurper

xml = XmlSlurper.create("<root><color><name>red</name><rgb>FF0000</rgb></color><color><name>green</name><rgb>00FF00</rgb></color></root>")
for color in xml.color:
    print("name: {}, rgb: {}".format(color.name, color.rgb))
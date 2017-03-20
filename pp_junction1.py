import numpy as np
from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment, parse
import fun_write_odr
import copy

# path_in = "/home/jennifer/j.simeon/GEOSAT/BMW/OpenDRIVE/"
# path_out = path_in + "OUTPUT/"
# input_fn = path_out + 'sample_road.xodr'
# tree = parse(input_fn)
# OpenDRIVE = tree.getroot()
path_in="./"
def pp_junction1(OpenDRIVE):
    # post fill controllers
    ControllerElement = SubElement(OpenDRIVE,"controller")
    ControlElement = SubElement(ControllerElement, "control")
    ControlElement.set("signalId", "Signal1")
    ControlElement.set("type","1000001")


    # post fill junction
    junction_element = np.genfromtxt(path_in + 'junction_element.csv', delimiter="|", dtype=str)

    sh2 = SubElement(OpenDRIVE,"junction")
    sh2.set('name', 'Junction1')
    sh2.set('id','1')
    for jid in range(1, len(junction_element)):
        row = junction_element[jid]
        sh3 = SubElement(sh2, "connection")
        sh4 = SubElement(sh3, "laneLink")
        sh3.set("id", row[0])
        sh3.set("incomingRoad", row[1])
        sh3.set("connectingRoad", row[2])
        sh3.set("contactPoint", row[3])
        sh4.set("from", row[4])
        sh4.set("to", row[5])

        if (row[0] == "10" or row[0] == "2"):
            sh3a = SubElement(sh2,"controller")
            sh3a.set("id", "Signal1")
            sh3a.set("type", "1000001")
            sh3a.set("sequence",'1')

    return OpenDRIVE

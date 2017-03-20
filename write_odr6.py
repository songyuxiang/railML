from xml.etree import ElementTree
from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment
from ElementTree_pretty import pretty as pretty
from ElementTree_pretty import indent as pretty_indent
import lxml.etree as etree

import numpy as np
from xml.sax.saxutils import escape
from xml.sax.saxutils import unescape
import glob
import pandas as pd
import fun_write_odr
import copy
from pp_junction1 import *
# Start reading in the data

def generateOdr(fileName="test.csv"):

    input_fn = fileName

    output_fn = fileName.replace("csv","xodr")

    # Top
    OpenDRIVE = Element('OpenDRIVE')

    # header
    header = SubElement(OpenDRIVE, "header")
    geoReference = SubElement(header, "geoReference")


    # Fill in header data
    open_drive_major_rev_num = "1"
    open_drive_minor_rev_num = "4"
    db_name = "geosatodr1.4"
    db_version = "1.00"
    db_date = "2017-02-05T14:00:00"


    InDE = False
    InFR = True
    InAllershausen = False
    InYvrac = True

    # Get the bounding box and fill in header
    if InAllershausen:
        north = "5367745.4613"
        south = "5366178.5176"
        east = "691672.3451"
        west = "691403.5362"
    elif InYvrac:
        north = "4972977.373"
        south = "4972898.543"
        east = "700368.657"
        west = "700277.226"
    else:
        pass

    vendor = "GEOSAT"

    header.set("revMajor", open_drive_major_rev_num)
    header.set("revMinor", open_drive_minor_rev_num)
    header.set("name", db_name)
    header.set("version", db_version)
    header.set("date", db_date)
    header.set("north", north)
    header.set("south", south)
    header.set("east", east)
    header.set("west", west)
    header.set("vendor", vendor)


    if InDE:
        #geoReference.text = "<![CDATA[+proj=utm +zone=32 +ellps=WGS84 +datum=WGS84 +units=m +no_defs]]>"
        geoReference.text = "<![CDATA[+proj=utm +zone=32 +ellps=WGS84 +datum=WGS84 +units=m +no_defs]]>"

    elif InFR:
        geoReference.text = "<[CDATA[+proj=utm +zone=30 +ellps=WGS84 +datum=WGS84 +units=m +no_defs]]>"
    else:
        pass



    data_in = np.genfromtxt(input_fn, delimiter="|", dtype=str)
    data = data_in[np.where(data_in[:,10] != "")]


    # Get counts of Level 1 elements
    num_road_segments = np.unique(data[np.where(data[:, 1] == "road"), 0])
    num_junctions =  np.unique(data[np.where(data[:, 1] == "junction"), 0])
    num_junctionGroups = np.unique(data[np.where(data[:, 1] == "junctionGroup"), 0])
    num_controllers = np.unique(data[np.where(data[:, 1] == "controller"), 0])
    num_stations = np.unique(data[np.where(data[:, 1] == "station"), 0])


    # String tags together
    # consisting of elements, clean-up then add attribute name and id

    tags_array_road = fun_write_odr.gen_tags_array(data[np.where(data[:, 1] == "road")])
    tags_array_junction = fun_write_odr.gen_tags_array(data[np.where(data[:, 1] == "junction")])
    tags_array_junctionGroup = fun_write_odr.gen_tags_array(data[np.where(data[:, 1] == "junctionGroup")])
    tags_array_controller = fun_write_odr.gen_tags_array(data[np.where(data[:, 1] == "controller")])
    tags_array_station = fun_write_odr.gen_tags_array(data[np.where(data[:, 1] == "station")])

    # check for multiple instances of tags by elements+attribute
    #multi_instance_elements = fun_write_odr.return_multi_instance_elements()


    # Set up complete tree
    # Generate the sub-elements
    fun_write_odr.gen_empty_tree(OpenDRIVE)

    # Start to fill attributes

    for iroad, road_id in enumerate(num_road_segments):

        if iroad == 0:
            ElementRoad = OpenDRIVE.find('road')
        else:
            ElementRoad = SubElement(OpenDRIVE, "road")

        tags_array = tags_array_road[tags_array_road[:,0] == str(road_id),1]
        values_array = tags_array_road[tags_array_road[:,0] == str(road_id),2]
        # Set attributes
        for itag, tag_attr in enumerate(tags_array[0:]):

            a = tag_attr.split('_')
            num_levels = len(a) - 1
            tag_now = a[:-1]  # all parent tags up to level 1 plus current tag
            attribute_now = a[-1]

            n = len(tag_now)
            tags_now_string = '_'.join(a[:n])
            parent_tag = '_'.join(a[:n-1])
            element_now = tag_now[-1]
            value = values_array[itag]

            if num_levels == 1:
                ElementRoad.set(attribute_now, value)

            if num_levels == 2:

                if tags_now_string == "road_type":
                    sh2 = ElementRoad.findall(a[1]) # type
                    if len(sh2) > 0:
                        if len(sh2[len(sh2)-1].attrib) == 2:
                            new_sh = SubElement(ElementRoad, element_now)
                            new_sh.set(attribute_now, value)
                        else:
                            sh_last = sh2[len(sh2) - 1]  # last type
                            sh_last.set(attribute_now, value)
                    else:
                        new_sh = SubElement(ElementRoad, element_now)
                        new_sh.set(attribute_now, value)


                else:
                    sh = ElementRoad.findall(a[1])
                    sh_last = sh[len(sh)-1]
                    sh_last.set(attribute_now, value)

            elif num_levels == 3:

                if tags_now_string == "road_type_speed":
                    sh = ElementRoad.findall(a[1]) # type
                    if len(sh) == 0:
                        sh2 = SubElement(ElementRoad, "type")
                        she = SubElement(sh2, element_now)
                        she.set(attribute_now, value)
                    else:
                        sh_last = sh[len(sh)-1]
                        she = sh_last.findall(a[2]) # find speed

                        if len(she) > 0 and len(she[len(she)-1].attrib) < 2:
                            she = she[len(she) - 1]
                            she.set(attribute_now, value)
                        else:
                            new_sh = SubElement(sh_last, element_now)
                            new_sh.set(attribute_now, value)

                elif tags_now_string == "road_planView_geometry":
                    sh2 = ElementRoad.findall(a[1])
                    if len(sh2) == 0:
                        sh2 = SubElement(ElementRoad, a[1]) # make planview
                        she = SubElement(sh2, element_now)  # make geometry
                        she.set(attribute_now, value)
                    else:
                        sh3 = sh2[len(sh2)-1].findall(a[2]) # find geometry
                        sh_last = sh3[len(sh3) - 1] # get last geometry
                        if ( len(sh_last.getchildren()) == 0 and len(sh_last.attrib) < 5 ):
                            sh_last.set(attribute_now, value)
                        else:
                            p_element = ElementRoad.find(a[1]) # find planview
                            new_sh = SubElement(p_element, element_now) # make geometry
                            new_sh.set(attribute_now, value)
                elif tags_now_string == "road_lanes_laneOffset":
                    sh2 = ElementRoad.findall(a[1])
                    sh3 = sh2[len(sh2)-1].findall(a[2])
                    sh_last = sh3[len(sh3) - 1]

                    if (sh_last is not None and len(sh_last.attrib) < 5):
                        sh_last.set(attribute_now, value)
                    else:
                        p_element = ElementRoad.find(a[1])
                        new_sh = SubElement(p_element, element_now)
                        new_sh.set(attribute_now, value)

                elif tags_now_string == "road_lanes_laneSection":
                    sh2 = ElementRoad.findall(a[1])
                    if len(sh2) == 0:
                        sh2 = SubElement(ElementRoad, a[1])
                        she = SubElement(sh2, element_now)
                        she.set(attribute_now, value)
                    else:
                        sh3 = sh2[len(sh2)-1].findall(a[2])

                        she = sh3[len(sh3) - 1]

                        if she is not None and len(she.attrib) == 2:
                            new_sh = SubElement(sh2[len(sh2)-1], element_now)
                            new_sh.set(attribute_now, value)
                        elif she is not None and len(she.attrib) < 3:
                            she.set(attribute_now, value)
                        else:
                            new_sh = SubElement(sh2[len(sh2)-1], element_now)
                            new_sh.set(attribute_now, value)
                elif (tags_now_string == "road_link_predecessor" or
                              tags_now_string == "road_link_successor"):
                    sh2 = ElementRoad.findall(a[1])  # link
                    if len(sh2) == 0:
                        new_sh2 = SubElement(ElementRoad, "link")
                        she = SubElement(new_sh2, element_now)
                        she.set(attribute_now, value)
                    else:
                        sh3 = sh2[len(sh2) - 1].findall(a[2]) # pred suc
                        if len(sh3) == 0:
                            she = SubElement(sh2[len(sh2) - 1], element_now)
                            she.set(attribute_now, value)
                        else:
                            she = sh3[len(sh3) - 1]

                            if she is not None and len(she.getchildren()) == 0:
                                she.set(attribute_now, value)
                            else:
                                new_sh = SubElement(sh2[len(sh2) - 1], element_now)
                                new_sh.set(attribute_now, value)
                elif (tags_now_string == "road_signals_signal"):
                    sh2 = ElementRoad.findall(a[1])
                    if len(sh2) == 0:
                        sh2 = SubElement(ElementRoad, a[1])
                        sh3 = SubElement(sh2, a[2])
                        she = SubElement(sh3,element_now)
                        she.set(attribute_now, value)

                    else:
                        sh3 = sh2[len(sh2)-1].findall(a[2])
                        she = sh3[len(sh3) - 1]

                        if she is not None and len(she.attrib) < 18:
                            she.set(attribute_now, value)
                        else:
                            new_sh = SubElement(sh2[len(sh2)-1], element_now)
                            new_sh.set(attribute_now, value)
                elif (tags_now_string == "road_objects_object"):
                    sh2 = ElementRoad.findall(a[1])
                    if len(sh2) == 0:
                        sh2 = SubElement(ElementRoad, a[1])
                        sh3 = SubElement(sh2, a[2])
                        she = SubElement(sh3,element_now)
                        she.set(attribute_now, value)

                    else:
                        sh3 = sh2[len(sh2)-1].findall(a[2])
                        she = sh3[len(sh3) - 1]

                        if she is not None and len(she.attrib) < 15:
                            she.set(attribute_now, value)
                        else:
                            new_sh = SubElement(sh2[len(sh2)-1], element_now)
                            new_sh.set(attribute_now, value)
                else:
                    sh2 = ElementRoad.findall(a[1])
                    if len(sh2) == 0:
                        sh2 = SubElement(ElementRoad, a[1])
                        sh3 = SubElement(sh2, a[2])
                        she = SubElement(sh3,element_now)
                        she.set(attribute_now, value)

                    else:
                        sh3 = sh2[len(sh2)-1].findall(a[2])
                        she = sh3[len(sh3) - 1]

                        if she is not None and len(she.getchildren()) == 0:
                            she.set(attribute_now, value)
                        else:
                            new_sh = SubElement(sh2[len(sh2)-1], element_now)
                            new_sh.set(attribute_now, value)


            elif num_levels == 4:

                if parent_tag == "road_planView_geometry":
                    sh2 = ElementRoad.findall(a[1])
                    sh3 = sh2[len(sh2)-1].findall(a[2])
                    sh_last = sh3[len(sh3) - 1]
                    # check if no children
                    sh_kids_len = len(sh_last.getchildren())

                    if sh_kids_len == 0:
                        new_sh = SubElement(sh_last, element_now)
                        if element_now == "arc":
                            new_sh.set(attribute_now, value)
                        elif element_now == "poly3":
                            new_sh.set(attribute_now, value)
                        elif element_now == "paramPoly3":
                            new_sh.set(attribute_now, value)
                        elif element_now == "spiral":
                            new_sh.set(attribute_now, value)
                        else:
                            pass
                    else:
                        she = sh_last.findall(a[3])
                        she = she[len(she)-1]
                        if she is not None:
                            she_len_attr = len(she.attrib)

                            if element_now == "poly3" and she_len_attr < 5:
                                she.set(attribute_now, value)
                            elif element_now == "paramPoly3" and she_len_attr < 10:
                                she.set(attribute_now, value)
                            elif element_now == "spiral" and she_len_attr < 3:
                                she.set(attribute_now, value)
                            else:
                                print ("ERROR unknown equation")

                else:
                    sh2 = ElementRoad.findall(a[1])
                    sh3 = sh2[len(sh2)-1].findall(a[2])
                    sh_last = sh3[len(sh3) - 1]
                    sh_kids_len = len(sh_last.getchildren())

                    she = sh_last.findall(a[3])

                    if len(she) > 0:
                        she = she[len(she) - 1]
                        she.set(attribute_now, value)
                    else:
                        new_sh = SubElement(sh_last, element_now)
                        new_sh.set(attribute_now, value)


            elif num_levels == 5:

                if ( parent_tag == "road_lanes_laneSection_left" or \
                     parent_tag == "road_lanes_laneSection_right" or\
                        parent_tag == "road_lanes_laneSection_center" ):
                    lane_sh = ElementRoad.findall(a[1])           #lanes
                    ls_sh = lane_sh[len(lane_sh)-1].findall(a[2]) #lanesection
                    ls_sh_last = ls_sh[len(ls_sh)-1]              #last lanesection

                    if len(ls_sh_last) == 0:
                        # need to make left right center element first
                        lrc_sh_last = SubElement(ls_sh_last, a[3]) # make left right center
                        lane_sh_last = SubElement(lrc_sh_last, element_now) # make lane
                        link_sh = SubElement(lane_sh_last, "link")
                        SubElement(link_sh, "predecessor")
                        SubElement(link_sh,"successor")
                        if a[3] == "right" or a[3] == "left":
                            SubElement(lane_sh_last, "width")
                            #SubElement(lane_sh_last, "border")

                        rmk_sh = SubElement(lane_sh_last, "roadMark")
                        rmk_type_sh = SubElement(rmk_sh, "type")
                        SubElement(rmk_type_sh, "line")

                        # if (a[3] == "right" or a[3] == "left"):
                        #     SubElement(lane_sh_last, "material")
                        #     SubElement(lane_sh_last, "visibility")
                        #     SubElement(lane_sh_last, "speed")
                        #     SubElement(lane_sh_last, "access")
                        #     SubElement(lane_sh_last, "height")
                        #     SubElement(lane_sh_last, "rule")

                    else:
                        # left right center element exists
                        lrc_sh_last = ls_sh_last.findall(a[3])             # get last left right center
                        if len(lrc_sh_last) == 0 :
                            # if lrc is empty
                            lrc_sh_last = SubElement(ls_sh_last, a[3]) # make lrc
                            lane_sh_last = SubElement(lrc_sh_last, element_now)  # make lane
                            link_sh = SubElement(lane_sh_last, "link")
                            SubElement(link_sh, "predecessor")
                            SubElement(link_sh, "successor")
                            if a[3] == "right" or a[3] == "left":
                                SubElement(lane_sh_last, "width")
                                #SubElement(lane_sh_last, "border")

                            rmk_sh = SubElement(lane_sh_last, "roadMark")
                            rmk_type_sh = SubElement(rmk_sh, "type")
                            SubElement(rmk_type_sh, "line")

                            # if (a[3] == "right" or a[3] == "left"):
                            #     SubElement(lane_sh_last, "material")
                            #     SubElement(lane_sh_last, "visibility")
                            #     SubElement(lane_sh_last, "speed")
                            #     SubElement(lane_sh_last, "access")
                            #     SubElement(lane_sh_last, "height")
                            #     SubElement(lane_sh_last, "rule")

                        else:
                            lane_sh_last = lrc_sh_last[len(lrc_sh_last) - 1].findall(a[4])
                            #check if need to init remaining lane elements
                            if ( len(lane_sh_last) > 0 and len(lane_sh_last[len(lane_sh_last) - 1].attrib) < 3 ):
                                lane_sh_last = lane_sh_last[len(lane_sh_last) - 1]
                            else:
                                lane_sh_last = SubElement(lrc_sh_last[len(lrc_sh_last) - 1], element_now)  # make lane
                                link_sh = SubElement(lane_sh_last, "link")
                                SubElement(link_sh, "predecessor")
                                SubElement(link_sh, "successor")
                                if a[3] == "right" or a[3] == "left":
                                    SubElement(lane_sh_last, "width")
                                    #SubElement(lane_sh_last, "border")

                                rmk_sh = SubElement(lane_sh_last, "roadMark")
                                rmk_type_sh = SubElement(rmk_sh, "type")
                                SubElement(rmk_type_sh, "line")

                                # if (a[3] == "right" or a[3] == "left"):
                                #     SubElement(lane_sh_last, "material")
                                #     SubElement(lane_sh_last, "visibility")
                                #     SubElement(lane_sh_last, "speed")
                                #     SubElement(lane_sh_last, "access")
                                #     SubElement(lane_sh_last, "height")
                                #     SubElement(lane_sh_last, "rule")


                    lane_sh_last.set(attribute_now, value)


                else:
                    sh1 = ElementRoad.findall(a[1])
                    sh2 = sh1[len(sh1)-1].findall(a[2])
                    sh = sh2[len(sh2)-1].findall(a[3])
                    sh_len = len(sh)
                    sh_last = sh[sh_len-1]

                    she = sh_last.findall(a[4])
                    she = she[len(she)-1]

                    if she is not None:
                        she.set(attribute_now, value)
                    else:
                        new_sh = SubElement(sh_last, element_now)
                        new_sh.set(attribute_now, value)

            elif num_levels == 6:
                sh1 = ElementRoad.findall(a[1])    # lanes
                sh2 = sh1[len(sh1) - 1].findall(a[2]) #lanesection
                sh3 = sh2[len(sh2) - 1].findall(a[3]) # rcl
                sh_last = sh3[len(sh3) - 1].findall(a[4])  # lane

                if sh_last is not None:

                    she = sh_last[len(sh_last)-1].findall(a[5])                   # find link/roadmark

                    if len(she) > 0:
                        she = she[len(she) - 1]
                        she.set(attribute_now, value)
                    else:
                        #print tags_now_string
                        #print element_now
                        #print sh_last
                        new_sh = SubElement(sh_last[len(sh_last)-1], element_now)
                        new_sh.set(attribute_now, value)
                else :
                    new_lane = SubElement(sh3, a[4])
                    new_lane_kid = SubElement(new_lane, a[5])
                    new_lane_kid.set(attribute_now,value)

            elif num_levels == 7:
                sh1 = ElementRoad.findall(a[1])    # lanes

                sh2 = sh1[len(sh1) - 1].findall(a[2]) #lanesection

                sh3 = sh2[len(sh2) - 1].findall(a[3]) # rcl

                sh4 = sh3[len(sh3) - 1].findall(a[4]) # lane last

                sh_last = sh4[len(sh4) - 1].findall(a[5])  # link/roadmark

                if len(sh_last) > 0:
                    she_list = sh_last[len(sh_last)-1].findall(a[6])

                    if len(she_list) > 0:
                        she = she_list[len(she_list) - 1]
                        she.set(attribute_now, value)
                    else:
                        new_sh = SubElement(sh_last[len(sh_last)-1], element_now)
                        new_sh.set(attribute_now, value)
                else :
                    new_sh = SubElement(sh4[len(sh4)-1], a[5])
                    new_sh_kid = SubElement(new_sh, a[6])
                    new_sh_kid.set(attribute_now,value)


            elif num_levels == 8:
                sh1 = ElementRoad.findall(a[1])
                sh2 = sh1[len(sh1) - 1].findall(a[2])
                sh3 = sh2[len(sh2) - 1].findall(a[3])
                sh4 = sh3[len(sh3) - 1].findall(a[4])
                sh5 = sh4[len(sh4) - 1].findall(a[5])
                sh = sh5[len(sh5) - 1].findall(a[6])
                sh_len = len(sh)
                sh_last = sh[sh_len - 1]

                she = sh_last.findall(a[7])
                she = she[len(she) - 1]

                if she is not None:
                    she.set(attribute_now, value)
                else:
                    new_sh = SubElement(sh_last, element_now)
                    new_sh.set(attribute_now, value)


            else:
                pass

    print ("Start junction analysis")

    for ijunc, junc_id in enumerate(num_junctions):

        if ijunc == 0:
            ElementJunction = OpenDRIVE.find('junction')
        else:
            ElementJunction = SubElement(OpenDRIVE, "junction")

        tags_array = tags_array_junction[tags_array_junction[:, 0] == str(junc_id), 1]
        values_array = tags_array_junction[tags_array_junction[:, 0] == str(junc_id), 2]
        # Set attributes

        for itag, tag_attr in enumerate(tags_array[0:]):

            a = tag_attr.split('_')
            num_levels = len(a) - 1
            tag_now = a[:-1]  # all parent tags up to level 1 plus current tag
            attribute_now = a[-1]

            n = len(tag_now)
            tags_now_string = '_'.join(a[:n])
            parent_tag = '_'.join(a[:n - 1])
            element_now = tag_now[-1]
            value = values_array[itag]

            if num_levels == 1:
                ElementJunction.set(attribute_now, value)
            elif num_levels == 2:
                if ijunc == 0:
                    sh_last = ElementJunction.findall(a[1])
                    she = sh_last[len(sh_last)-1]
                else:
                    she = SubElement(ElementJunction, a[1])

                if she is not None:
                    if element_now == "connection" and len(she.attrib) < 5:
                        she.set(attribute_now, value)
                    elif element_now == "priority" and len(she.attrib) < 3:
                        she.set(attribute_now, value)
                    elif element_now == "controller" and len(she.attrib) < 3:
                        she.set(attribute_now, value)
                else:
                    new_sh = SubElement(ElementJunction, element_now)
                    new_sh.set(attribute_now, value)

            elif num_levels == 3:
                sh2 = ElementJunction.findall(a[1]) # connection
                sh3 = sh2[len(sh2) - 1].findall(a[2]) #lanelink
                she = sh3[len(sh3) - 1]

                if she is not None :
                    she.set(attribute_now, value)
                else:
                    new_sh = SubElement(sh2, element_now)
                    new_sh.set(attribute_now, value)

    print ("Starting station analysis")
    for istn, stn_id in enumerate(num_stations):

        if istn == 0:
            ElementStation = OpenDRIVE.find('station')
        else:
            ElementStation = SubElement(OpenDRIVE, "station")

        tags_array = tags_array_station[tags_array_station[:, 0] == str(stn_id), 1]
        values_array = tags_array_station[tags_array_station[:, 0] == str(stn_id), 2]
        # Set attributes
        for itag, tag_attr in enumerate(tags_array[0:]):

            a = tag_attr.split('_')
            num_levels = len(a) - 1
            tag_now = a[:-1]  # all parent tags up to level 1 plus current tag
            attribute_now = a[-1]

            n = len(tag_now)
            tags_now_string = '_'.join(a[:n])
            parent_tag = '_'.join(a[:n - 1])
            element_now = tag_now[-1]
            value = values_array[itag]

            if num_levels == 1:
                ElementStation.set(attribute_now, value)
            elif num_levels == 2:

                if istn == 0:
                    sh_last = ElementStation.findall(a[1])
                    she = sh_last[len(sh_last)-1]
                else:
                    she = SubElement(ElementStation, a[1])


                if she is not None and len(she.attrib) < 3:
                    she.set(attribute_now, value)
                else:
                    new_sh = SubElement(ElementStation, element_now)
                    new_sh.set(attribute_now, value)

            elif num_levels == 3:
                sh2 = ElementStation.findall(a[1]) # platform
                sh3 = sh2[len(sh2) - 1].findall(a[2]) #segment
                she = sh3[len(sh3) - 1]

                if she is not None:
                    she.set(attribute_now, value)
                else:
                    new_sh = SubElement(sh2, element_now)
                    new_sh.set(attribute_now, value)

    print ("Starting junctionGroup analysis")
    for ijuncgrp, juncgrp_id in enumerate(num_junctionGroups):

        if ijuncgrp == 0:
            ElementJunctionGroup = OpenDRIVE.find('junctionGroup')
        else:
            ElementJunctionGroup = SubElement(OpenDRIVE, "junctionGroup")


        tags_array = tags_array_junctionGroup[tags_array_junctionGroup[:, 0] == str(juncgrp_id), 1]
        values_array = tags_array_junctionGroup[tags_array_junctionGroup[:, 0] == str(juncgrp_id), 2]
        # Set attributes
        for itag, tag_attr in enumerate(tags_array[0:]):

            a = tag_attr.split('_')
            num_levels = len(a) - 1
            tag_now = a[:-1]  # all parent tags up to level 1 plus current tag
            attribute_now = a[-1]

            n = len(tag_now)
            tags_now_string = '_'.join(a[:n])
            parent_tag = '_'.join(a[:n - 1])
            element_now = tag_now[-1]
            value = values_array[itag]

            if num_levels == 1:
                ElementJunctionGroup.set(attribute_now, value)
            elif num_levels == 2:

                if ijunc == 0:
                    sh_last = ElementJunctionGroup.findall(a[1])
                    she = sh_last[len(sh_last)-1]
                else:
                    she = SubElement(ElementJunctionGroup, a[1])


                if she is not None and len(she.attrib) == 0:
                    she.set(attribute_now, value)
                else:
                    new_sh = SubElement(ElementJunctionGroup, element_now)
                    new_sh.set(attribute_now, value)

    print ("Start controller")
    for icontroller, controller_id in enumerate(num_controllers):

        if icontroller == 0:
            ElementController = OpenDRIVE.find('controller')
        else:
            ElementController = SubElement(OpenDRIVE, "controller")


        tags_array = tags_array_controller[tags_array_controller[:, 0] == str(controller_id), 1]
        values_array = tags_array_controller[tags_array_controller[:, 0] == str(controller_id), 2]
        # Set attributes
        for itag, tag_attr in enumerate(tags_array[0:]):

            a = tag_attr.split('_')
            num_levels = len(a) - 1
            tag_now = a[:-1]  # all parent tags up to level 1 plus current tag
            attribute_now = a[-1]

            n = len(tag_now)
            tags_now_string = '_'.join(a[:n])
            parent_tag = '_'.join(a[:n - 1])
            element_now = tag_now[-1]
            value = values_array[itag]

            if num_levels == 1:
                ElementController.set(attribute_now, value)
            elif num_levels == 2:

                if icontroller == 0:
                    sh_last = ElementController.findall(a[1])
                    she = sh_last[len(sh_last)-1]
                else:
                    she = SubElement(ElementController, a[1])


                if she is not None and len(she.attrib) < 3:
                    she.set(attribute_now, value)
                else:
                    new_sh = SubElement(ElementController, element_now)
                    new_sh.set(attribute_now, value)


    print ("Post-process sequences")
    OpenDRIVE = fun_write_odr.check_width_border(OpenDRIVE)
    OpenDRIVE = fun_write_odr.sequence_lanes(OpenDRIVE)
    OpenDRIVE = fun_write_odr.sequence_signals(OpenDRIVE)
    OpenDRIVE = fun_write_odr.sequence_objects(OpenDRIVE)
    OpenDRIVE = fun_write_odr.post_fill_elevation(OpenDRIVE)
    OpenDRIVE = fun_write_odr.post_fill_elevationProfile(OpenDRIVE)
    OpenDRIVE = fun_write_odr.post_fill_geometry_line(OpenDRIVE)

    def snip_roadMarks(OpenDRIVE):
        for RoadElement in OpenDRIVE.findall('./road[@id]'):
            road_id = RoadElement.attrib['id']
            if road_id ==1002 or road_id==1003:
                sh_ln = RoadElement.findall("./lanes/laneSection/right/*[@id='-1']")
                she = RoadElement.findall("./lanes/laneSection/right/*[@id='-1']/roadMark")
                for she_id in range(0, len(she)):
                    sh_ln[she_id].remove(she[she_id])
        return OpenDRIVE
    # OpenDRIVE=snip_roadMarks(OpenDRIVE)
    print ("Run now pp_junction1.py to add junction")
    # OpenDRIVE = pp_junction1(OpenDRIVE)
    fun_write_odr.write_odr_to_xml(OpenDRIVE, output_fn)

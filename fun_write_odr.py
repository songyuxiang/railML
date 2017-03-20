from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment
from ElementTree_pretty import pretty as pretty

import numpy as np
import copy


def gen_tags_array(data):
    tags_array_full=[]
    for i in range(0, data.shape[0]):
        string_of_tags0 = data[i,1] + "_" + data[i,2] + "_"   \
                          + data[i,3] + "_" + data[i,4] + "_" \
                          + data[i,5] + "_" + data[i,6] + "_" \
                          + data[i,7] + "_" + data[i,8]

        cleaned_tags = str(string_of_tags0).\
                       replace("_______","").\
                       replace("______","").\
                       replace("_____","").\
                       replace("____","").\
                       replace("___","").\
                       replace("__","")

        string_of_tags = cleaned_tags + "_" + data[i, 9]
        tmp_array = np.array([data[i,0], string_of_tags.replace("__","_"), data[i,10]] )
        if len(tags_array_full) == 0:
            tags_array_full = tmp_array
        else:
            tags_array_full = np.vstack([tags_array_full, tmp_array])

    return tags_array_full


def gen_empty_tree(OpenDRIVE):
    road = SubElement(OpenDRIVE, "road")
    road_link = SubElement(road, "link")
    road_link_predecessor = SubElement(road_link, "predecessor")
    road_link_successor = SubElement(road_link, "successor")
    road_link_neighbor = SubElement(road_link, "neighbor")
    road_type = SubElement(road, "type")
    road_type_speed = SubElement(road_type, "speed")
    road_planView = SubElement(road, "planView")
    road_planView_geometry = SubElement(road_planView, "geometry")
    #road_planView_geometry_line = SubElement(road_planView_geometry, "line")
    #road_planView_geometry_spiral = SubElement(road_planView_geometry, "spiral")
    #road_planView_geometry_arc = SubElement(road_planView_geometry, "arc")
    #road_planView_geometry_poly3 = SubElement(road_planView_geometry, "poly3")
    #road_planView_geometry_paramPoly3 = SubElement(road_planView_geometry, "paramPoly3")
    road_elevationProfile = SubElement(road, "elevationProfile")
    road_elevationProfile_elevation = SubElement(road_elevationProfile, "elevation")
    road_lateralProfile = SubElement(road, "lateralProfile")
    road_lateralProfile_superelevation = SubElement(road_lateralProfile, "superelevation")
    #road_lateralProfile_crossfall = SubElement(road_lateralProfile, "crossfall")
    #road_lateralProfile_shape = SubElement(road_lateralProfile, "shape")
    road_lanes = SubElement(road, "lanes")
    road_lanes_laneOffset = SubElement(road_lanes, "laneOffset")
    road_lanes_laneSection = SubElement(road_lanes, "laneSection")

    # left lane
    road_lanes_laneSection_left                         = SubElement(road_lanes_laneSection, "left")
    road_lanes_laneSection_left_lane                    = SubElement(road_lanes_laneSection_left, "lane")
    road_lanes_laneSection_left_lane_link               = SubElement(road_lanes_laneSection_left_lane, "link")
    road_lanes_laneSection_left_lane_link_predecessor   = SubElement(road_lanes_laneSection_left_lane_link, "predecessor")
    road_lanes_laneSection_left_lane_link_successor     = SubElement(road_lanes_laneSection_left_lane_link, "successor")
    road_lanes_laneSection_left_lane_width              = SubElement(road_lanes_laneSection_left_lane, "width")
    #road_lanes_laneSection_left_lane_border             = SubElement(road_lanes_laneSection_left_lane, "border")
    road_lanes_laneSection_left_lane_roadMark           = SubElement(road_lanes_laneSection_left_lane, "roadMark")
    road_lanes_laneSection_left_lane_roadMark_type      = SubElement(road_lanes_laneSection_left_lane_roadMark, "type")
    road_lanes_laneSection_left_lane_roadMark_type_line = SubElement(road_lanes_laneSection_left_lane_roadMark_type, "line")
    # road_lanes_laneSection_left_lane_material           = SubElement(road_lanes_laneSection_left_lane, "material")
    # road_lanes_laneSection_left_lane_visibility         = SubElement(road_lanes_laneSection_left_lane, "visibility")
    # road_lanes_laneSection_left_lane_speed              = SubElement(road_lanes_laneSection_left_lane, "speed")
    # road_lanes_laneSection_left_lane_access             = SubElement(road_lanes_laneSection_left_lane, "access")
    # road_lanes_laneSection_left_lane_height             = SubElement(road_lanes_laneSection_left_lane, "height")
    # road_lanes_laneSection_left_lane_rule               = SubElement(road_lanes_laneSection_left_lane, "rule")

    # center lane
    road_lanes_laneSection_center                         = SubElement(road_lanes_laneSection, "center")
    road_lanes_laneSection_center_lane                    = SubElement(road_lanes_laneSection_center, "lane")
    road_lanes_laneSection_center_lane_link               = SubElement(road_lanes_laneSection_center_lane, "link")
    road_lanes_laneSection_center_lane_link_predecessor   = SubElement(road_lanes_laneSection_center_lane_link, "predecessor")
    road_lanes_laneSection_center_lane_link_successor     = SubElement(road_lanes_laneSection_center_lane_link, "successor")
    road_lanes_laneSection_center_lane_roadMark           = SubElement(road_lanes_laneSection_center_lane, "roadMark")
    road_lanes_laneSection_center_lane_roadMark_type      = SubElement(road_lanes_laneSection_center_lane_roadMark, "type")
    road_lanes_laneSection_center_lane_roadMark_type_line = SubElement(road_lanes_laneSection_center_lane_roadMark_type, "line")

    # right lane
    road_lanes_laneSection_right                         = SubElement(road_lanes_laneSection, "right")
    road_lanes_laneSection_right_lane                    = SubElement(road_lanes_laneSection_right, "lane")
    road_lanes_laneSection_right_lane_link               = SubElement(road_lanes_laneSection_right_lane, "link")
    road_lanes_laneSection_right_lane_link_predecessor   = SubElement(road_lanes_laneSection_right_lane_link, "predecessor")
    road_lanes_laneSection_right_lane_link_successor     = SubElement(road_lanes_laneSection_right_lane_link, "successor")
    road_lanes_laneSection_right_lane_width              = SubElement(road_lanes_laneSection_right_lane, "width")
    #road_lanes_laneSection_right_lane_border             = SubElement(road_lanes_laneSection_right_lane, "border")
    road_lanes_laneSection_right_lane_roadMark           = SubElement(road_lanes_laneSection_right_lane, "roadMark")
    road_lanes_laneSection_right_lane_roadMark_type      = SubElement(road_lanes_laneSection_right_lane_roadMark, "type")
    road_lanes_laneSection_right_lane_roadMark_type_line = SubElement(road_lanes_laneSection_right_lane_roadMark_type, "line")
    #road_lanes_laneSection_right_lane_material           = SubElement(road_lanes_laneSection_right_lane, "material")
    #road_lanes_laneSection_right_lane_visibility         = SubElement(road_lanes_laneSection_right_lane, "visibility")
    #road_lanes_laneSection_right_lane_speed              = SubElement(road_lanes_laneSection_right_lane, "speed")
    #road_lanes_laneSection_right_lane_access             = SubElement(road_lanes_laneSection_right_lane, "access")
    #road_lanes_laneSection_right_lane_height             = SubElement(road_lanes_laneSection_right_lane, "height")
    #road_lanes_laneSection_right_lane_rule               = SubElement(road_lanes_laneSection_right_lane, "rule")

    # objects
    road_objects                             = SubElement(road, "objects")
    road_objects_object                      = SubElement(road_objects, "object")
    # road_objects_object_repeat               = SubElement(road_objects_object, "repeat")
    # road_objects_object_outline              = SubElement(road_objects_object, "outline")
    # #road_objects_object_outline_cornerRoad   = SubElement(road_objects_object_outline, "cornerRoad")
    # #road_objects_object_outline_cornerLocal  = SubElement(road_objects_object_outline, "cornerLocal")
    # road_objects_object_material             = SubElement(road_objects_object, "material")
    # road_objects_object_validity             = SubElement(road_objects_object, "validity")
    # road_objects_object_parkingSpace         = SubElement(road_objects_object, "parkingSpace")
    # road_objects_object_parkingSpace_marking = SubElement(road_objects_object_parkingSpace, "marking")
    # road_objects_objectReference             = SubElement(road_objects, "objectReference")
    # road_objects_objectReference_validity    = SubElement(road_objects_objectReference, "validity")
    # road_objects_tunnel                      = SubElement(road_objects, "tunnel")
    # road_objects_tunnel_validity             = SubElement(road_objects_tunnel, "validity")
    # road_objects_bridge                      = SubElement(road_objects, "bridge")
    # road_objects_bridge_validity             = SubElement(road_objects_bridge, "validity")
    #
    # # Signals
    road_signals                             = SubElement(road, "signals")
    road_signals_signal                      = SubElement(road_signals, "signal")
    road_signals_signal_validity             = SubElement(road_signals_signal, "validity")
    road_signals_signal_dependency           = SubElement(road_signals_signal, "dependency")
    road_signals_signalReference             = SubElement(road_signals, "signalReference")
    road_signals_signalReference_validity    = SubElement(road_signals_signalReference, "validity")
    #
    # # Surface
    # road_surface                             = SubElement(road, "surface")
    # road_surface_CRG                         = SubElement(road_surface, "CRG")
    #
    # # Railroad
    # road_railroad                            = SubElement(road, "railroad")
    # road_railroad_switch                     = SubElement(road_railroad, "switch")
    # road_railroad_switch_mainTrack           = SubElement(road_railroad_switch, "mainTrack")
    # road_railroad_switch_sideTrack           = SubElement(road_railroad_switch, "sideTrack")
    # road_railroad_switch_partner             = SubElement(road_railroad_switch, "partner")
    #
    # # Controller
    # controller = SubElement(OpenDRIVE, "controller")
    # control = SubElement(controller, "control")


    # JunctionGroup
    # junctionGroup                   = SubElement(OpenDRIVE, "junctionGroup")
    # junctionGroup_junctionReference = SubElement(junctionGroup, "junctionReference")

    # Station
    #station                  = SubElement(OpenDRIVE, "station")
    #station_platform         = SubElement(station, "platform")
    #station_platform_segment = SubElement(station_platform, "segment")

def write_odr_to_xml(OpenDRIVE, output_fn):
    # Write to file
    text_file = open(output_fn, mode="w")
    text_file.write(pretty(OpenDRIVE))
    text_file.close()

def gen_empty_junction(OpenDRIVE):
    # # Junction
    junction                     = SubElement(OpenDRIVE, "junction")
    junction_connection          = SubElement(junction, "connection")
    junction_connection_laneLink = SubElement(junction_connection, "laneLink")
    junction_priority            = SubElement(junction, "priority")
    junction_controller          = SubElement(junction, "controller")

def check_width_border(OpenDRIVE):
    # check validity of width vs border
    for RoadElement in OpenDRIVE.findall('./road[@id]'):
        road_id = RoadElement.attrib['id']
        sh_ln = RoadElement.findall("./lanes/laneSection//lane")

        for sh_ln_id in range(0, len(sh_ln)):
            sh_w = sh_ln[sh_ln_id].find("width")
            sh_b = sh_ln[sh_ln_id].find("border")

            if (sh_w is not None and
                        sh_b is not None):
                if (len(sh_w.attrib['a']) == 1 and
                            len(sh_b.attrib['a']) == 1):
                    print ("Error Must choose width OR border")
                elif (len(sh_w.attrib['a']) == 0 and
                              len(sh_b.attrib['a']) == 1):
                    sh_ln[sh_ln_id].remove(sh_w)
                elif (len(sh_w.attrib['a']) == 1 and
                              len(sh_b.attrib['a']) == 0):
                    sh_ln[sh_ln_id].remove(sh_b)
                else:
                    print ("Missing width or border")
            else:
                pass
    return OpenDRIVE

def sequence_lanes(OpenDRIVE):
    # reorganize sequence for lanes
    for RoadElement in OpenDRIVE.findall('./road[@id]'):
        road_id = RoadElement.attrib['id']
        sh_ls = RoadElement.findall("./lanes/laneSection")
        she = RoadElement.findall("./lanes/laneSection/left")
        for she_id in range(0, len(she)):
            new_she = copy.deepcopy(she[she_id])
            sh_ls[she_id].remove(she[she_id])
            sh_ls[she_id].insert(0, new_she)
    return OpenDRIVE

def sequence_objects(OpenDRIVE):
    # reorganize sequence for objects object
    for RoadElement in OpenDRIVE.findall('./road[@id]'):
        road_id = RoadElement.attrib['id']
        sh_oo = RoadElement.findall("./objects/object")

        she = RoadElement.findall("./objects/object/repeat")
        for she_id in range(0, len(she)):
            new_she = copy.deepcopy(she[she_id])
            sh_oo[she_id].remove(she[she_id])
            sh_oo[she_id].insert(0, new_she)

        she = RoadElement.findall("./objects/object/outline")
        for she_id in range(0, len(she)):
            new_she = copy.deepcopy(she[she_id])
            sh_oo[she_id].remove(she[she_id])
            sh_oo[she_id].insert(1, new_she)

        she = RoadElement.findall("./objects/object/material")
        for she_id in range(0, len(she)):
            new_she = copy.deepcopy(she[she_id])
            sh_oo[she_id].remove(she[she_id])
            sh_oo[she_id].insert(2, new_she)

        she = RoadElement.findall("./objects/object/validity")
        for she_id in range(0, len(she)):
            new_she = copy.deepcopy(she[she_id])
            sh_oo[she_id].remove(she[she_id])
            sh_oo[she_id].insert(3, new_she)

        she = RoadElement.findall("./objects/object/parkingSpace")
        for she_id in range(0, len(she)):
            new_she = copy.deepcopy(she[she_id])
            sh_oo[she_id].remove(she[she_id])
            sh_oo[she_id].insert(4, new_she)
    return OpenDRIVE

def sequence_signals(OpenDRIVE):
    # reorganize sequence for signals signal
    for RoadElement in OpenDRIVE.findall('./road[@id]'):
        road_id = RoadElement.attrib['id']
        sh_oo = RoadElement.findall("./signals/signal")

        she = RoadElement.findall("./signals/signal/validity")
        for she_id in range(0, len(she)):
            new_she = copy.deepcopy(she[she_id])
            sh_oo[she_id].remove(she[she_id])
            sh_oo[she_id].insert(0, new_she)

        she = RoadElement.findall("./signals/signal/dependency")
        for she_id in range(0, len(she)):
            new_she = copy.deepcopy(she[she_id])
            sh_oo[she_id].remove(she[she_id])
            sh_oo[she_id].insert(1, new_she)

    return OpenDRIVE


def post_fill_elevation(OpenDRIVE):
    # post fill elevationProfile
    for RoadElement in OpenDRIVE.findall('./road[@id]'):
        sh_ln = RoadElement.find("elevationProfile")
        if sh_ln is None:
            sh_ln = SubElement(RoadElement,"elevationProfile")
            she = SubElement(sh_ln, "elevation")
        else:
            she = sh_ln.find("elevation")

        she.set("s", "0.0000000000000000e+00")
        she.set("a", "0.0000000000000000e+00")
        she.set("b", "0.0000000000000000e+00")
        she.set("c", "0.0000000000000000e+00")
        she.set("d", "0.0000000000000000e+00")


        new_she = copy.deepcopy(sh_ln)
        RoadElement.remove(sh_ln)
        RoadElement.insert(3, new_she)

    return OpenDRIVE

def post_fill_elevationProfile(OpenDRIVE):
    # post fill elevationProfile
    for RoadElement in OpenDRIVE.findall('./road[@id]'):
        sh_ln = RoadElement.find("lateralProfile")
        if sh_ln is None:
            sh_ln = SubElement(RoadElement,"lateralProfile")
            she = SubElement(sh_ln, "superelevation")
        else:
            she = sh_ln.find("superelevation")

        she.set("s", "0.0000000000000000e+00")
        she.set("a", "0.0000000000000000e+00")
        she.set("b", "0.0000000000000000e+00")
        she.set("c", "0.0000000000000000e+00")
        she.set("d", "0.0000000000000000e+00")

        new_she = copy.deepcopy(sh_ln)
        RoadElement.remove(sh_ln)
        RoadElement.insert(4, new_she)
    return OpenDRIVE


def post_fill_geometry_line(OpenDRIVE):
    for RoadElement in OpenDRIVE.findall('./road[@id]'):
        sh_ln = RoadElement.find('planView')
    for sh_geom in sh_ln.findall('geometry'):
            if (sh_geom is not None and len(sh_geom.getchildren())==0 and
		len(sh_geom.attrib) == 5):
                sh_ln = SubElement(sh_geom,"line")
    return OpenDRIVE


#def convert_double(data):
    #dbl_vars = ['s', 'x', 'y', 't', 'hdg', 'length', 'curvEnd', 'curvStart', 'a', 'b', 'c', 'd', 'curvature',
    #            'aV', 'bV', 'cV', 'dV', ]
    # for idx in range(0, data.shape[0]):
    #     row = data[idx,:]
    #     chk = np.in1d(row[-2], dbl_vars)
    #     if (len(chk) > 0):
    #         if str(row[10]).isdigit():
    #             data[idx,10] = '%.16e' % float(row[10])

    #return data

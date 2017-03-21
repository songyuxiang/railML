import sys
from PyQt5.Qt import *
import mainwindow
from syx import *
from write_odr6 import *
import subprocess
class mainwindow(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.initUI()
        self.roadLength = 0
        self.currentRoadName = self.lineEdit_roadName.text()
        self.currentRoadID = self.lineEdit_roadID.text()
        self.currentJunctionID = self.lineEdit_currentJunctionId.text()
        self.currentRoadType = self.comboBox_roadType.currentText()
        self.speedLimit = self.lineEdit_speed.text()
        self.predecessorType = self.comboBox_predecessorType.currentText()
        self.predecessorContactPoint = self.comboBox_predecessorContactPoint.currentText()
        self.predecessorID = self.lineEdit_predecessorId.text()
        self.successorType = self.comboBox_successorType.currentText()
        self.successorContactPoint = self.comboBox_successorContactPoint.currentText()
        self.successorID = self.lineEdit_successorId.text()
        self.point3D = []
        self.pointX = []
        self.pointY = []
        self.pointZ = []
        self.allLanesInfo = []
        self.sectionPoint = []
        self.size = 0
        self.pointGap = 0.1
        self.curvePointNumber = 500
        self.tolerance = 0.01
        self.geometryInfo=[]
        self.elevationInfo=[]
        self.sectionInfo=[]
        self.roadInfo=[]
        self.allRoadsInfo={}
        self.listViewModel=QStandardItemModel(1000,1)
    def initUI(self):
        self.pushButton_input.clicked.connect(self.importLaneInfo)
        self.pushButton_export.clicked.connect(self.export)
        self.pushButton_point3D.clicked.connect(self.importPoint3D)
        self.pushButton_compute.clicked.connect(self.compute)
        self.listView_allRoads.clicked.connect(self.loadRoadInfo)

# press escape to quit
    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Escape:
            self.close()



# import 3D points for pointX,pointY,pointZ,point3D
    def importPoint3D(self):
        filename, _ = QFileDialog.getOpenFileName(self, "open 3D points", "", "Text file(*.txt);;All File(*.*)")
        self.point3D = []
        with open(filename, 'r') as file:
            data_point3D = file.readlines()
        for line in data_point3D:
            line = line.split(',')
            self.pointX.append(float(line[0]))
            self.pointY.append(float(line[1]))
            self.pointZ.append(float(line[2]))
            self.point3D.append([float(line[0]), float(line[1]), float(line[2])])
        self.showInEditor(self.point3D)
        self.size = len(self.point3D)

# import lanes section info from a exported 3 levels python list [[[],[]],[[],[]]]
    def importLaneInfo(self):
        filename, _ = QFileDialog.getOpenFileName(self, "open 3D points", "", "Text file(*.txt);;All File(*.*)")
        self.allLanesInfo = ReadList3L(filename)
        self.showInEditor(self.allLanesInfo)

# find section points from lanes' infomation
    def getSectionPoints(self):
        for i in range(len(self.allLanesInfo) - 1):
            if not compareLaneSection(self.allLanesInfo[i], self.allLanesInfo[i + 1], False):
                self.sectionPoint.append([i, self.point3D[i][0], self.point3D[i][1], self.point3D[i][2]])
        self.showInEditor(self.sectionPoint, title="Section Point")

    def showInEditor(self, data, title=""):
        self.textEdit_input.setText(title)
        for i in data:
            self.textEdit_input.append(str(i))
    def computeGeometry(self):
        # compute geometry
        start = 0
        end = self.size
        gap_polyline = 10
        gap_circle = 10
        gap_line = 10
        geometryInfo = []
        cumulateLength = 0
        while self.size - start >= 2:
            hdg = getOrientation(self.pointX[start + 1] - self.pointX[start],
                                 self.pointY[start + 1] - self.pointY[start])
            x, y = rotateAndTranslate(self.pointX[start:end], self.pointY[start:end], -hdg, self.pointX[start],
                                      self.pointY[start])
            if len(x) >= 4:
                para_polyline, gap_polyline = getPolylineModel(x, y)
            if len(x) >= 3:
                para_circle, gap_circle = getCircleModel(x, y, False)
            gap_line = getLineModel(x, y)

            if gap_polyline > self.tolerance and gap_line > self.tolerance and gap_circle > self.tolerance:
                end = end - 1
                continue
            if gap_polyline < gap_line and gap_polyline < gap_circle:
                polylineLength = (len(x) - 1) * self.pointGap
                geometryInfo.append(
                    self.formatData(n1="road", n2="planView", n3="geometry", att="s", value=cumulateLength))
                cumulateLength = cumulateLength + polylineLength
                geometryInfo.append(
                    self.formatData(n1="road", n2="planView", n3="geometry", att="x", value=self.pointX[start]))
                geometryInfo.append(
                    self.formatData(n1="road", n2="planView", n3="geometry", att="y", value=self.pointY[start]))
                geometryInfo.append(self.formatData(n1="road", n2="planView", n3="geometry", att="hdg", value=hdg))
                geometryInfo.append(
                    self.formatData(n1="road", n2="planView", n3="geometry", att="length", value=polylineLength))
                geometryInfo.append(
                    self.formatData(n1="road", n2="planView", n3="geometry", n4="poly3", att="a", value=0))
                geometryInfo.append(
                    self.formatData(n1="road", n2="planView", n3="geometry", n4="poly3", att="b", value=0))
                geometryInfo.append(self.formatData(n1="road", n2="planView", n3="geometry", n4="poly3", att="c",
                                                    value=para_polyline[1]))
                geometryInfo.append(self.formatData(n1="road", n2="planView", n3="geometry", n4="poly3", att="d",
                                                    value=para_polyline[0]))
                start = end - 1
                end = self.size
            elif gap_circle < gap_polyline and gap_circle < gap_line:
                polylineLength = (len(x) - 1) * self.pointGap
                geometryInfo.append(
                    self.formatData(n1="road", n2="planView", n3="geometry", att="s", value=cumulateLength))
                cumulateLength = cumulateLength + polylineLength

                geometryInfo.append(
                    self.formatData(n1="road", n2="planView", n3="geometry", att="x", value=self.pointX[start]))
                geometryInfo.append(
                    self.formatData(n1="road", n2="planView", n3="geometry", att="y", value=self.pointY[start]))
                geometryInfo.append(self.formatData(n1="road", n2="planView", n3="geometry", att="hdg", value=hdg))
                geometryInfo.append(
                    self.formatData(n1="road", n2="planView", n3="geometry", att="length", value=polylineLength))
                geometryInfo.append(self.formatData(n1="road", n2="planView", n3="geometry", n4="arc", att="curvature",
                                                    value=1 / para_circle[2]))
                start = end - 1
                end = self.size
            elif gap_line < gap_polyline and gap_line < gap_circle:
                polylineLength = (len(x) - 1) * self.pointGap
                geometryInfo.append(
                    self.formatData(n1="road", n2="planView", n3="geometry", att="s", value=cumulateLength))
                cumulateLength = cumulateLength + polylineLength

                geometryInfo.append(
                    self.formatData(n1="road", n2="planView", n3="geometry", att="x", value=self.pointX[start]))
                geometryInfo.append(
                    self.formatData(n1="road", n2="planView", n3="geometry", att="y", value=self.pointY[start]))
                geometryInfo.append(self.formatData(n1="road", n2="planView", n3="geometry", att="hdg", value=hdg))
                geometryInfo.append(
                    self.formatData(n1="road", n2="planView", n3="geometry", att="length", value=polylineLength))
                start = end - 1
                end = self.size
        self.geometryInfo = geometryInfo
    def computeSection(self):
        laneSectionNb = len(self.sectionPoint) + 1
        sectionStartPos = 0
        sectionS = 0
        sectionInfo = []
        for i in range(laneSectionNb):
            try:
                sectionPts = self.point3D[sectionStartPos:self.sectionPoint[i][0]]
                sectionLanesInfo = self.allLanesInfo[sectionStartPos:self.sectionPoint[i][0]]
            except IndexError:
                sectionPts = self.point3D[sectionStartPos:self.size]
                sectionLanesInfo = self.allLanesInfo[sectionStartPos:self.size]
            s = len(sectionPts) * self.pointGap
            try:
                sectionStartPos = self.sectionPoint[i][0]
            except IndexError:
                sectionStartPos = self.size

            lane_section_s = sectionS
            lane_section_singleSide = ""
            sectionInfo.append(self.formatData(n1="road", n2="lanes", n3="laneSection", att="s", value=lane_section_s))

            if checkSingleSide(sectionLanesInfo[0]):
                lane_section_singleSide = "true"
            else:
                lane_section_singleSide = "false"

            sectionInfo.append(self.formatData(n1="road", n2="lanes", n3="laneSection", att="singleSide",
                                               value=lane_section_singleSide))

            allPass = True
            startPos = 0
            sectionSize = len(sectionLanesInfo)
            endPos = sectionSize + 1
            interS = sectionS
            while startPos < sectionSize - 1:
                lane_id_right = 0
                lane_id_left = 0
                lane_parameter_right = [0, 0, 0, 0]
                lane_parameter_left = [0, 0, 0, 0]
                parameters = []
                distantAllLanes = analyseSectionLanes(sectionLanesInfo[startPos:endPos])
                for lane in distantAllLanes:

                    a, b, c, d, s, gap = getSectionGeometry(lane[1:])
                    parameters.append([a, b, c, d, s, gap])
                    if gap > 0.02:
                        allPass = False
                if allPass == False:
                    endPos = endPos - 1
                    allPass = True
                    continue
                else:
                    for i in range(len(parameters)):

                        if distantAllLanes[i][0] == "center":
                            center_lane_id = 0
                            center_lane_type = sectionLanesInfo[0][i][5]
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="center", n5="lane",
                                                att="type",
                                                value=center_lane_type))
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="center", n5="lane",
                                                att="id",
                                                value=center_lane_id))
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="center", n5="lane",
                                                att="level",
                                                value="true"))
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="center", n5="lane",
                                                n6="link", n7="predecessor",
                                                att="id",
                                                value=0))
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="center", n5="lane",
                                                n6="link", n7="successor",
                                                att="id",
                                                value=0))

                            center_lane_roadmark_type = sectionLanesInfo[0][i][3]
                            if center_lane_roadmark_type != "":
                                center_lane_roadmark_offset = 0
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="center", n5="lane",
                                                    n6="roadMark",
                                                    att="sOffset",
                                                    value=center_lane_roadmark_offset))
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="center", n5="lane",
                                                    n6="roadMark",
                                                    att="type",
                                                    value=center_lane_roadmark_type))

                                center_lane_roadmark_weight = sectionLanesInfo[0][i][4]
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="center", n5="lane",
                                                    n6="roadMark",
                                                    att="weight",
                                                    value=center_lane_roadmark_weight))

                                # to add#
                                center_lane_roadmark_color = "standard"
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="center", n5="lane",
                                                    n6="roadMark",
                                                    att="color",
                                                    value=center_lane_roadmark_color))
                                center_lane_roadmark_material = "standard"
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="center", n5="lane",
                                                    n6="roadMark",
                                                    att="material",
                                                    value=center_lane_roadmark_material))

                                center_lane_roadmark_width = float(sectionLanesInfo[0][i][2]) / 1000
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="center", n5="lane",
                                                    n6="roadMark",
                                                    att="width",
                                                    value=center_lane_roadmark_width))
                                center_lane_roadmark_laneChange = "none"
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="center", n5="lane",
                                                    n6="roadMark",
                                                    att="laneChange",
                                                    value=center_lane_roadmark_laneChange))
                                center_lane_roadmark_height = 0
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="center", n5="lane",
                                                    n6="roadMark",
                                                    att="height",
                                                    value=center_lane_roadmark_height))
                        if distantAllLanes[i][0] == "right":
                            lane_id_right = lane_id_right - 1
                            right_lane_type = sectionLanesInfo[0][i][5]
                            right_lane_id = lane_id_right
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                att="type",
                                                value=right_lane_type))
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                att="id",
                                                value=right_lane_id))
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                att="level",
                                                value="true"))

                            right_lane_predecessor_id = right_lane_id
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                n6="link", n7="predecessor",
                                                att="id",
                                                value=right_lane_predecessor_id))
                            right_lane_successor_id = right_lane_id
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                n6="link", n7="successor",
                                                att="id",
                                                value=right_lane_successor_id))

                            right_lane_width_sOffset = 0
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                n6="width",
                                                att="sOffset",
                                                value=right_lane_width_sOffset))
                            right_lane_width_a = parameters[i][0] - lane_parameter_right[0]
                            right_lane_width_b = parameters[i][1] - lane_parameter_right[1]
                            right_lane_width_c = parameters[i][2] - lane_parameter_right[2]
                            right_lane_width_d = parameters[i][3] - lane_parameter_right[3]
                            lane_parameter_right[0] = parameters[i][0]
                            lane_parameter_right[1] = parameters[i][1]
                            lane_parameter_right[2] = parameters[i][2]
                            lane_parameter_right[3] = parameters[i][3]
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                n6="width",
                                                att="a",
                                                value=right_lane_width_a))
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                n6="width",
                                                att="b",
                                                value=right_lane_width_b))
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                n6="width",
                                                att="c",
                                                value=right_lane_width_c))
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                n6="width",
                                                att="d",
                                                value=right_lane_width_d))

                            right_lane_roadmark_type = sectionLanesInfo[0][i][3]
                            if right_lane_roadmark_type != "":
                                right_lane_roadmark_offset = 0
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                    n6="roadMark",
                                                    att="sOffset",
                                                    value=right_lane_roadmark_offset))
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                    n6="roadMark",
                                                    att="type",
                                                    value=right_lane_roadmark_type))

                                right_lane_roadmark_weight = sectionLanesInfo[0][i][4]
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                    n6="roadMark",
                                                    att="weight",
                                                    value=right_lane_roadmark_weight))

                                right_lane_roadmark_color = "standard"
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                    n6="roadMark",
                                                    att="color",
                                                    value=right_lane_roadmark_color))

                                right_lane_roadmark_material = "standard"
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                    n6="roadMark",
                                                    att="material",
                                                    value=right_lane_roadmark_material))

                                right_lane_roadmark_width = float(sectionLanesInfo[0][i][2]) / 1000
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                    n6="roadMark",
                                                    att="width",
                                                    value=right_lane_roadmark_width))

                                right_lane_roadmark_laneChange = "none"
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                    n6="roadMark",
                                                    att="laneChange",
                                                    value=right_lane_roadmark_laneChange))

                                right_lane_roadmark_height = 0
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="right", n5="lane",
                                                    n6="roadMark",
                                                    att="height",
                                                    value=right_lane_roadmark_height))

                        if distantAllLanes[i][0] == "left":
                            lane_id_left = lane_id_left + 1
                            left_lane_type = sectionLanesInfo[0][i][5]
                            left_lane_id = lane_id_left
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                att="type",
                                                value=left_lane_type))
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                att="id",
                                                value=left_lane_id))
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                att="level",
                                                value="true"))
                            left_lane_predecessor_id = left_lane_id
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                n6="link", n7="predecessor",
                                                att="id",
                                                value=left_lane_predecessor_id))

                            left_lane_successor_id = left_lane_id
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                n6="link", n7="successor",
                                                att="id",
                                                value=left_lane_successor_id))

                            left_lane_width_sOffset = 0
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                n6="width",
                                                att="sOffset",
                                                value=left_lane_width_sOffset))

                            left_lane_width_a = parameters[i][0] - lane_parameter_left[0]
                            left_lane_width_b = parameters[i][1] - lane_parameter_left[1]
                            left_lane_width_c = parameters[i][2] - lane_parameter_left[2]
                            left_lane_width_d = parameters[i][3] - lane_parameter_left[3]
                            lane_parameter_left[0] = parameters[i][0]
                            lane_parameter_left[1] = parameters[i][1]
                            lane_parameter_left[2] = parameters[i][2]
                            lane_parameter_left[3] = parameters[i][3]
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                n6="width",
                                                att="a",
                                                value=left_lane_width_a))
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                n6="width",
                                                att="b",
                                                value=left_lane_width_b))
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                n6="width",
                                                att="c",
                                                value=left_lane_width_c))
                            sectionInfo.append(
                                self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                n6="width",
                                                att="d",
                                                value=left_lane_width_d))

                            # to add
                            left_lane_roadmark_type = sectionLanesInfo[0][i][3]
                            if left_lane_roadmark_type != "":
                                left_lane_roadmark_offset = 0
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                    n6="roadMark",
                                                    att="sOffset",
                                                    value=left_lane_roadmark_offset))
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                    n6="roadMark",
                                                    att="type",
                                                    value=left_lane_roadmark_type))

                                left_lane_roadmark_weight = sectionLanesInfo[0][i][4]
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                    n6="roadMark",
                                                    att="weight",
                                                    value=left_lane_roadmark_weight))

                                left_lane_roadmark_color = "standard"
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                    n6="roadMark",
                                                    att="color",
                                                    value=left_lane_roadmark_color))

                                left_lane_roadmark_material = "standard"
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                    n6="roadMark",
                                                    att="material",
                                                    value=left_lane_roadmark_material))
                                left_lane_roadmark_width = float(sectionLanesInfo[0][i][2]) / 1000

                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                    n6="roadMark",
                                                    att="width",
                                                    value=left_lane_roadmark_width))
                                left_lane_roadmark_laneChange = "none"
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                    n6="roadMark",
                                                    att="laneChange",
                                                    value=left_lane_roadmark_laneChange))

                                left_lane_roadmark_height = 0
                                sectionInfo.append(
                                    self.formatData(n1="road", n2="lanes", n3="laneSection", n4="left", n5="lane",
                                                    n6="roadMark",
                                                    att="height",
                                                    value=left_lane_roadmark_height))
                    startPos = endPos - 1
                    interS = interS + s

                    if endPos < sectionSize + 1:
                        endPos = sectionSize + 1
                        sectionInfo.append(
                            self.formatData(n1="road", n2="lanes", n3="laneSection",
                                            att="s",
                                            value=interS))
                        sectionInfo.append(
                            self.formatData(n1="road", n2="lanes", n3="laneSection",
                                            att="singleSide",
                                            value=lane_section_singleSide))
                        allPass = True
            sectionS = sectionS + s
        self.sectionInfo = sectionInfo
    def computeElevation(self):
        start = 0
        end = self.size
        gap_polyline = 10
        elevationInfo = []
        cumulateLength = 0
        while self.size - start >= 2:
            z=self.pointZ[start:end]
            x=linspace(0,(end-start-1)*self.pointGap,end-start)
            if len(x) >= 4:
                para_polyline, gap_polyline = getPolylineModel(x, z)
            else:
                print("elevation error")

            if gap_polyline > self.tolerance:
                end = end - 1
                continue
            else:
                polylineLength = (len(x) - 1) * self.pointGap
                elevationInfo.append(
                    self.formatData(n1="road", n2="elevationProfile", n3="elevation", att="s", value=cumulateLength))
                cumulateLength = cumulateLength + polylineLength

                elevationInfo.append(
                    self.formatData(n1="road", n2="elevationProfile", n3="elevation", att="a", value=para_polyline[3]))
                elevationInfo.append(
                    self.formatData(n1="road", n2="elevationProfile", n3="elevation", att="b", value=para_polyline[2]))
                elevationInfo.append(self.formatData(n1="road", n2="elevationProfile", n3="elevation",att="c",
                                                    value=para_polyline[1]))
                elevationInfo.append(self.formatData(n1="road", n2="elevationProfile", n3="elevation",att="d",
                                                    value=para_polyline[0]))
                start = end - 1
                end = self.size
        self.elevationInfo=elevationInfo
    def updateListWidget(self):
        rowIndex=0
        self.allRoadsInfo[self.currentRoadID] = [self.roadInfo, self.geometryInfo, self.sectionInfo]

        for i in self.allRoadsInfo.keys():
            index = self.listViewModel.index(rowIndex,0)
            self.listViewModel.setData(index,i)
            rowIndex=rowIndex+1

        self.listView_allRoads.setModel(self.listViewModel)
    def compute(self):
        self.getSectionPoints()
        self.roadLength = (len(self.point3D) - 1) * self.pointGap
        self.updateRoadInfo()
        self.computeGeometry()
        self.computeElevation()
        self.computeSection()
        self.previewInfo()
        self.updateListWidget()
    def updateRoadInfo(self):
        self.currentRoadName = self.lineEdit_roadName.text()
        self.roadLength=(len(self.allLanesInfo)-1)*self.pointGap
        self.currentRoadID = self.lineEdit_roadID.text()
        self.currentJunctionID = self.lineEdit_currentJunctionId.text()
        self.currentRoadType = self.comboBox_roadType.currentText()
        self.speedLimit = self.lineEdit_speed.text()
        self.predecessorType = self.comboBox_predecessorType.currentText()
        self.predecessorContactPoint = self.comboBox_predecessorContactPoint.currentText()
        self.predecessorID = self.lineEdit_predecessorId.text()
        self.successorType = self.comboBox_successorType.currentText()
        self.successorContactPoint = self.comboBox_successorContactPoint.currentText()
        self.successorID = self.lineEdit_successorId.text()
        self.roadInfo=[]
        self.roadInfo.append(self.formatData(n1="road", att="name", value=self.currentRoadName))
        self.roadInfo.append(self.formatData(n1="road", att="id", value=self.currentRoadID))
        self.roadInfo.append(self.formatData(n1="road", att="junction", value=self.currentJunctionID))
        self.roadInfo.append(self.formatData(n1="road", att="length", value=str(self.roadLength)))
        self.roadInfo.append(self.formatData(n1="road", n2="type", att="type", value=self.currentRoadType))
        self.roadInfo.append(self.formatData(n1="road", n2="type", att="s", value="0"))
        self.roadInfo.append(
            self.formatData(n1="road", n2="type", n3="speed", att="max", value=self.speedLimit))
        self.roadInfo.append(self.formatData(n1="road", n2="type", n3="speed", att="unit", value="m/s"))
        self.roadInfo.append(
            self.formatData(n1="road", n2="link", n3="predecessor", att="elementType", value=self.predecessorType))
        self.roadInfo.append(
            self.formatData(n1="road", n2="link", n3="predecessor", att="elementId", value=self.predecessorID))
        self.roadInfo.append(self.formatData(n1="road", n2="link", n3="predecessor", att="contactPoint",
                                                     value=self.predecessorContactPoint))
        self.roadInfo.append(
            self.formatData(n1="road", n2="link", n3="successor", att="elementType", value=self.successorType))
        self.roadInfo.append(
            self.formatData(n1="road", n2="link", n3="successor", att="elementId", value=self.successorID))
        self.roadInfo.append(
            self.formatData(n1="road", n2="link", n3="successor", att="contactPoint", value=self.successorContactPoint))
    def formatData(self, n1="", n2="", n3="", n4="", n5="", n6="", n7="", n8="", att="", value=""):
        out = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|" % (self.currentRoadID, n1, n2, n3, n4, n5, n6, n7, n8, att, value)
        return out
    def loadRoadInfo(self,index):
        id=self.listViewModel.data(index)
        if id!="":
            self.displayAllRoadDictionary(self.allRoadsInfo[id])
    def displayAllRoadDictionary(self,list):
        for i in list:
            for j in i:
                self.textEdit_input.append(j)
    def previewInfo(self):
        self.textEdit_input.setText("")
        for i in self.roadInfo:
            self.textEdit_input.append(i)
        for i in self.geometryInfo:
            self.textEdit_input.append(i)
        for i in self.elevationInfo:
            self.textEdit_input.append(i)
        for i in self.sectionInfo:
            self.textEdit_input.append(i)

    def export(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save file", "", "CSV file(*.csv);;All File(*.*)")
        if (filename.find(".csv")<0):
            filename=filename+".csv"
        file = QFile(filename)
        if file.open(QFile.WriteOnly):
            out = QTextStream(file)
            for i in self.roadInfo:
                out<<i<<"\n"
            for i in self.geometryInfo:
                out<<i<<"\n"
            for i in self.elevationInfo:
                out<<i<<"\n"
            for i in self.sectionInfo:
                out<<i<<"\n"
            file.close()
        subprocess.call(["odrviewer"])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = mainwindow()
    form.show()
    app.exec_()

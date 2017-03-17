import sys
from PyQt5.Qt import *
import mainwindow
from syx import *


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
        self.roadInfo=[]

    def initUI(self):
        self.pushButton_input.clicked.connect(self.importLaneInfo)
        self.pushButton_preview.clicked.connect(self.previewInfo)
        self.pushButton_export.clicked.connect(self.export)
        self.pushButton_point3D.clicked.connect(self.importPoint3D)
        self.pushButton_compute.clicked.connect(self.compute)

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Escape:
            self.close()

    def importPoint3D(self):
        filename, _ = QFileDialog.getOpenFileName(self, "open 3D points", "", "All File(*.*)")
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

    def importLaneInfo(self):
        filename, _ = QFileDialog.getOpenFileName(self, "open 3D points", "", "All File(*.*)")
        self.allLanesInfo = ReadList3L(filename)
        self.showInEditor(self.allLanesInfo)

    def getSectionPoints(self):
        for i in range(len(self.allLanesInfo) - 1):
            if not compareLaneSection(self.allLanesInfo[i], self.allLanesInfo[i + 1], False):
                self.sectionPoint.append([i, self.point3D[i][0], self.point3D[i][1], self.point3D[i][2]])
        self.showInEditor(self.sectionPoint, title="Section Point")

    def showInEditor(self, data, title=""):
        self.textEdit_input.setText(title)
        for i in data:
            self.textEdit_input.append(str(i))

    def compute(self):
        self.getSectionPoints()
        self.roadLength = (len(self.point3D) - 1) * self.pointGap
        start = 0
        end = self.size
        gap_polyline = 10
        gap_circle = 10
        gap_line = 10
        geometryInfo = []
        cumulateLength = 0

        while self.size - start >= 2:
            print(start, end)
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
        self.geometryInfo=geometryInfo

    def updateRoadInfo(self):
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

    def previewInfo(self):
        self.updateRoadInfo()
        self.textEdit_preview.setText("")
        for i in self.roadInfo:
            self.textEdit_preview.append(i)
        for i in self.geometryInfo:
            self.textEdit_preview.append(i)

    def export(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save file", "", "All File(*.*)")
        file = QFile(filename)
        if file.open(QFile.ReadWrite):
            out = QTextStream(file)
            out << self.textEdit_preview.toPlainText()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = mainwindow()
    form.show()
    app.exec_()

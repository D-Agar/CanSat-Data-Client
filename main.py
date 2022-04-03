import sys
import io 
from textwrap import fill
import time
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import pyqtgraph as pg
import numpy as np
import dataWriter
import portCtrl
# import interface
from interface import *

# Main window class
class MainWindow(QMainWindow):
    def __init__(self, dw, ser):
        QMainWindow.__init__(self)
        pg.setConfigOption('background', (30, 31, 38))
        # loads ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.offset = None

        # hides the sidebar
        self.hiddenSidebar = True

        # Default open window - no sidebar, all graphs
        self.ui.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.ui.sidebar.setVisible(False)
        self.ui.stackedWidget.setCurrentIndex(0)


        # Sidebar controlled by menu button
        self.ui.menuBtn.clicked.connect(lambda: self.toggleSidebar())

        # data save buttons with their assigned use
        self.ui.startSaveBtn.clicked.connect(lambda: dw.start())
        self.ui.stopSaveBtn.clicked.connect(lambda: dw.stop())

        # Sidebarbuttons connect to the stacked widget
        self.ui.optionsAllBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.optionsAirBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.optionsTempBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.optionHumBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))
        self.ui.optionsAltBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(4))
        self.ui.optionsAccBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(5))
        self.ui.optionsVelBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(6))
        self.ui.optionsGyroBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(7))
        self.ui.optionsLocBtn.clicked.connect(lambda: self.showLocation())

        # all clear graph buttons will clear graph (if you couldn't tell)
        self.ui.clearGraphsBtn.clicked.connect(lambda: self.clearGraphs())

        # coordinates
        self.longitude = 0
        self.lattitude = 0

        # Graphs
        # look at library pyqtgraph for details
        self.timeData = []

        # one line for the most recent data received - only shows last 30 pieces of data
        self.airLine = pg.PlotCurveItem()
        # this graph line shows all the data - only shown in the singular graph view
        self.allAirLine = pg.PlotCurveItem()
        # data for lines
        self.airData = []

        # repeated process for all data types
        self.tempLine = pg.PlotCurveItem()
        self.allTempLine = pg.PlotCurveItem()
        self.tempData = []

        self.humidLine = pg.PlotCurveItem()
        self.humidData = []

        self.altLine = pg.PlotCurveItem()
        self.allAltLine = pg.PlotCurveItem()
        self.altData = []

        self.accXLine = pg.PlotCurveItem()
        self.accXData = []

        self.accYLine = pg.PlotCurveItem()
        self.accYData = []

        self.accZLine = pg.PlotCurveItem()
        self.accZData = []

        self.velLine = pg.PlotCurveItem()
        self.allVelLine = pg.PlotCurveItem()
        self.velData = []

        self.pitchLine = pg.PlotCurveItem()
        self.pitchData = []

        self.rollLine = pg.PlotCurveItem()
        self.rollData = []

        self.yawLine = pg.PlotCurveItem()
        self.yawData = []

        self.tempLine = pg.PlotCurveItem()
        self.allTempLine = pg.PlotCurveItem()
        self.tempData = []

        # adds all lines to the corresponding graphs
        self.ui.allAirGraph.addItem(self.allAirLine)
        self.ui.allTempGraph.addItem(self.allTempLine)
        self.ui.allAltGraph.addItem(self.allAltLine)
        self.ui.allVelGraph.addItem(self.allVelLine)

        self.ui.airGraph.addItem(self.airLine)
        self.ui.xAccGraph.addItem(self.accXLine)
        self.ui.yAccGraph.addItem(self.accYLine)
        self.ui.zAccGraph.addItem(self.accZLine)
        self.ui.tempGraph.addItem(self.tempLine)
        self.ui.altGraph.addItem(self.altLine)
        self.ui.velGraph.addItem(self.velLine)
        self.ui.humidityGraph.addItem(self.humidLine)
        self.ui.pitchGraph.addItem(self.pitchLine)
        self.ui.rollGraph.addItem(self.rollLine)
        self.ui.yawGraph.addItem(self.yawLine)

        self.show()

    # Toggle sidebar
    def toggleSidebar(self):
        if self.hiddenSidebar:
            self.ui.verticalLayout_5.setContentsMargins(6, 0, 0, 0)
            self.ui.sidebar.setVisible(True)
            shownIcon = QIcon()
            shownIcon.addPixmap(QPixmap("Application/icons/arrow-left.svg"), QIcon.Normal, QIcon.Off)
            self.ui.menuBtn.setIcon(shownIcon)
            self.hiddenSidebar = not(self.hiddenSidebar)
        else:
            self.ui.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
            self.ui.sidebar.setVisible(False)
            hiddenIcon = QIcon()
            hiddenIcon.addPixmap(QPixmap("Application/icons/menu.svg"), QIcon.Normal, QIcon.Off)
            self.ui.menuBtn.setIcon(hiddenIcon)
            self.hiddenSidebar = not(self.hiddenSidebar)
        
    # function to update all graphs of a specific data type (updates both velocity graphs etc)
    def updateAllGraphs(self, allGraphLine, graphData):
        # for when all the graphs are showing, only show the last 30
        if len(self.timeData) >= 30:
            allGraphLine.setData(x=self.timeData[len(self.timeData)-30:], y=graphData[len(graphData)-30:])
        else:
            allGraphLine.setData(x=self.timeData, y=graphData)

    def updateGraph(self, graphLine, graphData):
        graphLine.setData(x=self.timeData, y=graphData)

    # procedure to clear graph
    def clearGraphs(self):
        # reset the timer
        ser.restartTime()

        # wipe all data for the graphs
        self.timeData.clear()
        for data in self.graphData:
            data.clear()

        # update allGraphs
        for i in range(0, len(self.allGraphs)):
            self.allGraphs[i].setData(x=self.timeData, y=self.graphData[i])

        # update every other graph
        for i in range(0, len(self.graphs)):
            self.graphs[i].setData(x=self.timeData, y=self.graphData[i])

    # function to show the map
    def showLocation(self):
        self.ui.stackedWidget.setCurrentIndex(8)
        # Map with folium
        coordinate = (self.longitude, self.lattitude)
        map = folium.Map(title = "Can Location", location=coordinate, zoom_start=15, tiles="OpenStreetMap")
        folium.CircleMarker(location=coordinate, radius=25, color="#3186cc", fill=True, fill_color="#3186cc").add_to(map)
        mdata = io.BytesIO()
        map.save(mdata, close_file = False)
        self.ui.locationWebView.setHtml(mdata.getvalue().decode())


    # Procedure to update everything
    def updateWin(self, writer, coms):
        self.allGraphs = [self.allAirLine, self.allAltLine, self.allTempLine, self.allVelLine]
        self.graphs = [self.airLine, self.altLine, self.tempLine, self.accXLine, self.accYLine, self.accZLine, self.velLine, self.humidLine, self.pitchLine, self.rollLine, self.yawLine]
        self.graphData = [self.airData, self.altData, self.tempData, self.accXData, self.accYData, self.accZData, self.velData, self.humidData, self.pitchData, self.rollData, self.yawData]
        # get data
        data = coms.read()
        try:
            # update x values
            self.timeData.append(data[0])

            # append all data to the corresponding array
            for i in range(0, len(self.graphData)):
                self.graphData[i].append(data[i+1])
            # update allgraphs
            for i in range(0, len(self.allGraphs)):
                self.updateAllGraphs(self.allGraphs[i], self.graphData[i])
            # update the other graphs
            for i in range(0, len(self.graphs)):
                self.updateGraph(self.graphs[i], self.graphData[i])

            # update location
            self.longitude = data[12]
            self.lattitude = data[13]

            # update signal strength
            self.ui.signalLbl.setText("Signal: " + data[14])
            writer.save(data)
        except IndexError:
            print("Give me a moment.")

# execute application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # object to handle writing the data
    dw = dataWriter.data_writer()
    # object to handle all serial data
    ser = portCtrl.port_Control()
    
    window = MainWindow(dw, ser)
    window.show()

    # Update the app every 0.5 second with data
    if ser.isOpen() or ser.isSimulated():
        timer = QTimer()
        timer.timeout.connect(lambda: window.updateWin(dw, ser))
        timer.start(500)

    sys.exit(app.exec_())

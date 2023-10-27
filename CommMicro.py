# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 09:33:21 2021

@author: bob

J Nelson 4 Apr 2022
new directory structure for data: 
$DATA_DIR_PATH/ACCL_LxB_CM00/yyyy/mm/dd/filename

add cm # to filename with -F switch

J Nelson 30 June 2022 
add print to elog button

"""
import subprocess
import sys
from datetime import datetime
from functools import partial
from os import makedirs, path, system

import numpy as np

# import physicselog
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from pydm import Display
from scipy.fftpack import fft, fftfreq
from model import Model

# FFt_math has utility functions
import FFt_math

BUFFER_LENGTH = 16384
DEFAULT_SAMPLING_RATE = 2000

LASTPATH = ""
DATA_DIR_PATH = "/u1/lcls/physics/rf_lcls2/microphonics/"


class MplCanvas(FigureCanvasQTAgg):
    """MPLCanvas is the class for the 'canvas' that plots are drawn on and then mapped to the ui
    They are Figure format described in matplotlib 2.2 documentation"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout="true")
        # one axis per layout
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MicDisp(Display):
    def __init__(self, parent=None, args=None, ui_filename="FFT_test.ui"):
        super(MicDisp, self).__init__(parent=parent, args=args, ui_filename=ui_filename)
        self.pathHere = path.dirname(sys.modules[self.__module__].__file__)
        self.model = Model()
        self.model.save_root_location = DATA_DIR_PATH
        self.model.save_location = LASTPATH

        def getPath(fileName):
            return path.join(self.pathHere, fileName)

        # save the date
        self.startd = datetime.now()
        # link up to the secondary display
        self.xfDisp = Display(ui_filename=getPath("MicPlot.ui"))
        self.checkboxes = [self.ui.cb1, self.ui.cb2, self.ui.cb3, self.ui.cb4]
        # create plot canvases and link to GUI elements
        self.topPlot = MplCanvas(self, width=20, height=40, dpi=100)
        self.botPlot = MplCanvas(self, width=20, height=40, dpi=100)
        self.initiailise_gui()
        self.connect_widgets()

    def initiailise_gui(self):
        self.xfDisp.ui.PlotTop.addWidget(self.topPlot)
        self.xfDisp.ui.PlotBot.addWidget(self.botPlot)
        self.model.user_arguments.num_buffers = self.ui.spinBox_buffers.value()
        self.model.user_arguments.decimation_amount = int(
            self.ui.comboBox_decimation.currentText()
        )
        self.ui.label_samplingrate.setNum(self.model.sampling_rate)
        self.ui.label_acq_time.setNum(self.model.acquire_time)
        # fill combo boxes
        for cmid in self.model.cryomodules:
            self.ui.CMComboBox.addItem(cmid)
        self.ui.CavComboBox.addItem("Cavities 1-4")
        self.ui.CavComboBox.addItem("Cavities 5-8")
        # start out with cavities 1-4 selected
        for idx, cb in enumerate(self.checkboxes):
            cb.setText(str(idx + 1))

        # check the first box so there's Something
        self.ui.cb1.setChecked(True)

    def connect_widgets(self):
        # call function setGOVal when strtBut is pressed
        self.ui.StrtBut.clicked.connect(
            partial(self.setGOVal, self.topPlot, self.botPlot)
        )
        # call function getOldData when OldDatBut is pressed
        self.ui.OldDatBut.clicked.connect(
            partial(self.getOldData, self.topPlot, self.botPlot)
        )
        # call function plotWindow when printPushButton is pressed
        self.xfDisp.ui.printPushButton.clicked.connect(self.plotWindow)
        # call function if cavity select combo box changes
        # call function if cavity select combo box changes
        self.ui.CavComboBox.activated.connect(self.ChangeCav)
        self.ui.CMComboBox.currentTextChanged.connect(self.update_cmid)
        self.ui.CavComboBox.currentIndexChanged.connect(self.update_cavity)
        self.ui.spinBox_buffers.valueChanged.connect(self.update_number_of_buffers)
        self.ui.comboBox_decimation.currentTextChanged.connect(
            self.update_decimation_amount
        )

    def update_number_of_buffers(self, value: int) -> None:
        self.model.user_arguments.num_buffers = value
        self.ui.label_acq_time.setNum(self.model.acquire_time)

    def update_decimation_amount(self, value: str) -> None:
        self.model.user_arguments.decimation_amount = int(value)
        self.ui.label_samplingrate.setNum(self.model.sampling_rate)
        self.ui.label_acq_time.setNum(self.model.acquire_time)

    def update_cmid(self, cmid: str) -> None:
        self.model.user_arguments.cryomodule_id = cmid
        self.model.user_arguments.linac = cmid.split(":")[1]
        self.model.user_arguments.cryomodule = cmid.split(":")[2]
        print(self.model.user_arguments.__dict__)

    def update_cavity(self, rack_index: int) -> None:
        #   This function responds to a user changing the cavity combo box
        #    from cavs 1-4 to cavs 5-8
        delta = 1
        if rack_index != 0:
            delta = 5
        for idx, cb in enumerate(self.checkboxes):
            cb.setText(str(idx + delta))
        self.model.user_arguments.rack = rack_index
        self.model.user_arguments.rack_delta = delta

    def ChangeCav(self):
        pass

    # This function takes given data (cavUno) and axis handle (tPlot) and calcu        # This function lates FFT and plots
    def FFTPlot(self, bPlot, cavUno):

        num_points = len(cavUno)
        sample_spacing = 1.0 / (
            DEFAULT_SAMPLING_RATE / int(self.ui.comboBox_decimation.currentText())
        )
        yf1 = fft(cavUno)
        xf = fftfreq(num_points, sample_spacing)[: num_points // 2]
        bPlot.axes.plot(xf, 2.0 / num_points * np.abs(yf1[0 : num_points // 2]))

    # This function gets info from the GUI, fills out LASTPATH,
    #  and returns liNac, cmNumStr, cavNumA, cavNumB

    def getUserVal(self):
        # I don't get why I need the global declaration
        global LASTPATH
        # load up cavNumStr ('1234') and cavNumList (['1','2','3','4'])

        # we only want to do this on button-click, not constantly.
        for idx, cb in enumerate(self.checkboxes):
            if cb.isChecked():
                cav_num = str(idx + self.model.user_arguments.rack_delta)
                self.model.user_arguments.cavity_number_str += cav_num
                self.model.user_arguments.cavity_number_list += cav_num
        self.model.set_new_location()
        LASTPATH = self.model.save_location
        return (
            self.model.user_arguments.linac,
            self.model.user_arguments.cryomodule,
            self.model.user_arguments.cavity_number_str,
        )

    # setGOVal is the response to the Get New Measurement button push
    # it takes GUI settings and calls python script to fetch the data
    #  then if Plotting is chosen, it calls getDataBack to make the plot

    def setGOVal(self, tPlot, bPlot):
        global LASTPATH
        return_code = 2

        self.model.set_new_location()
        LASTPATH = self.model.save_location
        # reads GUI inputs, fills out LASTPATH, and returns LxB, CMxx, and cav num
        linac, cmNumSt, cavNumStr = self.getUserVal()

        self.ui.label_message.setText("Data acquisition started\n")
        self.ui.label_message.repaint()

        resScrptSrce = (
            "/usr/local/lcls/package/lcls2_llrf/srf/software/res_ctl/res_data_acq.py"
        )

        # made the channel access spec for script call
        rack = self.ui.CavComboBox.currentIndex()
        AB = "AB"
        caCmd = "ca://ACCL:" + linac + ":" + str(cmNumSt) + "00:RES" + AB[rack] + ":"

        # LASTPATH in this case ultimately looks like:
        #  /u1/lcls/physics/rf_lcls2/microphonics/ACCL_L0B_0110/ACCL_L0B_0110_20220329_151328
        # /u1/lcls/physics/rf_lcls2/microphonics/ACCL_L0B_0100/yyyy/mm/dd/
        # LASTPATH =  path.join(morPath, botPath)
        # get LASTPATH from getUserVal()
        # makedirs(LASTPATH, exist_ok=True)

        # numbWaveF = str(self.model.user_arguments.num_buffers)

        # decimation_str = str(self.model.user_arguments.decimation_amount)

        # LASTPATH is the directory to put the datafile compliments of getUserVal()
        # Need to make output file name
        # Sergio had res_cav#_c#_yyyymmdd_hhmmss
        # Go to res_cm##_cav####_c#_yyyymmdd_hhmmss

        # timestamp = datetime.now().strftime("%Y%m%d" + "_" + "%H%M%S")
        # outFile = (
        #     "res_CM"
        #     + cmNumSt
        #     + "_cav"
        #     + cavNumStr
        #     + "_c"
        #     + str(numbWaveF)
        #     + "_"
        #     + timestamp
        # )
        self.model.set_new_outfile()
        self.filNam = self.model.outfile_name

        cmdList = [
            "python",
            resScrptSrce,
            "-D",
            str(LASTPATH),
            "-a",
            caCmd,
            "-wsp",
            str(self.model.user_arguments.decimation_amount),
            "-acav",
        ]
        for cav in cavNumStr:
            cmdList += cav
        cmdList += [
            "-ch",
            "DF",
            "-c",
            self.model.user_arguments.num_buffers,
            "-F",
            self.model.outfile_name,
        ]
        print(cmdList)
        self.model.construct_args()
        print("*** ", self.model.daq.args)

        try:
            self.ui.label_message.setText("Data acquisition started\n")
            self.ui.label_message.repaint()
            # process = subprocess.Popen(
            # cmdList, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            # )
            # out, err = process.communicate()
            # return_code = process.poll()
            # print("Return code {}".format(return_code))
            # out = out.decode(sys.stdin.encoding)
            # err = err.decode(sys.stdin.encoding)
            # print("Out: {}".format(out))
            self.model.run()
            self.ui.label_message.setText("{}".format(self.model.daq.output))
            self.ui.label_message.repaint()

            if self.model.daq.return_code == 0:
                self.ui.label_message.setText(
                    "File saved at \n" + self.model.save_location
                )
                self.ui.label_message.repaint()

                # user requesting that plots be made
                if self.ui.PlotComboBox.currentIndex() == 0:
                    try:
                        fname = path.join(LASTPATH, self.model.outfile_name)
                        if path.exists(fname):
                            self.getDataBack(fname, tPlot, bPlot)
                        else:
                            print("file doesnt exist {}".format(fname))
                    except:
                        print(
                            "No data file found in {} to make plots from".format(
                                self.model.save_location
                            )
                        )

            # unsuccess - if return_code != 0
            else:
                print("return code is not 0")

                e = subprocess.CalledProcessError(
                    return_code, cmdList, output=self.model.daq.output
                )
                e.stdout, e.stderr = self.model.daq.output, self.model.daq.error
                self.ui.label_message.setText(
                    "Call to microphonics script failed \nreturn code: {}\nstderr: {}".format(
                        return_code, str(e.stderr)
                    )
                )
                self.ui.label_message.repaint()
                print(
                    "stdout {0} stderr {1} return_code {2}".format(
                        e.stdout, e.stderr, return_code
                    )
                )
        except:
            print("You are exceptional")
            self.ui.label_message.setText("Call to microphonics script failed \n")
            self.ui.label_message.repaint()

        return ()

    # This function prompts the user for a file with data to plot
    #  then calls getDataBack to plot it to axes tPlot and bPlot
    #  The inputs of tPlot and bPlot are passed through to getDataBack

    def getOldData(self, tPlot, bPlot):
        global LASTPATH

        # clear message box in case there's anything still there
        self.ui.label_message.setText("Choose previous data file.")
        self.ui.label_message.adjustSize()

        # getUserVal sets LASTPATH from user input on the GUI
        liNac, cmNumSt, cavNumStr = self.getUserVal()

        # fileDial is fun to say
        fileDial = QFileDialog()
        fname_tuple = fileDial.getOpenFileName(
            None, "Open File?", self.model.save_location, ""
        )
        if fname_tuple[0] != "":
            self.getDataBack(fname_tuple[0], tPlot, bPlot)

        # get file name for elog entry title
        fnameParts = fname_tuple[0].split("/")
        for part in fnameParts:
            if part.startswith("res"):
                self.filNam = part

        return ()

    # This function eats the data from filename fname and plots
    #  a waterfall plot to axis tPlot and an FFT to axis bPlot

    def getDataBack(self, fname, tPlot, bPlot):

        cavDataList = []

        if path.exists(fname):
            dFDat, throwAway = FFt_math.readCavDat(fname)

            # this returns a list of lists of data values
            cavDataList = FFt_math.parseCavDat(dFDat)

            # figure out cavities from filename for legend
            fnameParts = fname.split("_")
            # find the fnamePart that starts with cav
            for part in fnameParts:
                if part.startswith("cav"):
                    cavnums = str(part[3:])

            tPlot.axes.cla()
            bPlot.axes.cla()
            leGend = []
            leGend2 = []

            for idx, cavData in enumerate(cavDataList):
                if len(cavData) > 0:
                    leGend.append("Cav" + cavnums[idx])
                    tPlot.axes.hist(cavData, bins=140, histtype="step", log="True")

                    leGend2.append("Cav" + cavnums[idx])
                    self.FFTPlot(bPlot, cavData)

            # put file name on the plot
            parts = fname.split("/")
            tPlot.axes.set_title(parts[-1], loc="left", fontsize="small")
            # tPlot.axes.set_xlim(-200, 200)
            tPlot.axes.set_ylim(bottom=1)
            tPlot.axes.set_xlabel("Detune (Hz)")
            tPlot.axes.set_ylabel("Counts")
            tPlot.axes.grid(True)
            tPlot.axes.legend(leGend)
            tPlot.draw_idle()

            bPlot.axes.set_xlim(0, 150)
            bPlot.axes.set_xlabel("Frequency (Hz)")
            bPlot.axes.set_ylabel("Relative Amplitude")
            bPlot.axes.grid(True)
            bPlot.axes.legend(leGend2)
            bPlot.draw_idle()
            self.showDisplay(self.xfDisp)

        else:
            print("Couldn't find file {}".format(fname))
        return

    def showDisplay(self, display):
        # type: (QWidget) -> None
        display.show()
        # brings the display to the front
        display.raise_()
        # gives the display focus
        display.activateWindow()

    def plotWindow(self):
        screen = QtWidgets.QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.xfDisp.ui.frame.winId())
        screenshot.save("/tmp/srf_micro.png", "png")
        system("convert /tmp/srf_micro.png /tmp/srf_micro.ps")

        # physicselog.submit_entry("lcls2", "MicrophonicsGui",
        #                         "Microphonics Data " + self.filNam, None,
        #                         "/tmp/srf_micro.ps", None)

from pydm import Display
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import (
    QWidgetItem,
    QCheckBox,
    QPushButton,
    QLineEdit,
    QGroupBox,
    QHBoxLayout,
    QMessageBox,
    QWidget,
    QLabel,
    QFrame,
    QComboBox,
    QRadioButton,
)
from os import path
import subprocess
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import FFt_math

lastPath = ""


class MplCanvas(FigureCanvasQTAgg):
    # MPLCanvas is the class for the 'canvas' that plots are drawn on and then mapped to the ui
    # They are Figure format described in matplotlib 2.2 documentation

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout="true")
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MicDisp(Display):
    def __init__(self, parent=None, args=None, ui_filename="FFT_test2.ui"):
        super(MicDisp, self).__init__(parent=parent, args=args, ui_filename=ui_filename)
        self.pathHere = path.dirname(sys.modules[self.__module__].__file__)

        def getPath(fileName):
            return path.join(self.pathHere, fileName)

        self.show()
        # brings the display to the front
        self.raise_()
        # gives the display focus
        self.activateWindow()
        self.ui.AcqProg.setText("Test of printing output from subprocess  line by line")

        self.ui.StrtBut.clicked.connect(
            self.subCall
        )  # call function setGOVal when strtBut is pressed
        self.ui.AcqProg.setText(
            "Select 1 CM and 1 cavity at a time for commissioning. \nLimit plotted waveforms to 30 sec."
        )

    def subCall(self):
        try:
            cmd = ["python", "-u", "/home/user/tutorial/GitDir/Microphonics/Testy2.py"]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                shell=False,
            )
            while True:
                output = process.stdout.readline().decode()
                if output == "" and process.poll() is not None:
                    break
                if output != "":
                    print(output)
                    self.ui.AcqProg.setText(output)

            return_code = process.poll()
            if return_code == 0:
                #                self.ui.AcqProg.setText("Test run completed successfully")
                print("Test run completed sucessfully")

            if return_code != 0:
                #        print(err)
                e = subprocess.CalledProcessError(return_code, cmd)
                #                    e.stdout, e.stderr = err
                #                self.ui.AcqProg.setText("Call to microphonics script failed \n"+str(e))
                print("Call returned non-zero value")

        except:
            #            self.ui.AcqProg.setText("try failed \n")
            print("try failed")

from stitcher import Stitcher
from quilt2PDF import PDFifier
import sys
import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets, uic


qtcreator_file  = "mainwindow.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)

class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.startButton.clicked.connect(self.openFileNameDialog)
        self.nextButton.clicked.connect(self.nextSlide)
        self.previousButton.clicked.connect(self.prevSlide)
        self.pdfButton.clicked.connect(self.genPDF)

        self.quilt = None
        self.image_num = 0

    def startNoah(self, path):
        #data is a string with the text
        self.stitcher = Stitcher(path)
        self.stitcher.stitch()
        self.pdfifier = PDFifier()
        self.quilt = self.stitcher.get_quilt()

        self.image_num = 0
        image_map = QPixmap(self.quilt[0].slide_path)
        data = self.fix_text(self.quilt[0].script)
        self.slideImage.setPixmap(image_map)
        self.textArea.setText('\n'.join(data))
        self.repaint()

    def nextSlide(self):
        if(self.quilt != None):
            if(self.image_num < len(self.quilt) - 1):
                self.image_num += 1
                image_map = QPixmap(self.quilt[self.image_num].slide_path)
                self.slideImage.setPixmap(image_map)
                data = self.fix_text(self.quilt[self.image_num].script)
                self.textArea.setText('\n'.join(data))
                self.repaint()

    def prevSlide(self):
        if(self.quilt != None):
            if(self.image_num > 0):
                self.image_num -= 1
                image_map = QPixmap(self.quilt[self.image_num].slide_path)
                self.slideImage.setPixmap(image_map)
                data = self.fix_text(self.quilt[self.image_num].script)
                self.textArea.setText('\n'.join(data))
                self.repaint()

    def fix_text(self, script):
        first = True
        fixed = list()
        for segment in script:
            new_text = ""
            for text in segment:
                for word in text:
                    if(first):
                        first = False
                        new_text += word
                    else:
                        new_text += (" " + word)
            fixed.append(new_text)
        return fixed

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        path, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        path = os.path.basename(path)
        if path:
            self.startNoah(path)

    def genPDF(self):
        print("Generating a pdf...")
        if(self.quilt != None):
            self.pdfifier.makePDF(self.quilt)
        print("Done!")



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

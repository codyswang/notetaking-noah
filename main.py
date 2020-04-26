from stitcher import Stitcher
import sys
import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets, uic


qtcreator_file  = "mainwindow.ui" # Enter file here.
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtcreator_file)

imagenum = 1
with open ("sampletext.txt", "r") as myfile:
            data=myfile.readlines()
            
class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
            
        self.startButton.clicked.connect(self.openFileNameDialog)
        self.nextButton.clicked.connect(self.nextSlide)
        self.previousButton.clicked.connect(self.prevSlide)
        self.pdfButton.clicked.connect(self.genPDF)
        
        
    def startNoah(self, path):
        #data is a string with the text
        self.stitcher = Stitcher(path)
        self.stitcher.stitch()
        global data
        global name
        name = os.path.basename(path)
        imagemap = QPixmap('slides/' + name + '0.jpg')
        self.slideImage.setPixmap(imagemap)
        self.textArea.setText('\n'.join(data))

    def nextSlide(self):
        global imagenum
        imagenum += 1
        imagemap = QPixmap('slides/'+name+str(imagenum)+'.jpg')
        self.slideImage.setPixmap(imagemap)
        
    def prevSlide(self):
        global imagenum
        if imagenum > 0:
            imagenum -= 1
            imagemap = QPixmap('slides/'+name+str(imagenum)+'.jpg')
            self.slideImage.setPixmap(imagemap)

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        path, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if path:
            self.startNoah(path)

    def genPDF(self):
        print("generating a pdf") #for debugging purposes
        ##put code in here to generate pdf
                           
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

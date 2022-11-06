import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog, QLineEdit, QRadioButton, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon, QImage
import sys
from PIL import Image
from PIL import ImageColor
import cv2
import math

# window

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # window size

        self.top = 200
        self.left = 500
        self.width = 300
        self.height = 400
        self.imgwidth = 417
        self.imgheight = 412

        # window name

        self.setWindowTitle("FaceTagging Application")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon('icon.png'))

    # btn
    def setWidgets(self):
        self.btn1 = QPushButton("이미지 업로드", self)
        self.btn1.clicked.connect(self.getPhotoPath)
        self.btn2 = QPushButton("이미지 편집", self)
        self.btn2.clicked.connect(self.createEditingWindow)
        self.btn3 = QPushButton("얼굴 찾기", self)
        self.btn3.clicked.connect(self.findFace)
        self.btn4 = QPushButton("얼굴 삭제", self)
        self.btn4.clicked.connect(self.delface)
        self.btn5 = QPushButton("Button 5", self)
        self.btn6 = QPushButton("Button 6", self)

        # upload
        self.label = QLabel("Upload Image Here.", self)

        # btn&label move
        vbox = QVBoxLayout()
        vbox.addWidget(self.btn1)
        vbox.addWidget(self.btn2)
        vbox.addWidget(self.btn3)
        vbox.addWidget(self.btn4)
        vbox.addWidget(self.btn5)
        vbox.addWidget(self.btn6)

        self.setLayout(vbox)

        # QVbox to widget
        buttons_widget = QWidget()
        buttons_widget.setLayout(vbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addWidget(buttons_widget)

        self.setLayout(hbox)

    # upload
    def getPhotoPath(self):
        fname = QFileDialog.getOpenFileName(self, '사진 업로드')
        # save image file location to int
        self.imagepath = fname[0]
        self.originalpath = fname[0]
        # load
        self.loadImage()

    # load
    def loadImage(self):
        self.pixmap = QPixmap(self.imagepath)
        self.label.setPixmap(self.pixmap)
        # set size
        pixmap_resized = self.pixmap.scaled(self.imgwidth, self.imgheight)
        self.label.setPixmap(pixmap_resized)

    # editing window (from here to ~ 119)
    def createEditingWindow(self):
        self.editwin = EditWindow()
        self.editwin.setWidgets(self)
        self.editwin.show()

    # face finding
    def findFace(self):
        self.fList = FaceList()
        # load xml
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        # read
        img = cv2.imread(self.imagepath, cv2.IMREAD_COLOR)
        img = cv2.resize(img, (self.imgwidth, self.imgheight))
        # set color
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # change 2 list
        faces = face_cascade.detectMultiScale(gray, 1.2, 1).tolist()

        for (x, y, w, h) in faces:
            print(x, y, w, h)
            self.fList.append_face(x, y, w, h)
            # circle = ((image), (x, y), (size), (color), radius))
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        self.showImage(img)
        print("face found")

    def showImage(self, img):
        height, width, colors = img.shape
        bytesPerLine = 3 * width
        image = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.image = image.rgbSwapped()
        self.label.setPixmap(QPixmap.fromImage(self.image))

    def delface(self):
        if self.label.pixmap() == None:
            print("image hasn't uploaded.")
        elif self.fList is None or self.fList.count_face==0:
            print("no face has been checked.")
        else:
            print("which face do you want to remove? right click to delete.")
            self.delclicked = True

    def mousePressEvent(self, event):
        diag = 10000.0

        if self.delclicked == True:
            print('position:' + ' (%d %d)' % (event.x(), event.y()))
            for i in self.fList.face_list:
                centx = i.x + (i.w / 2)
                centy = i.y + (i.h / 2)
                if diag > abs(math.sqrt(((centx-event.x())**2)+((centy-event.y())**2))):
                    diag = abs(math.sqrt(((centx-event.x())**2)+((centy-event.y())**2)))
                    faceid = i.id

            # remove
            print("removing face id: ", faceid)
            self.fList.remove_face(faceid)

            # reset recangle
            img = cv2.imread(self.imagepath, cv2.IMREAD_COLOR)
            img = cv2.resize(img, (self.imgwidth, self.imgheight))

            for f in self.fList.face_list:
                print(f.x, f.y, f.w, f.h, f.name, f.id)
                cv2.rectangle(img, (f.x, f.y), (f.x + f.w, f.y + f.h), (255, 0, 0), 2)
                self.delclicked = False
                self.showImage(img)

# editing window
class EditWindow(MainWindow):
    def __init__(self):
        super().__init__()
        self.width = 200
        self.height = 300
        self.setGeometry(self.left, self.top, self.width, self.height)

    # set widgets
    def setWidgets(self, mainwindow):
        # image name
        self.textimgname = QLabel('이미지 이름: {img.filename}', self)

        # change width, height
        self.textblank2 = QLabel(' ', self)
        self.labelwidth = QLabel("너비")
        self.textwidth = QLineEdit('Width', self)
        self.labelheight = QLabel("높이")
        self.textheight = QLineEdit('Height', self)
        self.labelcolor = QLabel("사진색")

        # image color
        self.textblank3 = QLabel(' ', self)
        self.radiobtn1 = QRadioButton("원본")
        self.radiobtn1.setChecked(True)
        self.radiochecked = "원본"
        self.radiobtn2 = QRadioButton("회색")
        self.radiobtn3 = QRadioButton("빨간색")
        self.radiobtn4 = QRadioButton("초록색")
        self.radiobtn5 = QRadioButton("파란색")
        self.radiobtn6 = QRadioButton("another color?")

        # image format
        self.textblank1 = QLabel(' ', self)
        self.textformat = QLabel('이미지 형식: {img.format}', self)
        self.textcmode = QLabel('이미지 색상모드: {img.mode}', self)

        self.btnOK = QPushButton('확인', self)
        self.btnOK.clicked.connect(lambda: self.editImage(mainwindow))

        # set layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.textblank2)
        vbox.addWidget(self.labelwidth)
        vbox.addWidget(self.textwidth)
        vbox.addWidget(self.labelheight)
        vbox.addWidget(self.textheight)
        vbox.addWidget(self.textblank3)
        vbox.addWidget(self.labelcolor)
        vbox.addWidget(self.radiobtn1)
        vbox.addWidget(self.radiobtn2)
        vbox.addWidget(self.radiobtn3)
        vbox.addWidget(self.radiobtn4)
        vbox.addWidget(self.radiobtn5)
        vbox.addWidget(self.radiobtn6)
        vbox.addWidget(self.textblank1)
        vbox.addWidget(self.textformat)
        vbox.addWidget(self.textcmode)
        vbox.addWidget(self.textimgname)
        vbox.addWidget(self.btnOK)

        self.setLayout(vbox)

        # connect
        self.radiobtn1.toggled.connect(self.btnstate)
        self.radiobtn2.toggled.connect(self.btnstate)
        self.radiobtn3.toggled.connect(self.btnstate)
        self.radiobtn4.toggled.connect(self.btnstate)
        self.radiobtn5.toggled.connect(self.btnstate)

    def btnstate(self):
        radiobtn = self.sender()
        self.radiochecked = radiobtn.text()

    # image size edit
    def editImage(self, mainwindow):
        imgwidth_edited = self.textwidth.text()
        imgheight_edited = self.textheight.text()

        img = Image.open(mainwindow.originalpath)
        # set color
        if self.radiochecked == "회색":
            img_edited = img.convert("L")
            img_edited.save(os.getcwd() + "\output\edited_gray.jpg", "JPEG")
            mainwindow.imagepath = os.getcwd() + "\output\edited_gray.jpg"
            mainwindow.loadImage()
            print("color set to gray")
        
        if self.radiochecked == "초록색":
            green = (
                0.41, 0.36, 0.18, 0,
                0.50, 0.12, 0.95, 0,
                0.02, 0.12, 0.95, 0)
            img_edited = img.convert("RGB", green)
            img_edited.save(os.getcwd() + "\output\edited_green.jpg", "JPEG")
            mainwindow.imagepath = os.getcwd() + "\output\edited_green.jpg"
            mainwindow.loadImage()
            print("color set to green")
        
        if self.radiochecked == "빨간색":
            red = (
                0.90, 0.36, 0.18, 0,
                0.11, 0.72, 0.07, 0,
                0.02, 0.12, 0.95, 0)
            img_edited = img.convert("RGB", red)
            img_edited.save(os.getcwd() + "\output\edited_red.jpg", "JPEG")
            mainwindow.imagepath = os.getcwd() + "\output\edited_red.jpg"
            mainwindow.loadImage()
            print("color set to red")

        if self.radiochecked == "파란색":
            blue = (
                0.31, 0.36, 0.18, 0,
                0.40, 0.72, 0.07, 0,
                0.60, 0.12, 0.95, 0)
            img_edited = img.convert("RGB", blue)
            img_edited.save(os.getcwd() + "\output\edited_blue.jpg", "JPEG")
            mainwindow.imagepath = os.getcwd() + "\output\edited_blue.jpg"
            mainwindow.loadImage()
            print("color set to blue")

        # original color
        if self.radiochecked == "원본":
            img_edited = img
            print("color set to default")

        # another color
        if self.radiochecked == "another color?":
            sans = ImageColor.getrgb('aquamarine')
            img_edited = img.convert(sans)
            img_edited.save(os.getcwd() + "\output\wasans.jpg", "JPEG")
            mainwindow.imagepath = os.getcwd() + "\output\wasans.jpg"
            mainwindow.loadImage()
            print("color set to ?")

        # if same as default
        if imgwidth_edited == "Width":
            imgwidth_edited = mainwindow.imgwidth
        if imgheight_edited == "Height":
            imgheight_edited = mainwindow.imgheight

        try:
            mainwindow.imgwidth = int(imgwidth_edited)
            mainwindow.imgheight = int(imgheight_edited)
            mainwindow.loadImage()
            self.close()

        except ValueError:
            QMessageBox.question(self, '너비, 높이 오류', "너비나 높이가 숫자가 아닙니다.", QMessageBox.Ok)

class Face:
    def __init__(self, x, y, w, h, name, idx):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.name = name
        self.id = idx

class FaceList:
    def __init__(self):
        # reset
        self.face_list = []
        self.next_id = 0

    def append_face(self, x, y, w, h):
        self.face_list.append(Face(x, y, w, h, '', self.next_id))
        self.next_id += 1

    def count_face(self):
        return len(self.face_list)

    def remove_face(self, ind):
        cnt = 0
        for i in self.face_list:
            if i.id == ind:
                del self.face_list[cnt]
            cnt += 1

# Main
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # load main window
    win = MainWindow()
    win.setWidgets()
    win.show()
    app.exec_()

##############################
#        NOTE SECTION        |
##############################
# testimg 1 ~ 5 size         |
##############################
# 1. 243 x 207               |
# 2. 417 x 412               |
# 3. 508 x 339               |
# 4. 509 x 339               |
# 5. 417 x 412               |
##############################

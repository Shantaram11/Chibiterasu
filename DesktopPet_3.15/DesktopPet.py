import os
import threading
import time
import pygame
import cfg
import sys
import random
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import QThread
import re


class OneThread(QThread):
    signal = QtCore.pyqtSignal(int)

    def __init__(self, **kwargs):
        super(OneThread, self).__init__()
        self.t = kwargs.get('t')

    def run(self):
        start = time.time()
        while True:
            if time.time() - start >= self.t:
                self.signal.emit(0)
                return


class TwoThread(QThread):
    signal = QtCore.pyqtSignal(str)

    def __init__(self, **kwargs):
        super(TwoThread, self).__init__()

    def run(self):

        while True:
            t = time.strftime("%H:%M:%S", time.localtime())
            for i in range(0, 24):
                temp = "{:0>2d}:00:00".format(i)
                if t == temp:  # check time
                    self.signal.emit(temp)  # transfer data


class DesktopPet(QWidget):
    def __init__(self, parent=None, **kwargs):
        super(DesktopPet, self).__init__(parent)
        # initialization
        self.timer1 = QTimer(self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.repaint()
        # Import pet image
        self.pet_images, iconpath = self.loadPetImages()
        # Set exit options
        quit_action = QAction('exit', self, triggered=self.quit)
        quit_action.setIcon(QIcon(iconpath))
        self.tray_icon_menu = QMenu(self)
        self.tray_icon_menu.addAction(quit_action)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(iconpath))
        self.tray_icon.setContextMenu(self.tray_icon_menu)
        self.tray_icon.show()
        # The picture currently displayed
        self.image = QLabel(self)
        self.setImage(self.pet_images[0][0])
        # Follow the mouse or not
        self.is_follow_mouse = False
        # Avoid the mouse jumping directly to the upper left corner when the pet is dragged
        self.mouse_drag_pos = self.pos()
        # display
        self.resize(128, 128)
        self.move(200, 200)
        self.show()

        # Some variables required for the execution of the pet animation action
        self.pet_status_list = cfg.PET_STATUS_MAP
        self.pet_status = self.pet_status_list[0]
        self.music_list = cfg.MUSIC_LIST
        self.if_hourlyChime = False
        self.edgePos_right = QDesktopWidget().screenGeometry().width()
        self.action_images = []
        self.action_pointer = 0
        self.action_max_len = 0

        # Do a move every once in a while
        self.timer = QTimer()
        self.timer.timeout.connect(self.runAction)
        self.timer.start(400)

        self.drag_image = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime6.png'))
        self.fall_image = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime4.png'))
        self.fall_image_1 = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime18.png'))
        self.fall_image_2 = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime20.png'))
        self.fall_image_3 = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime21.png'))

        self.talklabel = QLabel()
        self.talklabel.setWindowFlags(Qt.FramelessWindowHint)
        self.talklabel.setStyleSheet("color:#66ccff;"
                                     "background-color:#f5f5dc;"
                                     "border:0px;"
                                     "font-size:20px;"
                                     "font-family:Comic Sans MS"
                                     )
        self.timer_for_hide = QTimer()
        self.timer_for_hide.timeout.connect(self.talklabel_hide)
        self.timer_for_hide.start(5000)

        self.input_talklabel = QInputDialog()
        self.input_talklabel.setWindowTitle("Input Dialog")
        global input_message


        self.setFocusPolicy(Qt.StrongFocus)
        self.swoop_left_0 = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime21.png'))
        self.swoop_left_1 = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime22.png'))
        self.swoop_left_2 = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime19.png'))
        self.swoop_left_3 = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime18.png'))
        self.swoop_right_0 = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime50.png'))
        self.swoop_right_1 = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime51.png'))
        self.swoop_right_2 = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime52.png'))
        self.swoop_right_3 = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime53.png'))
        self.swoop_distance = 200

    def hide(self):
        self.talklabel.hide()

    def runAction(self):
        if self.pet_status == self.pet_status_list[0]:
            self.randomAct()
        elif self.pet_status == self.pet_status_list[1]:
            # self.dragged()
            pass
        elif self.pet_status == self.pet_status_list[2]:
            self.climbAct()

    # Do an action at random
    def randomAct(self):
        def move():
            x = self.pos().x()
            y = self.pos().y()
            if self.action_images != self.pet_images[4]:
                self.move(x + 20, y)  # Go to the right
            elif self.action_images != self.pet_images[5]:
                self.move(x - 20, y)  # Go to the left
            self.setImage(self.action_images[self.action_pointer])
            self.action_pointer += 1
            self.runFrame()

        # Walk left and right at random, or stop
        if self.action_pointer == self.action_max_len:
            choice = random.randint(1, 10)
            if choice in (1, 2) and self.pos().x() > 20:  # Go to the left
                self.action_images = self.pet_images[4]
            elif choice in (3, 4) and self.pos().x() < self.edgePos_right - 200:  # Go to the right
                self.action_images = self.pet_images[5]
            else:  # Sit still
                # Sit-down random action
                choice = random.randint(1, 10)
                if choice in (1, 2):
                    self.action_images = self.pet_images[6]
                elif choice in (2, 3):
                    self.action_images = self.pet_images[7]
                else:
                    self.action_images = self.pet_images[8]
            self.action_max_len = len(self.action_images)
            self.action_pointer = 0
        if self.action_images == self.pet_images[4] or self.action_images == self.pet_images[5]:
            move()
        else:
            self.runFrame()

    # Complete the wall climb
    def climbAct(self):
        screen_size = QDesktopWidget().screenGeometry()
        self.pet_status = self.pet_status_list[2]  # Setting up a pet to climb the state
        if self.pos().x() < 0:
            petPos_x = -40
        else:
            petPos_x = QDesktopWidget().screenGeometry().width() - 100
        self.move(petPos_x, self.y())

        # When the climb is performed, the pet moves upward
        def climb():
            self.runFrame()
            if self.pos().y() > 30:
                self.move(petPos_x, self.y() - 10)
            else:  # Reach the corresponding height automatic sliding
                delta_time = (1 / 1000)

                def playMusic():
                    pygame.mixer.init()
                    pygame.mixer.music.load(self.music_list[0])  # path of mp3 file
                    pygame.mixer.music.play()
                    time.sleep(1)

                move_dis = random.randint(int(screen_size.height() / 3), int(screen_size.height() / 2))

                t1 = threading.Thread(target=playMusic)
                t1.start()
                while move_dis >= 0:
                    # jump out the loop if draged
                    if self.is_follow_mouse:
                        break
                    self.move(self.pos().x(), self.pos().y() + 2)
                    move_dis -= 2
                    time.sleep(delta_time)
                    t1.join()

        # Determine whether the action is executed/executed, and the random selection continues to climb/stop
        if self.action_pointer == self.action_max_len or (
                self.action_images != self.pet_images[2] and self.action_images != self.pet_images[3]):
            random_num = random.randint(1, 10)
            if random_num in range(1, 7):
                self.action_images = self.pet_images[3]
            else:
                self.action_images = self.pet_images[2]
            self.action_max_len = len(self.action_images)
            self.action_pointer = 0

        if self.action_images == self.pet_images[2]:
            climb()
        else:
            self.runFrame()

    # Complete each frame of the action, and each frame plays after the timer ends
    def runFrame(self):
        if self.action_pointer == self.action_max_len:  # End of action
            self.action_pointer = 0
        self.setImage(self.action_images[self.action_pointer])
        self.action_pointer += 1

    # Sets the image currently displayed
    def setImage(self, image):
        self.image.setPixmap(QPixmap.fromImage(image))

    # Import all pictures of desktop pets
    def loadPetImages(self):
        pet_name = random.choice(list(cfg.PET_ACTIONS_MAP.keys()))
        actions = cfg.PET_ACTIONS_MAP[pet_name]
        pet_images = []
        for action in actions:
            pet_images.append(
                [self.loadImage(os.path.join(cfg.ROOT_DIR, pet_name, 'shime' + item + '.png')) for item in action])
        iconpath = os.path.join(cfg.ROOT_DIR, pet_name, 'shime1.png')
        return pet_images, iconpath

    # Determine if the pet is on the edge
    def isEdge(self):
        if self.pos().x() < 0 or self.pos().x() > self.edgePos_right - 140:
            self.pet_status = self.pet_status_list[2]
            return True
        return False

    # When the left mouse button is pressed, the pet will be bound to the mouse position
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pet_status = self.pet_status_list[1]
            self.setImage(self.drag_image)
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))
            pygame.mixer.init()
            pygame.mixer.music.load(self.music_list[1])
            pygame.mixer.music.play()

    # When the mouse moves, the pet moves
    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_follow_mouse:
            self.pet_status = self.pet_status_list[1]
            # Switch images while moving
            self.setImage(self.fall_image)
            self.move(event.globalPos() - self.mouse_drag_pos)
            event.accept()

    # Cancel the binding when the mouse is released
    def mouseReleaseEvent(self, event):
        # When the mouse is released, you need to determine if the pet is on the edge of the screen
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = False
            self.setCursor(QCursor(Qt.ArrowCursor))
            if self.isEdge():
                self.pet_status = self.pet_status_list[2]

            else:
                g = 1
                distance = 250
                if self.pos().y() > 700:
                    distance = 0
                while distance != 0:
                    self.setImage(self.fall_image)
                    self.move(self.x(), self.y() + g)
                    distance -= g
                self.setImage(self.fall_image_1)
                self.setImage(self.fall_image_2)
                self.setImage(self.fall_image_3)
                self.setCursor(QCursor(Qt.ArrowCursor))
                self.pet_status = self.pet_status_list[0]

    def keyPressEvent(self, event):
        self.pet_status = self.pet_status_list[3]
        if event.key() == Qt.Key_Right:
            self.setImage(self.swoop_right_0)
            self.swoop_distance += 20

        elif event.key() == Qt.Key_Left:
            self.setImage(self.swoop_left_0)
            self.swoop_distance += 20


    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Right:
            if not event.isAutoRepeat():
                self.setImage(self.swoop_right_1)
                distance = min(self.swoop_distance, self.edgePos_right - self.pos().x() - 200)
                distance = 2*round(distance)
                x = self.pos().x()
                y = self.pos().y()
                for i in range(distance):
                    x += 0.25
                    y -= 0.25
                    self.move(round(x), round(y))
                self.setImage(self.swoop_right_2)
                for i in range(distance):
                    x += 0.25
                    y += 0.25
                    self.move(round(x), round(y))
                self.setImage(self.swoop_right_3)
                textbox(self.talklabel, "Oops!", self.pos().x(), self.pos().y()-20)
                self.swoop_distance = 200
                self.pet_status = self.pet_status_list[0]
        elif event.key() == Qt.Key_Left:
            if not event.isAutoRepeat():
                self.setImage(self.swoop_left_1)
                distance = min(self.swoop_distance, self.pos().x() - 100)
                distance = 2*round(distance)
                x = self.pos().x()
                y = self.pos().y()
                for i in range(distance):
                    x -= 0.25
                    y -= 0.25
                    self.move(round(x), round(y))
                self.setImage(self.swoop_left_2)
                for i in range(distance):
                    x -= 0.25
                    y += 0.25
                    self.move(round(x), round(y))

                self.setImage(self.swoop_left_3)
                textbox(self.talklabel, "Oops", self.pos().x(), self.pos().y() - 20)
                self.swoop_distance = 200
                self.pet_status = self.pet_status_list[0]



    # Import image
    def loadImage(self, imagepath):
        image = QImage()
        image.load(imagepath)
        return image

    def contextMenuEvent(self, e, ):
        # Right-click menu
        cmenu = QMenu(self)
        act1 = cmenu.addAction("Open")
        act2 = cmenu.addAction("Interaction")
        act3 = cmenu.addAction("Weather")
        act4 = cmenu.addAction("Daily reminder")
        act5 = cmenu.addAction("Game")
        act6 = cmenu.addAction("HourlyChime")
        act7 = cmenu.addAction("Exit")
        act8 = cmenu.addAction("swoop")

        action = cmenu.exec_(self.mapToGlobal(e.pos()))
        if action == act7:
            qApp.quit()
        elif action == act1:
            os.system()
        elif action == act2:
            os.startfile()
        elif action == act3:
            os.startfile()
        elif action == act4:
            self.countDown()
        elif action == act6:
            self.hourlyChime()
        elif action == act8:
            self.pet_status = self.pet_status_list[3]

    def hourlyChime(self):
        # on time alarm

        if not self.if_hourlyChime:

            self.if_hourlyChime = True
            self.hour = TwoThread()
            self.hour.start()
            self.hour.signal.connect(self.printTime)
        else:

            self.if_hourlyChime = False
            self.hour.quit()

    def printTime(self, tm):
        print(222)

    def countDown(self):
        # reminder

        value, ok = QInputDialog.getMultiLineText(self, "Reminder", "Countdown\n\nPlease enter time: ",
                                                  "Count down time: 0h0m0s\ncontent")
        values = re.findall('\d', value.split('\n')[0])
        t = int(values[0]) * 3600 + int(values[1]) * 60 + int(values[2])
        self.p = OneThread(t=t)
        self.p.start()
        self.p.signal.connect(self.func)

    def func(self):
        # "时间到！
        print(111)

    '''quit program'''

    def quit(self):
        self.close()
        sys.exit()

    def talklabel_hide(self):
        self.talklabel.hide()



def textbox(label, words, x, y):  # parameter label = self.talklabel
    label.hide()
    label.setText(words)
    label.move(x, y)
    label.adjustSize()
    label.show()


def input_textbox(input_label, title, ask, x, y):  # parameter input_label = self.input_talklabel
    input_label.move(x, y)
    inputmessage, okpressed = QInputDialog.getText(input_label, title, ask)
    if okpressed and inputmessage != "":
        input_message = inputmessage  # content stored in global variable input_message
        input_label.hide()


'''run'''
if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec_())

import os
import sqlite3
import threading
import time
from lxml import etree

import pygame
import requests as requests

import cfg
import sys
import random
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread
import re
from UILoader import UILoader
from qt_material import apply_stylesheet


class ODBC():
    def __init__(self):
        self.path = os.path.join(os.getcwd(), 'datas.db')

    def GetConnect(self):
        self.con = sqlite3.connect(self.path)
        cur = self.con.cursor()
        if not cur:
            raise (NameError, 'Fail to connect with database')
        else:
            return cur

    def add_info(self, table_name, data):
        # add information
        value_len = ','.join('?' * len(data[0]))  # count the length of info
        sql = 'INSERT INTO %s VALUES (%s)' % (str(table_name), value_len)
        cur = self.GetConnect()
        cur.executemany(sql, data)
        self.con.commit()

    def del_info(self, table_name, name):
        # delete information
        sql = 'delete from %s where Time2 like "%s"' % (str(table_name), str(name))

        cur = self.GetConnect()
        cur.execute(sql)
        self.con.commit()

    def adjust_info(self, table_name, text, data):
        # adjust information
        self.del_info(table_name, text)
        self.add_info(table_name, data)

    def search_all_info(self, table_name):
        # search for information
        sql = 'select * from %s' % str(table_name)

        cur = self.GetConnect()
        datas = cur.execute(sql)
        return [i for i in datas]

    def search_info_by(self):

        pass

    def creat_(self):
        # using cursor（）to create a cursor
        cursor = self.GetConnect()
        sql = '''CREATE TABLE Bwl
                           (
                           Texts          CHAR(100),
                           Time1          CHAR(100)  ,
                            Time2     CHAR(300));'''
        try:
            cursor.execute(sql)
            # upload to database
            self.con.commit()
            print('CREATE [user_info] TABLE SUCCESS.')
        # catch database corresponding error
        except:
            print('CREATE TABLE FAILED')
            self.con.rollback()
        finally:
            # close database
            self.con.close()


ms = ODBC()


class OneThread(QThread):
    signal = QtCore.pyqtSignal(str)

    def __init__(self, **kwargs):
        super(OneThread, self).__init__()
        # self.t = kwargs.get('t')  #

    def run(self):
        start = time.time()
        while True:
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            datas = ms.search_all_info('Bwl')
            if len(datas) == 0:
                continue
            for i in datas:

                if i[1] == t:
                    self.signal.emit(i[0])


class TwoThread(QThread):
    signal = QtCore.pyqtSignal(str)

    def __init__(self, **kwargs):
        super(TwoThread, self).__init__()

    def run(self):

        while True:
            t = time.strftime("%H:%M:%S", time.localtime())
            for i in range(0, 24):
                temp = "{:0>2d}:00:00".format(i)
                if t == temp:  # check hour
                    self.signal.emit(temp)  # transmit data


class DesktopPet(QWidget):
    def __init__(self, window: UILoader, parent=None, **kwargs):
        super(DesktopPet, self).__init__(parent)
        # initialization
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.repaint()
        self.p = OneThread()
        self.p.start()
        self.p.signal.connect(self.func)
        # Import pet image
        self.pet_images, iconpath1, iconpath2, iconpath3 = self.loadPetImages()
        # Set exit options
        self.quit_action = QAction('Exit', self, triggered=self.quit)
        self.pet_show_action = QAction('Hide Pet', self, triggered=self.show_or_hide)
        self.window_show_action = QAction('Show Console', self, triggered=self.show_or_hide_window)
        self.show_or_not = 1

        self.quit_action.setIcon(QIcon(iconpath1))
        self.pet_show_action.setIcon(QIcon(iconpath2))
        self.window_show_action.setIcon(QIcon(iconpath3))

        self.tray_icon_menu = QMenu(self)
        self.tray_icon_menu.addAction(self.pet_show_action)
        self.tray_icon_menu.addAction(self.window_show_action)
        self.tray_icon_menu.addAction(self.quit_action)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(iconpath1))
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

        self.rest = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime15.png'))
        self.weather_posture = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime41.png'))

        self.drag_image = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime6.png'))
        self.fall_image = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime4.png'))
        self.fall_image_1 = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime18.png'))
        self.fall_image_2 = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime20.png'))
        self.fall_image_3 = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime21.png'))

        self.talklabel = QLabel()
        self.talklabel.setWordWrap(True)
        self.talklabel.setWindowFlags(Qt.FramelessWindowHint)
        self.talklabel.setStyleSheet("color:#66ccff;"
                                     "background-color:#f5f5dc;"
                                     "border:0px;"
                                     "font-size:20px;"
                                     "font-family:Comic Sans MS"
                                     )
        self.timer_for_hide = QTimer()
        self.timer_for_hide.timeout.connect(self.talklabel_hide)
        self.timer_for_weather_hide = QTimer()
        self.timer_for_weather_hide.timeout.connect(self.weather_hide)
        self.wea = self.weather()

        self.input_talklabel = QInputDialog()
        self.input_talklabel.setWindowTitle("Input Dialog")

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

        self.icon1 = os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime16.png')
        self.icon2 = os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime22.png')
        self.icon3 = os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime41.png')
        self.icon4 = os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime5.png')
        self.icon5 = os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime18.png')
        self.icon6 = os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime23.png')
        self.icon7 = os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime42.png')

        self.seeyou = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime30.png'))
        self.alarm = self.loadImage(os.path.join(cfg.ROOT_DIR, 'pet_1', 'shime41.png'))

        t = time.localtime()

        if 4 <= t.tm_hour < 11:
            hello = "Good Morning!"
        elif 11 <= t.tm_hour < 18:
            hello = "Good Afternoon!"
        else:
            hello = "Good Evening!"
        textbox(self.talklabel, hello, self.x() - 10, self.y() - 30)
        self.timer_for_hide.start(2000)

        self.timer_seeyou = QTimer()
        self.timer_seeyou.timeout.connect(self.quit)

        self.ms = ODBC()
        self.timer_reminder = QTimer()
        self.timer_reminder.timeout.connect(self.reminder)

        app1 = QApplication(sys.argv)
        self.window = window
        sys.exit(app1.exec_())
        self.window.mainWindow.hide()

    def hide(self):
        self.talklabel.hide()

    def runAction(self):
        if self.window.OpenShowModel() == 0:
            self.image.hide()
            self.pet_show_action.setText("Show Pet")
            self.show_or_not = 0
        else:
            self.image.show()
            self.pet_show_action.setText("Hide Pet")
            self.show_or_not = 1

        if self.window.OpenFreeMove() == 0:
            self.pet_status = self.pet_status_list[5]
            self.setImage(self.rest)

        else:
            if self.pet_status == self.pet_status_list[0]:
                self.randomAct()
            elif self.pet_status == self.pet_status_list[1]:
                # self.dragged()
                pass
            elif self.pet_status == self.pet_status_list[2]:
                self.climbAct()
            elif self.pet_status == self.pet_status_list[5]:
                if (self.window.OpenFreeMove() == 1):
                    self.pet_status = self.pet_status_list[0]

        self.timer.start(1200 - self.window.GetActivityFrequency())

    # Do an action at random
    def randomAct(self):
        def move():
            x = self.pos().x()
            y = self.pos().y()
            if self.action_images != self.pet_images[4]:
                self.talklabel.move(self.talklabel.x() + 20, self.talklabel.y())
                self.move(x + 20, y)  # Go to the right
            elif self.action_images != self.pet_images[5]:
                self.talklabel.move(self.talklabel.x() - 20, self.talklabel.y())
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
                    pygame.mixer.music.load(self.music_list[0])  # path of the music
                    pygame.mixer.music.set_volume(self.window.GetSoundValue())
                    pygame.mixer.music.play()
                    time.sleep(1)

                move_dis = random.randint(int(screen_size.height() / 3), int(screen_size.height() / 2))

                t1 = threading.Thread(target=playMusic)
                t1.start()
                while move_dis >= 0:
                    # jump out of the loop if it's dragged
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
        # self.activity_frequency.start(self.window.GetActivityFrequency())

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
        iconpath1 = os.path.join(cfg.ROOT_DIR, pet_name, 'shime1.png')
        iconpath2 = os.path.join(cfg.ROOT_DIR, pet_name, 'shime4.png')
        iconpath3 = os.path.join(cfg.ROOT_DIR, pet_name, 'shime18.png')
        return pet_images, iconpath1, iconpath2, iconpath3

    # Determine if the pet is on the edge
    def isEdge(self):
        if self.pos().x() < 0:
            self.pet_status = self.pet_status_list[2]
            return True
        return False

    # When the left mouse button is pressed, the pet will be bound to the mouse position
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.talklabel.hide()
            self.pet_status = self.pet_status_list[1]
            self.setImage(self.drag_image)
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))
            pygame.mixer.init()
            pygame.mixer.music.load(self.music_list[1])
            pygame.mixer.music.set_volume(self.window.GetSoundValue())
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
                distance = 2 * round(distance)
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
                textbox(self.talklabel, "Oops!", self.pos().x(), self.pos().y() - 20)
                self.timer_for_hide.start(1000)
                self.swoop_distance = 200
                self.pet_status = self.pet_status_list[0]
        elif event.key() == Qt.Key_Left:
            if not event.isAutoRepeat():
                self.setImage(self.swoop_left_1)
                distance = min(self.swoop_distance, self.pos().x() - 100)
                distance = 2 * round(distance)
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
                textbox(self.talklabel, "Oops!", self.pos().x() + 35, self.pos().y() - 20)
                self.timer_for_hide.start(1000)
                self.swoop_distance = 200
                self.pet_status = self.pet_status_list[0]

    # Weather
    def weather(self):
        # Weather catch bag
        url = f'https://www.bbc.co.uk/weather/2644210'
        res = requests.get(url)
        res.encoding = 'utf-8'
        html_node = etree.HTML(res.content)
        maxTemperature = \
            html_node.xpath('//*[@id="daylink-0"]/div[4]/div[1]/div/div[4]/div/div[1]/span[2]/span/span[1]/text()')[0]
        try:
            minTemperature = \
                html_node.xpath('//*[@id="daylink-0"]/div[4]/div[1]/div/div[4]/div/div[2]/span[2]/span/span[1]/text()')[
                    0]
        except:
            minTemperature = \
                html_node.xpath('//*[@id="daylink-0"]/div[4]/div[1]/div/div[4]/div/div[1]/span[2]/span/span[1]/text()')[
                    0]
            maxTemperature = str(int(minTemperature[0:-1]) + 5) + "°"

        sunriseTime = \
            html_node.xpath('//*[@id="wr-forecast"]/div[4]/div/div[1]/div[4]/div/div[1]/div[1]/span[1]/span[2]/text()')[
                0]
        sunsetTime = \
            html_node.xpath('//*[@id="wr-forecast"]/div[4]/div/div[1]/div[4]/div/div[1]/div[1]/span[2]/span[2]/text()')[
                0]
        detailedWeather = \
            html_node.xpath('// *[ @ id = "wr-forecast"] / div[1] / div[4] / div / span[1]/text()')[0]
        humidity = \
            html_node.xpath('//*[@id="site-container"]/div[6]/div/div/div[3]/div/div[1]/ul/li[1]/text()')[0]
        visibility = \
            html_node.xpath('//*[@id="site-container"]/div[6]/div/div/div[3]/div/div[1]/ul/li[2]/text()')[0]

        # Tips
        tempTip1 = \
            "Hoo hoo, how cold it is today! I still feel good, but you need to keep warm ლ(╹◡╹ლ)"
        tempTip2 = \
            "It's a sizzler! My fur coat makes me feel so hot (T ^ T). How do you feel now?"
        tempTip3 = \
            "Wow, today's temperature makes me feel very comfortable (*￣∇￣*)"

        if float(minTemperature[0:-1]) <= 5:
            tempTip = tempTip1
        elif float(maxTemperature[0:-1]) >= 25:
            tempTip = tempTip2
        else:
            tempTip = tempTip3

        sunTip = "(〃'▽'〃) Are we going to the seaside to watch the sunset together?"

        temp = "Maximum temperature and minimum temperature:" + maxTemperature + "," + minTemperature + ". " + tempTip
        wea = "Weather:" + detailedWeather
        hum = "Humidity:" + humidity
        vis = "Visibility:" + visibility
        sun = "Time of sunrise and sunset:" + sunriseTime + "," + sunsetTime + sunTip
        return [temp, wea, hum, vis, sun]

        # Import image

    def loadImage(self, imagepath):
        image = QImage()
        image.load(imagepath)
        return image

    def contextMenuEvent(self, e, ):
        # Right-click menu
        cmenu = QMenu(self)
        act1 = cmenu.addAction("Open Console")
        act2 = cmenu.addAction("Swoop")
        act3 = cmenu.addAction("Weather")
        act4 = cmenu.addAction("Add Reminder")
        if self.pet_status == self.pet_status_list[5]:
            act5 = cmenu.addAction("Move")
        else:
            act5 = cmenu.addAction("Rest")
        if self.if_hourlyChime == 1:
            act6 = cmenu.addAction("Close HourlyChime")
        else:
            act6 = cmenu.addAction("Open HourlyChime")
        act7 = cmenu.addAction("Exit")

        child = QMenu(self)
        child_1 = child.addAction("Temperature")
        child_2 = child.addAction("Weather")
        child_3 = child.addAction("Humidity")
        child_4 = child.addAction("Visibility")
        child_5 = child.addAction("Time of sunrise and sunset")
        act3.setMenu(child)

        act1.setIcon(QIcon(self.icon1))
        act2.setIcon(QIcon(self.icon2))
        act3.setIcon(QIcon(self.icon3))
        act4.setIcon(QIcon(self.icon4))
        act5.setIcon(QIcon(self.icon5))
        act6.setIcon(QIcon(self.icon6))
        act7.setIcon(QIcon(self.icon7))

        action = cmenu.exec_(self.mapToGlobal(e.pos()))
        if action == act1:
            self.window.mainWindow.show()
        elif action == act2:
            self.pet_status = self.pet_status_list[3]
            textbox(self.talklabel, "Press <- or -> to swoop!", self.x() - 20, self.y() - 50)
            self.timer_for_hide.start(2000)
        elif action == act3:
            # temp->wea[0], wea->wea[1], hum->wea[2], vis->wea[3], sun->wea[4]
            self.pet_status = self.pet_status_list[4]
        elif action == act4:
            self.setImage(self.rest)
            self.pet_status = self.pet_status_list[4]
            self.input_talklabel.move(self.x() - 280, self.y() - 350)
            content = input_textbox(self.input_talklabel, "Schedule", "Content", self.x() - 280, self.y() - 350, "")
            if content == "0":
                pass
            else:
                local_time = time.localtime()
                default = str(local_time.tm_year) + "-" + str(local_time.tm_mon) + "-" + str(
                    local_time.tm_mday) + " " + str(local_time.tm_hour) + ":" + str(local_time.tm_min) + ":" + str(
                    local_time.tm_sec)
                self.input_talklabel.move(self.x() - 280, self.y() - 350)
                time_to_add = input_textbox(self.input_talklabel, "Time", "Target time\n(yyyy-mm-dd hh:mm:ss)",
                                            self.x() - 280, self.y() - 350, default)
                if time_to_add == "0": pass
                else:
                    s = str.split(time_to_add, " ")
                    d = str.split(s[0], "-")
                    qdate = QDate(int(d[0]), int(d[1]), int(d[2]))
                    t = str.split(s[1], ":")
                    qtime = QTime(int(t[0]), int(t[1]), int(t[2]))
                    (self.window).addSchedule1(qdate, qtime, content)
                    t = QDateTime(qdate, qtime)
                    self.ms.add_info('Bwl',
                                     [[content, t.toString(Qt.ISODate).replace('T', ' '),
                                       str(t.toMSecsSinceEpoch())[0:-3]]])
                    textbox(self.talklabel, "Successfully added! you can check it in Console->Schedule", self.x() - 130,
                            self.y() - 55)
                    self.timer_for_hide.start(3000)
            self.pet_status = self.pet_status_list[0]
        elif action == act5:
            if self.window.OpenFreeMove() == 1:
                self.window.SetFreeMove(0)
            else:
                self.window.SetFreeMove(1)
            if self.pet_status == self.pet_status_list[0]:
                self.setImage(self.rest)
                self.pet_status = self.pet_status_list[4]

            else:
                self.pet_status = self.pet_status_list[0]

        elif action == act6:
            if not self.if_hourlyChime:

                textbox(self.talklabel, "Yes! I will meow~ every hour!", self.x() - 20, self.y() - 55)
                self.timer_for_hide.start(2000)
                self.hourlyChime()
            else:

                textbox(self.talklabel, "Alright~ I know you dislike it", self.x() - 20, self.y() - 55)
                self.timer_for_hide.start(2000)
                self.hourlyChime()
        elif action == act7:
            self.pet_status = self.pet_status_list[4]
            self.setImage(self.seeyou)
            textbox(self.talklabel, "See you~", self.x() + 10, self.y() - 25)
            self.timer_for_hide.start(1500)
            self.timer_seeyou.start(2000)
        elif action == child_1:
            self.pet_status = self.pet_status_list[4]
            self.setImage(self.weather_posture)
            textbox(self.talklabel, self.wea[0], self.x() - 100, self.y() - 150)
            self.timer_for_weather_hide.start(self.window.GetDialogLife())
        elif action == child_2:
            self.pet_status = self.pet_status_list[4]
            self.setImage(self.weather_posture)
            textbox(self.talklabel, self.wea[1], self.x() - 100, self.y() - 60)
            self.timer_for_weather_hide.start(self.window.GetDialogLife())
        elif action == child_3:
            self.pet_status = self.pet_status_list[4]
            self.setImage(self.weather_posture)
            textbox(self.talklabel, self.wea[2], self.x() - 20, self.y() - 25)
            self.timer_for_weather_hide.start(self.window.GetDialogLife())
        elif action == child_4:
            self.pet_status = self.pet_status_list[4]
            self.setImage(self.weather_posture)
            textbox(self.talklabel, self.wea[3], self.x(), self.y() - 60)
            self.timer_for_weather_hide.start(self.window.GetDialogLife())
        elif action == child_5:
            self.pet_status = self.pet_status_list[4]
            self.setImage(self.weather_posture)
            textbox(self.talklabel, self.wea[4], self.x() - 100, self.y() - 120)
            self.timer_for_weather_hide.start(self.window.GetDialogLife())

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
        tm = time.localtime().tm_hour
        textbox(self.talklabel, str("It's " + str(tm) + " now!"), self.x(), self.y() - 50)
        self.timer_for_hide.start(3000)
        self.setCursor(QCursor(Qt.OpenHandCursor))
        pygame.mixer.init()
        pygame.mixer.music.load(self.music_list[1])
        pygame.mixer.music.set_volume(self.window.GetSoundValue())
        pygame.mixer.music.play()

    def countDown(self):
        # memorandum

        value, ok = QInputDialog.getMultiLineText(self, "Reminder", "Countdown\n\nPlease enter time: ",
                                                  "Count down time: 0h0m0s\ncontent")

        values = re.findall('\d', value.split('\n')[0])
        t = int(values[0]) * 3600 + int(values[1]) * 60 + int(values[2])
        self.p = OneThread(t=t)
        self.p.start()
        self.p.signal.connect(self.func)

    def func(self, t):
        # it's about the time
        if self.window.getRemindstate() == 1:
            self.setCursor(QCursor(Qt.OpenHandCursor))
            pygame.mixer.init()
            pygame.mixer.music.load(self.music_list[1])
            pygame.mixer.music.set_volume(self.window.GetSoundValue())
            pygame.mixer.music.play()
            self.pet_status = self.pet_status_list[4]
            self.setImage(self.alarm)
            textbox(self.talklabel, str("Yahoo! It's time to:\n" + t), self.x(), self.y() - 50)
            self.timer_reminder.start(3000)

    '''exit program'''

    def quit(self):
        self.close()
        sys.exit()

    def talklabel_hide(self):
        self.talklabel.hide()
        self.timer_for_hide.stop()

    def weather_hide(self):
        self.talklabel.hide()
        self.timer_for_weather_hide.stop()
        self.pet_status = self.pet_status_list[0]

    def show_or_hide(self):
        if (self.show_or_not == 1):
            self.image.hide()
            self.pet_show_action.setText("Show Pet")
            self.show_or_not = 0
            self.window.SetShowModel(0)


        else:
            self.image.show()
            self.pet_show_action.setText("Hide Pet")
            self.show_or_not = 1
            self.window.SetShowModel(1)

    def show_or_hide_window(self):
        self.window.mainWindow.show()

    def reminder(self):
        self.talklabel.hide()
        self.pet_status = self.pet_status_list[0]


def textbox(label, words, x, y):  # parameter label = self.talklabel
    label.hide()
    label.resize(300, 50)
    label.setText(words)
    label.move(x, y)
    label.adjustSize()
    label.show()


def input_textbox(input_label, title, ask, x, y, default):  # parameter input_label = self.input_talklabel
    input_label.move(x, y)
    inputmessage, okpressed = QInputDialog.getText(input_label, title, ask, text=default)

    if okpressed and inputmessage != "":
        input_label.hide()
        return inputmessage
    else: return "0"


'''run'''
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UILoader()
    # window.mainWindow.show()
    apply_stylesheet(app, theme='dark_teal.xml')
    pet = DesktopPet(window)
    sys.exit(app.exec_())

# -*- coding: utf-8 -*-
import os
import sqlite3
import time
import subprocess

from PyQt5 import uic
from PyQt5.QtCore import QDateTime, Qt, QDate, QTime
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow


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


class UILoader(QMainWindow):
    def __init__(self):
        # load UI file
        # uiFile = QFile("console.ui")
        # uiFile.open(QFile.ReadOnly)
        # uiFile.close()
        self.ms = ODBC()

        # dynamically create window object from ui file
        self.mainWindow = uic.loadUi("console.ui")
        # 左侧的按钮
        self.showModelBtn = self.mainWindow.showModelBtn
        self.showModelBtn.clicked.connect(lambda value: self.OpenShowModel())
        self.soundsEffectBtn = self.mainWindow.soundsEffectBtn
        self.soundsEffectBtn.setChecked(True)

        self.freeMoveBtn = self.mainWindow.freeMoveBtn
        self.freeMoveBtn.clicked.connect(lambda value: self.OpenFreeMove())
        self.freeMoveBtn = self.mainWindow.freeMoveBtn

        self.soundsEffectBtn = self.mainWindow.soundsEffectBtn
        self.soundsEffectBtn.clicked.connect(lambda value: self.OpenSoundEffect())
        self.soundsEffectBtn = self.mainWindow.soundsEffectBtn

        # slider for text box appear time
        self.dialogLifeLable = self.mainWindow.dialogLifeLable
        self.dialogLifeSlider = self.mainWindow.dialogLifeSlider
        self.dialogLifeSlider.valueChanged.connect(
            lambda value: self.ShowValue(self.dialogLifeLable,
                                         "Duration of the dialog box: " + str(self.dialogLifeSlider.value())))
        self.dialogLifeSlider.valueChanged.connect(lambda value: self.SetDialogLife(self.dialogLifeSlider.value()))

        #slider for frequency of random action
        self.actFrequencyLabel = self.mainWindow.ActFrequencyLable
        self.actFrequencySlider = self.mainWindow.ActFrequencySlider
        self.actFrequencySlider.valueChanged.connect(
            lambda value: self.ShowValue(self.actFrequencyLabel,
                                         "Activity frequency: " + str(self.actFrequencySlider.value())))
        self.actFrequencySlider.valueChanged.connect(lambda value: self.SetActivityFrequency(self.actFrequencySlider.value()))
        self.activityFrequency = 6


        # slider for sound
        self.soundValueLabel = self.mainWindow.soundValueLabel
        self.soundValueSlider = self.mainWindow.soundValueSlider
        self.soundValueSlider.valueChanged.connect(
            lambda value: self.ShowValue(self.soundValueLabel,
                                         "Sound value: " + str(self.soundValueSlider.value())))
        self.soundValueSlider.valueChanged.connect(lambda value: self.SetSoundValue(self.soundValueSlider.value()))
        self.soundValue = 25

        # button for opening file and resetting
        self.resourceFileBtn = self.mainWindow.resourceFileBtn
        self.resourceFileBtn.clicked.connect(lambda value: self.OpenResourceFile())
        self.resetBtn = self.mainWindow.resetBtn
        self.resetBtn.clicked.connect(lambda value: self.Reset())

        # implementation in Schedule interface
        self.dateEdit = self.mainWindow.dateEdit
        self.dateEdit.setDate(QDateTime.currentDateTime().date())
        self.timeEdit = self.mainWindow.timeEdit
        self.timeEdit.setTime(QDateTime.currentDateTime().time())
        self.scheduleEdit = self.mainWindow.ScheduleEdit
        self.addScheduleBtn = self.mainWindow.addScheduleBtn
        self.addScheduleBtn.clicked.connect(
            lambda value: self.addSchedule(self.dateEdit.date(), self.timeEdit.time(), self.scheduleEdit.text()))
        self.scheduleListModel = QStandardItemModel()

        # button in Schedule interface
        self.clearFinishTaskBtn = self.mainWindow.clearFinishTaskBtn
        self.clearFinishTaskBtn.clicked.connect(lambda value: self.clearTask())
        self.openRemindingBtn = self.mainWindow.openRemindingBtn
        self.openRemindingBtn.clicked.connect(lambda value: self.getRemindstate())
        self.stateLable = self.mainWindow.stateLable
        self.stateLable.setStyleSheet("color: red;")

        datas = self.ms.search_all_info('bwl')
        row = len(datas)
        for i in range(row):
            time_to_add = datas[i][1]
            s = str.split(time_to_add, " ")
            d = str.split(s[0], "-")
            qdate = QDate(int(d[0]), int(d[1]), int(d[2]))
            t = str.split(s[1], ":")
            qtime = QTime(int(t[0]), int(t[1]), int(t[2]))
            self.addSchedule1(qdate, qtime, datas[i][0])




    def closeEvent(self, event):
        event.ignore()

    def OpenShowModel(self):
        if self.showModelBtn.isChecked():
            return 1
        else: return 0

    def SetShowModel(self, boolean):
        if boolean:
            self.showModelBtn.setChecked(Qt.Checked)
        else: self.showModelBtn.setChecked(Qt.Unchecked)


    def OpenFreeMove(self):
        if self.freeMoveBtn.isChecked():
            return True
        return False

    def SetFreeMove(self, boolean):
        if boolean:
            self.freeMoveBtn.setChecked(Qt.Checked)
        else: self.freeMoveBtn.setChecked(Qt.Unchecked)

    def OpenSoundEffect(self):
        if self.soundsEffectBtn.isChecked():
            return True
        else: False

    def ShowValue(self, target, textContent):
        target.setText(textContent)

    def SetDialogLife(self, setValue):
        pass

    def GetDialogLife(self):
        return self.dialogLifeSlider.value() * 1000

    def SetSoundValue(self, setValue):
        self.soundValue = setValue

    def GetSoundValue(self):
        if self.OpenSoundEffect():
            return self.soundValue/100
        else: return 0

    def SetActivityFrequency(self, setValue):
        self.activityFrequency = setValue

    def GetActivityFrequency(self):
        return self.activityFrequency*100

    def OpenResourceFile(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.run(["explorer.exe", current_dir])

    # return qdate, qtime and if it's clicked
    def getSchedule(self):
        itemList = []
        for row in range(0, self.scheduleListModel.rowCount() - 1):
            datetimeItem = self.scheduleListModel.item(row, column=0)
            getDateTime = QDateTime.fromString(datetimeItem.text(), Qt.ISODate)
            QDate = getDateTime.date()
            QTime = getDateTime.time()
            is_checked = bool(datetimeItem.checkState())
            taskContent = self.scheduleListModel.item(row, column=1).text()
            itemList.append([QDate, QTime, is_checked, taskContent])
        return itemList

    #add schedule
    def addSchedule(self, Qdate, Qtime, TaskContent):

        def validation(date, time):
            setDateTime = QDateTime(date,time).toSecsSinceEpoch()

            currentDateTime = QDateTime.currentSecsSinceEpoch()

            if self.scheduleEdit.text() == '':
                self.stateLable.setText('please enter your task')
                return False
            if currentDateTime > setDateTime:
                self.stateLable.setText('please enter a correct time')
                return False
            return True

        def changeFormat(inputNum):
            if inputNum < 10:
                inputNum = '0'+str(inputNum)
            return inputNum


        if validation(Qdate, Qtime):

            self.stateLable.setText('') # hide text beside button
            Qdate = Qdate.getDate()
            timeItem = QStandardItem('%s-%s-%s %s:%s:%s' % (changeFormat(Qdate[0]), changeFormat(Qdate[1]), changeFormat(Qdate[2])
                                                              ,changeFormat(Qtime.hour()),changeFormat(Qtime.minute()),changeFormat(Qtime.second())))

            timeItem.setCheckable(True)
            timeItem.setEditable(False)
            timeItem.setCheckState(Qt.Unchecked)  # 设置复选框的默认状态
            taskItem = QStandardItem(TaskContent)
            taskItem.setEditable(False)

            self.scheduleListModel.setHorizontalHeaderLabels(['time','Task'])
            self.scheduleListModel.appendRow([timeItem,taskItem])
            # sort current schedules by time
            self.scheduleListModel.sort(0, Qt.AscendingOrder)
            self.mainWindow.ScheduleListView.show()
            self.mainWindow.ScheduleListView.setModel(self.scheduleListModel)
            time_to_add = timeItem.text()
            s = str.split(time_to_add, " ")
            d = str.split(s[0], "-")
            qdate = QDate(int(d[0]), int(d[1]), int(d[2]))
            t = str.split(s[1], ":")
            qtime = QTime(int(t[0]), int(t[1]), int(t[2]))
            t = QDateTime(qdate, qtime)
            self.ms.add_info('Bwl',
                             [[TaskContent, t.toString(Qt.ISODate).replace('T', ' '), str(t.toMSecsSinceEpoch())[0:-3]]])

            return True

        return False

    def addSchedule1(self, Qdate, Qtime, TaskContent):


        def changeFormat(inputNum):
            if inputNum < 10:
                inputNum = '0'+str(inputNum)
            return inputNum

        self.stateLable.setText('')
        Qdate = Qdate.getDate()
        timeItem = QStandardItem(
            '%s-%s-%s %s:%s:%s' % (changeFormat(Qdate[0]), changeFormat(Qdate[1]), changeFormat(Qdate[2])
                                   , changeFormat(Qtime.hour()), changeFormat(Qtime.minute()),
                                   changeFormat(Qtime.second())))

        timeItem.setCheckable(True)
        timeItem.setEditable(False)
        timeItem.setCheckState(Qt.Unchecked)  # 设置复选框的默认状态
        taskItem = QStandardItem(TaskContent)
        taskItem.setEditable(False)

        self.scheduleListModel.setHorizontalHeaderLabels(['time', 'Task'])
        self.scheduleListModel.appendRow([timeItem, taskItem])

        self.scheduleListModel.sort(0, Qt.AscendingOrder)

        self.mainWindow.ScheduleListView.show()
        self.mainWindow.ScheduleListView.setModel(self.scheduleListModel)
        return 1

    # delete schedule by index(row)
    def deleteTask(self, row):
        if row in range(0, self.scheduleListModel.rowCount()):
            self.scheduleListModel.removeRow(row)
            # self.ms.del_info('bwl', data[2])

    # click the schedule
    def setChecked(self, row):
        if row in range(0, self.scheduleListModel.rowCount()):
            checkBox = self.scheduleListModel.item(row, column=0)
            checkBox.setCheckState(Qt.Checked)

    def getRemindstate(self):
        if self.openRemindingBtn.isChecked():
            return True
        else: return False

    # clear clicked tasks
    def clearTask(self):

        for row in range(self.scheduleListModel.rowCount()-1, -1, -1):
            # get clicked status in every row
            checkBox_state = self.scheduleListModel.item(row, column=0).checkState()
            time_to_add = self.scheduleListModel.item(row, column=0).text()
            s = str.split(time_to_add, " ")
            d = str.split(s[0], "-")
            qdate = QDate(int(d[0]), int(d[1]), int(d[2]))
            t = str.split(s[1], ":")
            qtime = QTime(int(t[0]), int(t[1]), int(t[2]))
            t = QDateTime(qdate, qtime)
            self.ms.del_info('bwl', str(t.toMSecsSinceEpoch())[0:-3])
            if checkBox_state:
                self.scheduleListModel.removeRow(row)


    def Reset(self):
        self.showModelBtn.setChecked(Qt.Checked)
        self.freeMoveBtn.setChecked(Qt.Checked)
        self.soundsEffectBtn.setChecked(Qt.Checked)

        self.dialogLifeSlider.setValue(3)
        self.actFrequencySlider.setValue(6)
        self.soundValueSlider.setValue(25)


# app = QApplication()
# window = UILoader()
# window.mainWindow.show()
# app.exec_()

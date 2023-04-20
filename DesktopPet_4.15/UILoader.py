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
        self.path = os.path.join(os.getcwd(),  'datas.db')

    def GetConnect(self):
        self.con = sqlite3.connect(self.path)
        cur = self.con.cursor()
        if not cur:
            raise (NameError, '连接数据库失败')
        else:
            return cur

    def add_info(self, table_name, data):
        # 添加信息
        value_len = ','.join('?' * len(data[0]))  # 计算数据长度
        sql = 'INSERT INTO %s VALUES (%s)' % (str(table_name), value_len)
        cur = self.GetConnect()
        cur.executemany(sql, data)
        self.con.commit()

    def del_info(self, table_name, name):
        # 添加信息
        sql = 'delete from %s where Time2 like "%s"' % (str(table_name), str(name))

        cur = self.GetConnect()
        cur.execute(sql)
        self.con.commit()

    def xiugai_info(self, table_name, text, data):
        # 添加信息
        self.del_info(table_name, text)
        self.add_info(table_name, data)


    def search_all_info(self, table_name):
        # 添加信息
        sql = 'select * from %s' % str(table_name)

        cur = self.GetConnect()
        datas = cur.execute(sql)
        return [i for i in datas]

    def search_info_by(self):
        # 添加信息
        pass
    def creat_(self):
        # 使用 cursor（）方法创建一个游标对象 cursor
        cursor = self.GetConnect()
        sql = '''CREATE TABLE Bwl
                           (
                           Texts          CHAR(100),
                           Time1          CHAR(100)  ,
                            Time2     CHAR(300));'''
        try:
            cursor.execute(sql)
            # 提交到数据库执行
            self.con.commit()
            print('CREATE [user_info] TABLE SUCCESS.')
        # 捕获与数据库相关的错误
        except:
            print('CREATE TABLE FAILED')
            # 如果发生错误就回滚
            self.con.rollback()
        finally:
            # 关闭数据库连接
            self.con.close()
ms = ODBC()


class UILoader(QMainWindow):
    def __init__(self):
        # 加载UI文件
        # uiFile = QFile("console.ui")
        # uiFile.open(QFile.ReadOnly)
        # uiFile.close()
        self.ms = ODBC()

        # 从ui文件中动态创建一个相应的窗口对象
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

        # 控制移动速度的滑块
        self.dialogLifeLable = self.mainWindow.dialogLifeLable
        self.dialogLifeSlider = self.mainWindow.dialogLifeSlider
        self.dialogLifeSlider.valueChanged.connect(
            lambda value: self.ShowValue(self.dialogLifeLable,
                                         "Duration of the dialog box: " + str(self.dialogLifeSlider.value())))
        self.dialogLifeSlider.valueChanged.connect(lambda value: self.SetDialogLife(self.dialogLifeSlider.value()))

        #控制移动频率的滑块
        self.actFrequencyLabel = self.mainWindow.ActFrequencyLable
        self.actFrequencySlider = self.mainWindow.ActFrequencySlider
        self.actFrequencySlider.valueChanged.connect(
            lambda value: self.ShowValue(self.actFrequencyLabel,
                                         "activity frequency: " + str(self.actFrequencySlider.value())))
        self.actFrequencySlider.valueChanged.connect(lambda value: self.SetActivityFrequency(self.actFrequencySlider.value()))
        self.activityFrequency = 6


        # 控制音量大小的滑块
        self.soundValueLabel = self.mainWindow.soundValueLabel
        self.soundValueSlider = self.mainWindow.soundValueSlider
        self.soundValueSlider.valueChanged.connect(
            lambda value: self.ShowValue(self.soundValueLabel,
                                         "sound value: " + str(self.soundValueSlider.value())))
        self.soundValueSlider.valueChanged.connect(lambda value: self.SetSoundValue(self.soundValueSlider.value()))
        self.soundValue = 25

        # 主界面右下角两个按钮
        self.resourceFileBtn = self.mainWindow.resourceFileBtn
        self.resourceFileBtn.clicked.connect(lambda value: self.OpenResourceFile())
        self.resetBtn = self.mainWindow.resetBtn
        self.resetBtn.clicked.connect(lambda value: self.Reset())

        # 日程界面的操作栏
        self.dateEdit = self.mainWindow.dateEdit
        self.dateEdit.setDate(QDateTime.currentDateTime().date())
        self.timeEdit = self.mainWindow.timeEdit
        self.timeEdit.setTime(QDateTime.currentDateTime().time())
        self.scheduleEdit = self.mainWindow.ScheduleEdit
        self.addScheduleBtn = self.mainWindow.addScheduleBtn
        self.addScheduleBtn.clicked.connect(
            lambda value: self.addSchedule(self.dateEdit.date(), self.timeEdit.time(), self.scheduleEdit.text()))
        self.scheduleListModel = QStandardItemModel()

        # 日程界面按钮
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
        print('set value:',setValue)
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

    # 获取日程表，返回Qdate, QTime, 是否勾选, 日程内容
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

    #设置日程
    def addSchedule(self, Qdate, Qtime, TaskContent):

        def validation(date, time):

            # 该方法返回自1970年1月1日以来的毫秒数
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

            self.stateLable.setText('') # 隐藏按钮侧边的文字
            Qdate = Qdate.getDate()
            timeItem = QStandardItem('%s-%s-%s %s:%s:%s' % (changeFormat(Qdate[0]), changeFormat(Qdate[1]), changeFormat(Qdate[2])
                                                              ,changeFormat(Qtime.hour()),changeFormat(Qtime.minute()),changeFormat(Qtime.second())))

            timeItem.setCheckable(True)
            timeItem.setCheckState(Qt.Unchecked)  # 设置复选框的默认状态
            taskItem = QStandardItem(TaskContent)
            self.scheduleListModel.setHorizontalHeaderLabels(['time','Task'])
            self.scheduleListModel.appendRow([timeItem,taskItem])
            # 显示列表前对时间进行排序
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

        return False  # 格式不对返回False

    def addSchedule1(self, Qdate, Qtime, TaskContent):


        def changeFormat(inputNum):
            if inputNum < 10:
                inputNum = '0'+str(inputNum)
            return inputNum

        self.stateLable.setText('')  # 隐藏按钮侧边的文字
        Qdate = Qdate.getDate()
        timeItem = QStandardItem(
            '%s-%s-%s %s:%s:%s' % (changeFormat(Qdate[0]), changeFormat(Qdate[1]), changeFormat(Qdate[2])
                                   , changeFormat(Qtime.hour()), changeFormat(Qtime.minute()),
                                   changeFormat(Qtime.second())))

        timeItem.setCheckable(True)
        timeItem.setCheckState(Qt.Unchecked)  # 设置复选框的默认状态
        taskItem = QStandardItem(TaskContent)

        self.scheduleListModel.setHorizontalHeaderLabels(['time', 'Task'])
        self.scheduleListModel.appendRow([timeItem, taskItem])
        # 显示列表前对时间进行排序
        self.scheduleListModel.sort(0, Qt.AscendingOrder)

        self.mainWindow.ScheduleListView.show()
        self.mainWindow.ScheduleListView.setModel(self.scheduleListModel)
        return 1

    # 通过行数删除日程，行数和getSchedule返回的列表索引相同
    def deleteTask(self, row):
        if row in range(0, self.scheduleListModel.rowCount()):
            self.scheduleListModel.removeRow(row)
            # self.ms.del_info('bwl', data[2])

    # 设置任务已完成
    def setChecked(self, row):
        if row in range(0, self.scheduleListModel.rowCount()):
            checkBox = self.scheduleListModel.item(row, column=0)
            checkBox.setCheckState(Qt.Checked)

    def getRemindstate(self):
        if self.openRemindingBtn.isChecked():
            return True
        else: return False

    # 清除已经勾选（完成）的任务
    def clearTask(self):
        print('work')
        # 反向遍历，避免删除时行数改变
        for row in range(self.scheduleListModel.rowCount()-1, -1, -1):
            # 获取每一行的勾选框
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
        self.actFrequencySlider.setValue(3)
        self.soundValueSlider.setValue(50)


# app = QApplication()
# window = UILoader()
# window.mainWindow.show()
# app.exec_()

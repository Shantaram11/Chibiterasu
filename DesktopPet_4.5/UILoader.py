# -*- coding: utf-8 -*-
import os
import subprocess

from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtWidgets import QApplication, QMessageBox, QWidget, QHBoxLayout, QSizePolicy, QHeaderView
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile, Qt, QSize, QDateTime


class UILoader:
    def __init__(self):
        # 加载UI文件
        uiFile = QFile("console.ui")
        uiFile.open(QFile.ReadOnly)
        uiFile.close()

        # 从ui文件中动态创建一个相应的窗口对象
        self.mainWindow = QUiLoader().load(uiFile)
        # 左侧的按钮
        self.showModelBtn = self.mainWindow.showModelBtn
        self.showModelBtn.clicked.connect(self.ShowModel)
        self.soundsEffectBtn = self.mainWindow.soundsEffectBtn

        self.freeMoveBtn = self.mainWindow.freeMoveBtn
        self.freeMoveBtn.clicked.connect(self.OpenFreeMove)
        self.freeMoveBtn = self.mainWindow.freeMoveBtn

        self.soundsEffectBtn = self.mainWindow.soundsEffectBtn
        self.soundsEffectBtn.clicked.connect(self.OpenSoundEffect)
        self.soundsEffectBtn = self.mainWindow.soundsEffectBtn

        # 控制移动速度的滑块
        self.walkingSpeedLable = self.mainWindow.walkingSpeedLable
        self.walkingSpeedSlider = self.mainWindow.walkingSpeedSlider
        self.walkingSpeedSlider.valueChanged.connect(
            lambda value: self.ShowValue(self.walkingSpeedLable,
                                         "walking speed: " + str(self.walkingSpeedSlider.value())))
        self.walkingSpeedSlider.valueChanged.connect(lambda value: self.SetWalkingSpeed(self.walkingSpeedSlider.value()))

        # 控制音量大小的滑块
        self.soundValueLabel = self.mainWindow.soundValueLabel
        self.soundValueSlider = self.mainWindow.soundValueSlider
        self.soundValueSlider.valueChanged.connect(
            lambda value: self.ShowValue(self.soundValueLabel,
                                         "sound value: " + str(self.soundValueSlider.value())))
        self.soundValueSlider.valueChanged.connect(lambda value: self.SetSoundValue(self.soundValueSlider.value()))

        # 主界面右下角两个按钮
        self.resourceFileBtn = self.mainWindow.resourceFileBtn
        self.resourceFileBtn.clicked.connect(self.OpenResourceFile)
        self.resetBtn = self.mainWindow.resetBtn
        self.resetBtn.clicked.connect(self.Reset)

        # 日程界面的操作栏
        self.dateEdit = self.mainWindow.dateEdit
        self.dateEdit.setDate(QDateTime.currentDateTime().date())
        self.timeEdit = self.mainWindow.timeEdit
        self.timeEdit.setTime(QDateTime.currentDateTime().time())
        self.scheduleEdit = self.mainWindow.ScheduleEdit
        self.addScheduleBtn = self.mainWindow.addScheduleBtn
        self.addScheduleBtn.clicked.connect(self.addSchedule)
        self.scheduleListModel = QStandardItemModel()
        # 日程界面按钮
        self.clearFinishTaskBtn = self.mainWindow.clearFinishTaskBtn
        self.clearFinishTaskBtn.clicked.connect(self.clearTask)
        self.stateLable = self.mainWindow.stateLable
        self.stateLable.setStyleSheet("color: red;")

    def ShowModel(self):
        if self.showModelBtn.isChecked():
            print('show model')
        pass

    def OpenFreeMove(self):
        if self.freeMoveBtn.isChecked():
            print('free move')
        pass

    def OpenSoundEffect(self):
        if self.soundsEffectBtn.isChecked():
            print('sound effect')
        pass

    def ShowValue(self, target, textContent):
        target.setText(textContent)

    def SetWalkingSpeed(self, setValue):
        print('set value:',setValue)
        pass

    def SetSoundValue(self, setValue):
        print('set value:', setValue)
        pass

    def OpenResourceFile(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.run(["explorer.exe", current_dir])

    def addSchedule(self):

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
            return  inputNum


        Qdate = self.dateEdit.date()
        Qtime = self.timeEdit.time()
        if validation(Qdate, Qtime):
            self.stateLable.setText('') # 隐藏按钮侧边的文字
            Qdate = Qdate.getDate()
            timeItem = QStandardItem('%s-%s-%s %s:%s:%s' % (changeFormat(Qdate[0]), changeFormat(Qdate[1]), changeFormat(Qdate[2])
                                                              ,changeFormat(Qtime.hour()),changeFormat(Qtime.minute()),changeFormat(Qtime.second())))
            timeItem.setCheckable(True)
            timeItem.setCheckState(Qt.Unchecked)  # 设置复选框的默认状态
            taskItem = QStandardItem(self.scheduleEdit.text())
            self.scheduleListModel.setHorizontalHeaderLabels(['time','Task'])
            self.scheduleListModel.appendRow([timeItem,taskItem])
            # 显示列表前对时间进行排序
            self.scheduleListModel.sort(0, Qt.AscendingOrder)
            self.mainWindow.ScheduleListView.show()
            self.mainWindow.ScheduleListView.setModel(self.scheduleListModel)

    def clearTask(self):
        #反向遍历，避免删除时行数改变
        for row in range(self.scheduleListModel.rowCount()-1, -1, -1):
            # 获取每一行的勾选框
            checkBox_state = self.scheduleListModel.item(row, column=0).checkState()
            if checkBox_state:
                self.scheduleListModel.removeRow(row)
    def Reset(self):
        pass



app = QApplication()
window = UILoader()
window.mainWindow.show()
app.exec_()

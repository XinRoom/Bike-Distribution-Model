from sys import argv, exit
from os.path import exists
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox,  QWidget
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
#from .Ui_window import Ui_MainWindow
from core import matplot
from core.globalmap import GlobalMap
import time
from core.UI_dig import Dig_change

class Main(QMainWindow):
    '''主窗口'''
    
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        QMainWindow.__init__(self)
        loadUi('core/window.ui', self) 
        #self.setupUi(self)
        self.setWindowIcon(QIcon('main.ico'))
        
        '''pushButton等控件信号'''
        self.time_point_training.clicked.connect(self.clickedTime_point_training)
        self.pushButton_pause.clicked.connect(self.clickedPause)
        #self.dynamic_display.clicked.connect(self.dynamic_display_click)
        self.change_dynamic.clicked.connect(self.change_dynamic_click)
        self.change_hot.clicked.connect(self.change_hot_click)
        self.commandLink_about.clicked.connect(self.about)
        self.time_point.currentIndexChanged.connect(self.currentIndexChanged)
        
        '''newForm'''
        self.new_dig.clicked.connect(self.test)
        #self.close_signal.connect(self.newForm.close)
        
        '''widget_plot，数据可视化'''
        self.main_widget = QWidget(self)
        self.widget_plot = matplot.MyccMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.verticalLayout_cell.addWidget(self.widget_plot)
        
        GlobalMap().set(running_global = 0)
        self.initial_value() #初始化全局变量
        self.timer = QTimer(self) #动态更新全局变量
        self.timer.timeout.connect(self.update_value)
        self.global_temp= GlobalMap().get('all')
        #self.main_widget.setFocus()
    
#    def closeEvent(self, event):
#        #self.close_signal.emit()
#        self.close()
        
    def update_value(self):
        '''更新UI状态显示'''
        self.global_temp= GlobalMap().get('all')
        try:
            if not GlobalMap().get('running_global'):
                time.sleep(0.3)
                self.timer.stop()
                self.initial_value()
            #print(self.global_temp)
            self.progress_num.setValue(self.global_temp['progress_num'])
            self.iter_times.setText(str(self.global_temp['times']))
            self.loss_now.setText(str(self.global_temp['loss_now']))
            self.used_time.display(self.global_temp['used_time'])
        except:
            pass
    
    def initial_value(self):
        '''初始化全局变量'''
        #print(temp)
        GlobalMap().set(max_itera = self.max_itera.value(), 
                neurons_num = self.neurons_num.value(), 
                dg_initial = self.dg_initial.value(), 
                dg_adaptive = self.dg_adaptive.value(), 
                precision = self.precision.value(), 
                save_question = 1, 
                save_nopass = 1, 
                temp_path = 'temp', 
                fix_auto = self.fix_auto.isChecked()
            )
        for i in range(24):
            if exists('ckpt/model-'+ str(i) +'.ckpt.index'):
                '''每个小时点的训练状况'''
                {0:self.checkBox_0.setChecked, 
                1:self.checkBox_1.setChecked, 
                2:self.checkBox_2.setChecked, 
                3:self.checkBox_3.setChecked, 
                4:self.checkBox_4.setChecked, 
                5:self.checkBox_5.setChecked, 
                6:self.checkBox_6.setChecked, 
                7:self.checkBox_7.setChecked, 
                8:self.checkBox_8.setChecked, 
                9:self.checkBox_9.setChecked, 
                10:self.checkBox_10.setChecked,  
                11:self.checkBox_11.setChecked, 
                12:self.checkBox_12.setChecked, 
                13:self.checkBox_13.setChecked, 
                14:self.checkBox_14.setChecked, 
                15:self.checkBox_15.setChecked, 
                16:self.checkBox_16.setChecked, 
                17:self.checkBox_17.setChecked, 
                18:self.checkBox_18.setChecked, 
                19:self.checkBox_19.setChecked, 
                20:self.checkBox_20.setChecked, 
                21:self.checkBox_21.setChecked, 
                22:self.checkBox_22.setChecked, 
                23:self.checkBox_23.setChecked, 
                }.get(i)(True)

    
    def clickedTime_point_training(self):
        '''点击单时间的预测'''
        self.initial_value()
        if GlobalMap().get('running_global'):
            QMessageBox.warning(self, "Warning","Is_running!!!\nMaybe you want to click '停止当前任务'")
            return
        
        GlobalMap().set(running_global = 1, running_status = 0, time_point = self.time_point.currentIndex(), fix_seed = self.fix_seed.isChecked())
        self.update_value()
        
        if exists('ckpt/model-'+ str(self.global_temp['time_point']) +'.ckpt.index') and GlobalMap().get('save_question'):         #判断模型是否存在  
            self.save_question()
        
        self.timer.start(600)
        self.verticalLayout_cell.removeWidget(self.widget_plot)
        self.widget_plot = matplot.MySticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.verticalLayout_cell.addWidget(self.widget_plot)
        self.widget_plot.start()
    
        
    def dynamic_display_click(self):
        '''24小时动态分布图'''
        if GlobalMap().get('running_global'):
            QMessageBox.warning(self, "Warning","Is_running!!!\nMaybe you want to click '停止当前任务'")
            return
        self.initial_value()
        GlobalMap().set(running_global = 1, running_status = 1, time_point = self.time_point.currentIndex(), fix_seed = self.fix_seed.isChecked())
        
        self.update_value()
        
        self.timer.start(1000)
        self.verticalLayout_cell.removeWidget(self.widget_plot)
        self.widget_plot = matplot.MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.verticalLayout_cell.addWidget(self.widget_plot)
        self.widget_plot.start()
    
    def change_dynamic_click(self):
        '''23小时各小时变化动态图'''
        if GlobalMap().get('running_global'):
            QMessageBox.warning(self, "Warning","Is_running!!!\nMaybe you want to click '停止当前任务'")
            return
        self.initial_value()
        GlobalMap().set(running_global = 1, running_status = 2, time_point = self.time_point.currentIndex(), fix_seed = self.fix_seed.isChecked())
        
        self.update_value()
        
        self.timer.start(1000)
        self.verticalLayout_cell.removeWidget(self.widget_plot)
        self.widget_plot = matplot.MyChangeDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.verticalLayout_cell.addWidget(self.widget_plot)
        self.widget_plot.start()
    
    def change_hot_click(self):
        '''热力图对比'''
        if GlobalMap().get('running_global'):
            QMessageBox.warning(self, "Warning","Is_running!!!\nMaybe you want to click '停止当前任务'")
            return
        self.initial_value()
        GlobalMap().set(running_global = 1, running_status = 3, time_point = self.time_point.currentIndex(), fix_seed = self.fix_seed.isChecked())
        
        self.update_value()
        
        self.timer.start(1000)
        self.verticalLayout_cell.removeWidget(self.widget_plot)
        self.widget_plot = matplot.MyHotMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.verticalLayout_cell.addWidget(self.widget_plot)
        self.widget_plot.start()
    
    def currentIndexChanged(self, i):
        '''分时间的推荐精度参数'''
        if i == 0:
            self.precision.setValue(25.9)
        elif i == 2 or i == 4 or i == 5:
            self.precision.setValue(0.11)
        elif i == 6:
            self.precision.setValue(0.7)
        elif i == 15:
            self.precision.setValue(0.75)
        elif i == 8:
            self.precision.setValue(1.8)
        elif i == 18 or i == 21:
            self.precision.setValue(2.2)
        elif i == 20:
            self.precision.setValue(2.85)
        elif i == 12:
            self.precision.setValue(1.7)
        elif i == 16:
            self.precision.setValue(1.45)
        elif i == 14:
            self.precision.setValue(1.55)
        elif i == 11 or i == 17:
            self.precision.setValue(0.91)
        elif i == 10:
            self.precision.setValue(1.4)
        elif i == 13:
            self.precision.setValue(1.2)
        elif i == 19:
            self.precision.setValue(3.5)
        elif i == 9:
            self.precision.setValue(2.5)
        elif i == 22 or i == 23:
            self.precision.setValue(1.95)
        elif i == 3:
            self.precision.setValue(0.2)
        elif i == 7:
            self.precision.setValue(0.52)
        else:
            self.precision.setValue(0.42)
        
        
        
    def clickedPause(self):
        '''停止当前任务'''
        self.widget_plot.pause()
    
    def save_question(self):
        '''询问是否使用历史训练数据，提高速度'''
        reply = QMessageBox.question(self, '已有历史训练数据',
            "你还要重新训练吗?", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            GlobalMap().set( 
                save_nopass = 0
            )
            
        GlobalMap().set( 
            save_question = 0
        )


    def dig_change_accept(self):
        '''23小时各小时变化动态图'''
        if GlobalMap().get('running_global'):
            QMessageBox.warning(self, "Warning","Is_running!!!\nMaybe you want to click '停止当前任务'")
            return
        self.initial_value()
        GlobalMap().set(running_global = 1, running_status = 2, time_point = self.time_point.currentIndex(), fix_seed = self.fix_seed.isChecked())
        
        self.update_value()
        
        self.timer.start(1000)
        self.verticalLayout_cell.removeWidget(self.widget_plot)
        self.widget_plot = matplot.MyDig_ChangeMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        self.verticalLayout_cell.addWidget(self.widget_plot)
        self.widget_plot.start()
    
    def test(self):
        self.dig_change = Dig_change(self)
        self.dig_change.accepted.connect(self.dig_change_accept)
        self.dig_change.exec_()
#        dialog = Dig_change(self)
#        if dialog.exec_():
#            pass
    def about(self):
        '''关于'''
        QMessageBox.about(self, "About","Copyright@ 2018 XinRoom\n\n"
        "----参数基本说明----\n"
        "如果当前精度出现nan可以调节初始学习率(降低或增大)\t\n"
                    )
        

def run():
    '''实例化'''
    #QApplication.setStyle(QStyleFactory.create("Fusion"))
    app = QApplication(argv)
    w=Main()
    w.show()
    exit(app.exec_())

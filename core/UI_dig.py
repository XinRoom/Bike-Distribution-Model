from numpy.random import uniform
from numpy import append
from PyQt5.QtWidgets import QMessageBox,  QDialog, QLabel
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen
from PyQt5.QtCore import QRect, Qt, pyqtSignal
from core.globalmap import GlobalMap


class Dig_change(QDialog):
    
    
    def __init__(self, parent=None):
        super(Dig_change, self).__init__(parent)
        loadUi('core/dig_change.ui', self) 
        self.setWindowIcon(QIcon('main.ico'))
        
        self.lb = myLabel()
        self.lb.__init__()
        self.lb.setCursor(Qt.CrossCursor)
        
        png=QPixmap('core/map2.png')
        self.lb.setScaledContents(True)
        self.lb.setPixmap(png)
        self.horizontalLayout.addWidget(self.lb)
        self.lb.chage_move_signal.connect(self.chage_move)
        
        QMessageBox.information(self, '提示', 
                    '---操作说明---\n'
                    '左键单击拖动选择区域，弹出对话框输入单车数量，确认即可\n'
            )
    
    def chage_move(self, strr):
        self.label_text.setText(strr)
    


class Dig_setting(QDialog):

    def __init__(self, parent=None):
        super(Dig_setting, self).__init__(parent)
        loadUi('core/dig_setting.ui', self) 
        self.setWindowIcon(QIcon('main.ico'))
        self.accepted.connect(self.ciled_ok)
        
    def chage_move(self, strr):
        self.label_text.setText(strr)
    
        
    def ciled_ok(self):
        QMessageBox.information(self, '提示', 
            '---注意---\n'
            '由于训练集过少、精度不够和当地摩拜用量较少，效果并不明显，仅作为一个想法展示\n'
            '只展示到3：00\n'
            '希望未来能有更多精确、连续的数据供我们学习\n'
        )


class myLabel(QLabel):
    x0 = 0
    y0 = 0
    x1 = 0
    y1 = 0
    flag = False
    chage_move_signal = pyqtSignal(str)
    cum = [[], []]
    accept_move = [[]]
    mun = 100
    
    def __init__(self):
        super().__init__()
        self.accept_move = [[]]
        self.cum = [[], []]

    def mousePressEvent(self,event):
        self.flag = True
        self.x0 = event.x()
        self.y0 = event.y()
    def mouseReleaseEvent(self,event):
        self.flag = False
        self.x_n0 = self.x0/8208.95522 + 112.150
        self.y_n0 = self.y0/8763.15789 + 30.309
        self.dialog_setting = Dig_setting(self)
        self.dialog_setting.accepted.connect(self.accept)
        self.dialog_setting.exec_()

    def accept(self):
        self.mun = self.dialog_setting.spinBox.value()
        self.cum[0]=append(self.cum[0], uniform(self.x_n0,self.x_n1,size=(1,self.mun)))
        self.cum[1]=append(self.cum[1], uniform(self.y_n0,self.y_n1,size=(1,self.mun)))
        self.accept_move += [[self.x0, self.y0, self.x1-self.x0, self.y1-self.y0, self.mun]]
        GlobalMap().set(userdefined = self.cum, )
        #print(self.cum)
        
    
    def mouseMoveEvent(self,event):
        if self.flag:
            self.x1 = event.x()
            self.y1 = event.y()
            self.update()
            self.x_n1 = self.x1/8208.95522 + 112.150
            self.y_n1 = self.y1/8763.15789 + 30.309
            self.chage_move_signal.emit(str(self.x_n1)+ ';' + str(self.y_n1))

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red,4,Qt.SolidLine))
        rect =QRect(self.x0, self.y0, self.x1-self.x0, self.y1-self.y0)
        painter.drawRect(rect)
        if self.accept_move[1:]:
            for i in self.accept_move[1:]:
                cc = QRect(i[0], i[1], i[2], i[3])
                painter.drawRect(cc)
                painter.drawText(cc, Qt.AlignCenter, str(i[4]))


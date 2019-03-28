import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.pyplot import imread
from matplotlib import style
style.use('classic')
from scipy.stats import gaussian_kde
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import  QSizePolicy
from core import NeuralNetwork as NN
from core.datadone import dataclear
from pandas import DataFrame, read_csv, merge
from core.globalmap import GlobalMap
from os.path import exists
from time import sleep

class Worker(QThread):
    '''用于UI与数据计算分离，防止界面卡死'''
    changed_signal = pyqtSignal(np.ndarray, np.ndarray)
    
    def __init__(self, sec=0, parent=None):
        super().__init__(parent)
        self.working = True
        self.sec = sec
        
    def __del__(self):
        self.working = False
        self.wait()
        
    def run(self):
        if self.working == True:
            times = GlobalMap().get('time_point')
            GlobalMap().set(progress_num = 0)
            
            lists = []
            for i in range(24):
                lists += [i]
            
            GlobalMap().set(progress_num = 2 )
            
            if exists('db/temp/20180515.csv') and exists('db/temp/20180516.csv'):
                temp1 = DataFrame(read_csv('db/temp/20180515.csv' ,header=0))
                temp2 = DataFrame(read_csv('db/temp/20180516.csv' ,header=0))
            else:
                temp1 = dataclear(20180515).run()
                temp2 = dataclear(20180516).run()
            
            GlobalMap().set(progress_num = 5 )
            
            temp11 = temp1[temp1['time'] == lists[times-1]]
            temp12 = temp1[temp1['time'] == lists[times]]
            temp1112 = merge(temp11, temp12, how='outer',on='id') .dropna()
            
            '''begin 另一种数据处理方式'''
#            temp1_x = DataFrame(read_csv('db/temp/20180515-x.csv' ,header=0))
#            temp1_y = DataFrame(read_csv('db/temp/20180515-y.csv' ,header=0))
#            temp2_x = DataFrame(read_csv('db/temp/20180516-x.csv' ,header=0))
#            temp2_y = DataFrame(read_csv('db/temp/20180516-y.csv' ,header=0))
#            
#            temp11_x = temp1_x[str(lists[times])]
#            temp11_y = temp1_y[str(lists[times])]
#            temp12_x = temp2_x[str(lists[times])]
#            temp12_y = temp2_y[str(lists[times])]
#            
#            temp21_x = temp1_x[str(lists[times+1])]
#            temp21_y = temp1_y[str(lists[times+1])]
#            temp22_x = temp2_x[str(lists[times+1])]
#            temp22_y = temp2_y[str(lists[times+1])]
#            
#            cc01 = np.vstack((temp11_x, temp11_y))
#            cc02 = np.vstack((temp21_x, temp21_y))
#            cc03 = np.vstack((temp12_x, temp12_y))
#            cc04 = np.vstack((temp22_x, temp22_y))
            '''end'''
            
            temp21 = temp2[temp2['time'] == lists[times-1]]
            temp22 = temp2[temp2['time'] == lists[times]]
            temp2122 = merge(temp21, temp22, how='outer',on='id') .dropna()
            
            temp000 = np.vstack((temp1112['x_x'],temp1112['y_x']))
            temp001 = np.vstack((temp1112['x_y'],temp1112['y_y']))
            
            temp020 = np.vstack((temp2122['x_x'],temp2122['y_x']))
            temp021 = np.vstack((temp2122['x_y'],temp2122['y_y']))
            
            #用20180515 T 和 T+1 时刻的训练 来预测  20180516 T 时刻 在 T+1 时刻的分布情况
            cells_array = np.array(NN.main(temp000, temp001, temp020 ))
            #cells_array = np.array(NN.main(cc01, cc02, cc03 ))
            
            np.save(GlobalMap().get('temp_path')+'/test'+str(times), cells_array)
            GlobalMap().set(progress_num = 100 )
            
            self.changed_signal.emit(cells_array, temp021)
            

class Worker_2(QThread):
    '''24小时动态图线程'''
    
    changed2_signal = pyqtSignal(int) # 信号类型：str
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.working = True
        
    def __del__(self):
        self.working = False
        self.wait()
        
    def run(self):
        if self.working == True:
            times = GlobalMap().get('time_point')
            GlobalMap().set(progress_num = 0)
            
            lists = []
            for i in range(24):
                lists += [i]
            
            GlobalMap().set(progress_num = 2 )
            
            if exists('db/temp/20180515.csv') and exists('db/temp/20180516.csv'):
                temp1 = DataFrame(read_csv('db/temp/20180515.csv' ,header=0))
                temp2 = DataFrame(read_csv('db/temp/20180516.csv' ,header=0))
            else:
                temp1 = dataclear(20180515).run()
                temp2 = dataclear(20180516).run()
            
            GlobalMap().set(progress_num = 5 )
            
            temp11 = temp1[temp1['time'] == lists[times-1]]
            temp12 = temp1[temp1['time'] == lists[times]]
            temp1112 = merge(temp11, temp12, how='outer',on='id') .dropna()
            
            temp21 = temp2[temp2['time'] == lists[times-1]]
            temp22 = temp2[temp2['time'] == lists[times]]
            temp2122 = merge(temp21, temp22, how='outer',on='id') .dropna()
            
            temp000 = np.vstack((temp1112['x_x'],temp1112['y_x']))
            temp001 = np.vstack((temp1112['x_y'],temp1112['y_y']))
            
            temp020 = np.vstack((temp2122['x_x'],temp2122['y_x']))
            #temp021 = np.vstack((temp2122['x_y'],temp2122['y_y']))
            
            cells_array = np.array(NN.main(temp000, temp001, temp020 ))
            
            np.save(GlobalMap().get('temp_path')+'/test'+str(times), cells_array)
            
            GlobalMap().set(progress_num = 100 ,running_global = 0 )
            
            self.changed2_signal.emit(1)
    
class MyMplCanvas(FigureCanvas):
    """这是一个窗口部件，即QWidget（当然也是FigureCanvasAgg）"""

    def __init__(self, parent=None, width=6, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        
        self.fig.subplots_adjust(left=0.08, bottom=0.08, right=0.92, top=0.92, hspace=0.04, wspace=0.02)
        
        self.axes = self.fig.add_subplot(111)
        
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class MyChangeDynamicMplCanvas(MyMplCanvas):
    '''23小时各小时变化动态图'''
    
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
    
    def start(self):
        self.times = 1
        GlobalMap().set(progress_num = 0)
        self.lists = []
        self.changenum00 = []
        self.changenum01 = []
        for i in range(24):
            self.lists += [i]
            
        if exists('db/temp/20180515.csv'):
            self.temp1 = DataFrame(read_csv('db/temp/20180515.csv' ,header=0))
        else:
            self.temp1 = dataclear(20180515).run()
        
        self.compute_initial_figure()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.compute_initial_figure)
        self.timer.start(1000)

    def pause(self):
        self.timer.stop()
        GlobalMap().set(running_global = 0)
    
    def compute_initial_figure(self):
        if self.times <= 23:
            temp11 = self.temp1[self.temp1['time'] == self.lists[self.times-1]]
            temp12 = self.temp1[self.temp1['time'] == self.lists[self.times]]
            temp1112 = merge(temp11, temp12, how='outer',on='id')
            temp1112 = temp1112[['x_x','y_x', 'x_y', 'y_y']][temp1112['x_x']!=temp1112['x_y']]#np.isnan(temp1112['y_y'])]
            temp1112 = temp1112[['x_x','y_x', 'x_y', 'y_y']][np.square(temp1112['x_x']- temp1112['x_y']) + np.square(temp1112['y_x'] - temp1112['y_y']) >np.square(0.0001)]  #车至少移动了直线距离100
            temp1112 = temp1112[['x_x','y_x', 'x_y', 'y_y']][np.isfinite(temp1112['x_x'])]
            
            temp11120 = merge(temp11, temp12, how='outer',on='id')
            temp11120 = temp11120[['x_x','y_x', 'x_y', 'y_y']][np.square(temp11120['x_x']- temp11120['x_y']) + np.square(temp1112['y_x'] - temp11120['y_y']) >np.square(0.001)]   #车至少移动了直线距离1km
            temp11120 = temp11120[['x_x','y_x']][np.isfinite(temp11120['x_x'])]
            
            
            self.changenum00 += [temp1112.shape[0]]
            self.changenum01 += [temp11120.shape[0]]
            imgP = imread('core/map.png',)
            self.axes.imshow(imgP, extent=[112.1495,112.288,30.308,30.391], aspect='auto') 
            x = temp1112['x_x']
            y = temp1112['y_x']
            np.save(GlobalMap().get('temp_path')+'/change'+str(self.times)+'.npy',np.vstack((x, y) ))
            self.axes.hold(True)
            self.axes.scatter(x, y, marker='o',c='',edgecolors='g')
            self.axes.grid(True)
            self.axes.set_xlim(112.150 , 112.284 )
            self.axes.set_ylim( 30.309, 30.385 )
            self.axes.set(xlabel="longitude", ylabel="latitude")
            self.axes.set_title('The '+str(self.times)+':00 ’s distribution statistics')
            self.draw()
            self.axes.hold(False)
        if self.times >= 23:
            if self.times == 23:
                self.axes.bar(range(1, 24), self.changenum00, 0.8, color=['g','c'], linewidth = 0.1, yerr=[0.8, ]*23,error_kw=dict(elinewidth=1.5,ecolor='green'))
                self.axes.hold(True)
                self.axes.plot(range(1, 24), self.changenum00, marker="o", linestyle="-", color="r")
                self.axes.set_xticks(range(1, 24))
                self.axes.set(xlabel="hour", ylabel="number")
                for x,y in zip(range(1, 24),self.changenum00): 
                    self.axes.text(x,y+0.5,'%d' % y,ha='center')
                    self.axes.set_title('Number of changes at each time point(At least 100m)')
                self.draw()
                self.axes.hold(False)
            else:
                self.pause()
                sleep(1)
                self.axes.bar(range(1, 24), self.changenum01, 0.8, color=['g','c'], linewidth = 0.1, yerr=[0.8, ]*23,error_kw=dict(elinewidth=1.5,ecolor='green'))
                self.axes.hold(True)
                self.axes.plot(range(1, 24), self.changenum01, marker="o", linestyle="-", color="r")
                self.axes.set_xticks(range(1, 24))
                self.axes.set(xlabel="hour", ylabel="number")
                for x,y in zip(range(1, 24),self.changenum01): 
                    self.axes.text(x,y+0.5,'%d' % y,ha='center')
                    self.axes.set_title('Number of changes at each time point(At least 1km)')
                self.draw()
                self.axes.hold(False)
        self.times+=1

#用包含密度信息的图代替了
#class MyDynamicMplCanvas(MyMplCanvas):
#
#    '''24小时动态分布图'''
#    def __init__(self, *args, **kwargs):
#        MyMplCanvas.__init__(self, *args, **kwargs)
#    
#    def start(self):
#        #self.n.value=1000
#        imgP = imread('core/map.png',)
#        self.axes.imshow(imgP, extent=[112.1495,112.288,30.308,30.391], aspect='auto') 
#        self.draw()
#        self.times = 0
#        num = 0
#        self.timer = QTimer(self)
#        self.timer.timeout.connect(self.update_figure)
#        for i in range(24):
#            if exists(GlobalMap().get('temp_path')+'/test'+str(i)+'.npy'):
#                num += 1
#        if num != 24:
#            #print(num)
#            GlobalMap().set(time_point = 0)
#            self.thread = Worker_2()
#            self.thread.changed2_signal.connect(self.compute_initial_figure)
#            self.thread.start()
#        else:
#            self.axes.hold(False)
#            self.times = 0
#            self.timer.start(1000)
# 
#    def pause(self):
#        try:
#            self.timer.stop()
#            self.thread.quit()
#        except:
#            pass
#        GlobalMap().set(running_global = 0, )
#        #self.n.value = 0
#    
#    def compute_initial_figure(self, iss):
#        if iss == 1:
#            self.thread.quit()
#            GlobalMap().set(time_point = self.times+1)
#            self.times += 1
#            if self.times < 24:
#                self.axes.hold(False)
#                imgP = imread('core/map.png',)
#                self.axes.set(xlabel="longitude", ylabel="latitude")
#                self.axes.imshow(imgP, extent=[112.1495,112.288,30.308,30.391], aspect='auto') 
#                self.axes.text(112.217, 30.347, r'The '+str(self.times) +':00 is in progress...')
#                self.draw()
#                GlobalMap().set(running_global = 1, )
#                self.thread = Worker_2()
#                self.thread.changed2_signal.connect(self.compute_initial_figure)
#                self.thread.start()
#            else:
#                self.times = 0
#                self.timer.start(1000)
#        
#    def update_figure(self):
#        temp = np.load(GlobalMap().get('temp_path')+'/test'+str(self.times)+'.npy')
#        imgP = imread('core/map.png',)
#        self.axes.imshow(imgP, extent=[112.1495,112.288,30.308,30.391], aspect='auto') 
#        x = temp[0]
#        y = temp[1]
#        self.axes.hold(True)
#        self.axes.scatter(x, y,marker='.',s=5,  edgecolors='g')
#        self.axes.grid(True)
#        self.axes.set_xlim(112.150 , 112.284 )
#        self.axes.set_ylim( 30.309, 30.385 )
#        self.axes.set(xlabel="longitude", ylabel="latitude")
#        self.axes.set_title('The '+str(self.times)+':00 ’s distribution prediction')
#        self.draw()
#        self.axes.hold(False)
#        if self.times >= 23:
#            self.pause()
#        self.times+=1
        
        
class MyDig_ChangeMplCanvas(MyMplCanvas):

    '''24小时动态分布图（自定义）'''
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
    
    def start(self):
        #初始地图图
        imgP = imread('core/map.png',)
        self.axes.set_xlim(112.150 , 112.284 )
        self.axes.set_ylim( 30.309, 30.385 )
        self.axes.imshow(imgP, extent=[112.1495,112.288,30.308,30.391], aspect='auto') 
        self.draw()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_figure)
        self.axes.hold(False)
        self.times = 1
        self.timer.start(1000)
        self.begin = 1
 
    def pause(self):
        try:
            self.timer.stop()
            self.thread.quit()
        except:
            pass
        GlobalMap().set(running_global = 0, )
        
    def update_figure(self):
        if GlobalMap().get('userdefined') == 'Null_': #检测从自定义对话框传递过来的数据
            return
        if not self.begin:  #防止重绘
            return
        self.begin = 0
        GlobalMap().set(time_point=self.times, )
        self.times+=1
        if self.times == 2:
            self.begin = 1
            self.temp0 = NN.main([], [], GlobalMap().get('userdefined') )  #传入BP网络预测
            return
        else:
            temp01 = self.temp0
            self.temp0 = NN.main([], [], temp01)
        imgP = imread('core/map.png',)
        self.axes.imshow(imgP, extent=[112.1495,112.288,30.308,30.391], aspect='auto') 
        x = np.array(self.temp0[0])
        y = np.array(self.temp0[1])
        z = gaussian_kde(self.temp0)(self.temp0)  #生成密度颜色
        self.axes.hold(True)
        self.axes.scatter(x, y,marker='.',s=100, c=z,  edgecolors='')
        self.axes.grid(True)
        self.axes.set_xlim(112.150 , 112.284 )
        self.axes.set_ylim( 30.309, 30.385 )
        self.axes.set(xlabel="longitude", ylabel="latitude")
        self.axes.set_title('The '+str(self.times)+':00 ’s distribution prediction')
        self.draw()
        self.begin = 1
        self.axes.hold(False)
        if self.times >= 2:
            self.pause()
        
        
class MyHotMplCanvas(MyMplCanvas):
    '''含有密度信息的动态分布图'''
    
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
    
    def start(self):
        self.times = 1
        GlobalMap().set(progress_num = 0)
        self.lists = []  #记录时间
        self.list_height = [[], []]  #用于记录高密度的区域
        self.stat = 0
        self.fig.subplots_adjust(left=0.02, bottom=0.02, right=0.98, top=0.92, hspace=0.04, wspace=0.02)
        self.axes1 = self.fig.add_subplot(211)
        self.axes2 = self.fig.add_subplot(212)
        for i in range(24):
            self.lists += [i]
            
        if exists('db/temp/20180515.csv'):
            self.temp1 = DataFrame(read_csv('db/temp/20180515.csv' ,header=0))
        else:
            self.temp1 = dataclear(20180515).run()
        
        self.compute_initial_figure()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.compute_initial_figure)
        self.timer.start(1000)


    def pause(self):
        self.timer.stop()
        GlobalMap().set(running_global = 0)
        
    def compute_initial_figure(self):
        if not self.stat:
            self.stat = 1
            temp = np.load('temp/test'+ str(self.times)+'.npy') #加载之前生成的预测数据
            x = temp[0]
            y = temp[1]
            z = gaussian_kde(temp)(temp)
            x2y2 = np.load('temp/change'+ str(self.times)+'.npy')  #加载之前生成的改变的单车数据
            x2 = x2y2[0]
            y2 = x2y2[1]
            z2 = gaussian_kde(x2y2)(x2y2)  #生成密度 颜色
            K = 5
            point = np.argpartition(z2,-K)[-K:]
            
            #用于记录高密度的区域
            self.list_height[0] += [x2[point[0]], x2[point[1]], x2[point[2]], x2[point[3]], x2[point[3]]]
            self.list_height[1] += [y2[point[0]], y2[point[1]], y2[point[2]], y2[point[3]], y2[point[3]]]
            
            self.axes1.hold(False)
            self.axes2.hold(False)
    
            imgP = imread('core/map.png',)
            self.axes2.imshow(imgP, extent=[112.1495,112.288,30.308,30.391], aspect='auto')
            self.axes1.imshow(imgP, extent=[112.1495,112.288,30.308,30.391], aspect='auto')
            
            self.axes2.hold(True)
            self.axes1.hold(True)
            
            self.axes1.scatter(x, y, c=z, s=100, edgecolor='')
            self.axes2.scatter(x2, y2, c=z2, s=100, edgecolor='')
            self.axes2.axis('off')
            self.axes1.axis('off')
            self.axes2.set_xlim(112.150 , 112.284 ) 
            self.axes2.set_ylim( 30.309, 30.385 )
            self.axes1.set_xlim(112.150 , 112.284 ) 
            self.axes1.set_ylim( 30.309, 30.385 )
    
            self.axes.axis('off')
            self.axes.set_title('The top is '+ str(self.times) +':00 bike‘s distribution\n The bottom is chnaged bike’s distribution')
            self.draw()
    
            if self.times >= 23:
                #绘制高密度区域分布图
                self.fig.subplots_adjust(left=0.08, bottom=0.08, right=0.92, top=0.92, hspace=0.04, wspace=0.02)
                self.axes.hold(False)
                self.axes1.remove() #移除之前创建的两个子图
                self.axes2.remove()
                self.axes.set_xlim(112.150 , 112.284 ) 
                self.axes.hold(True)
                self.axes.axis('on')
                self.axes.set_title('Bike flow Top 50')
                self.axes.set(xlabel="longitude", ylabel="latitude")
                self.axes.set_ylim( 30.309, 30.385 )
                self.axes.imshow(imgP, extent=[112.1495,112.288,30.308,30.391], aspect='auto')
                self.axes.scatter(self.list_height[0], self.list_height[1], c='r', s=200, edgecolor='')
                self.draw()
                self.pause()
                
            self.times+=1
            self.stat = 0

class MyccMplCanvas(MyMplCanvas):
    """初始图"""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.compute_initial_figure()
            
    def compute_initial_figure(self):
        #展示地图
        self.axes.set_xlim(112.150 , 112.284 ) 
        self.axes.set_ylim( 30.309, 30.385 )
        self.axes.set_title('JingZhou')
        self.axes.set(xlabel="longitude", ylabel="latitude")
        imgP = imread('core/map.png',)
        self.axes.imshow(imgP, extent=[112.1495,112.288,30.308,30.391], aspect='auto')
        self.draw()


class MySticMplCanvas(MyMplCanvas):
    """单个时间点预测验证图"""
   
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
    
    def start(self):
        self.thread = Worker()
        self.thread.changed_signal.connect(self.compute_initial_figure)  #信号连接
        self.thread.start()
        self.a = []
        self.b = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loss)
        self.timer.start(1000)

    def loss(self):
        #绘制损失度动态图
        self.axes.hold(False)
        self.a += [GlobalMap().get('times')]
        self.b += [GlobalMap().get('loss_now')/100]
        self.axes.plot(self.a,self.b, linewidth=2)
        self.axes.set(xlabel="times", ylabel="loss", title='Real time training state')
        self.draw()
        
    def pause(self):
        GlobalMap().set(running_global = 0, )
    
    def compute_initial_figure(self, a, b):
        self.timer.stop()
        self.axes.hold(True)
        self.axes.set_title('The '+str(GlobalMap().get('time_point'))+':00 ’s distribution prediction')
        x = a[0]
        y = a[1]
        x0 = b[0]
        y0 = b[1]
        
        imgP = imread('core/map.png',)
        self.axes.imshow(imgP, extent=[112.1495,112.288,30.308,30.391], aspect='auto') 
        
        self.axes.plot(x,y, '.b', markersize=3,
             label='prediction')   #预测的结果
        self.axes.plot(x0,y0, '.r', markersize=2,
            label='original')     #期望的结果
    
        self.axes.grid(True)
        self.axes.legend(shadow=True)
        self.axes.set_xlim(112.150 , 112.284 )
        self.axes.set_ylim( 30.309, 30.385 )
        self.axes.set(xlabel="longitude", ylabel="latitude")
        self.draw()

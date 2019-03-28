from numpy import vstack, isnan #, random , array, linalg, spacing, sign
from os.path import exists
from datetime import datetime
from core.globalmap import GlobalMap
from tensorflow import reset_default_graph, global_variables_initializer, train, placeholder, set_random_seed, float32, reduce_mean, reduce_sum, square, Variable, random_normal, matmul, zeros, Session
            
    
class BPNeuralNetwork:
    '''BP神经网络'''
    def __init__(self, session):
        self.session = session  #记录session
        self.saver = train  #提供Saver服务
        self.loss = None  #记录误差
        self.optimizer = None  #优化器
        self.input_n = 0  #输入维度
        self.hidden_n = 0  #中间层个数
        self.hidden_size = []  #中间层大小
        self.output_n = 0  #输出维度
        self.input_layer = None
        self.hidden_layers = []
        self.output_layer = None
        self.label_layer = None
        self.init_temp = GlobalMap().get('all')  #获取所有前台传递过来的数据
        self.auto_times = 0
        #print(self.init_temp)   #测试用
        self.ckpt_path = 'ckpt/model-'+ str(self.init_temp['time_point']) +'.ckpt'  #定义训练模型保存位置
        if self.init_temp['fix_seed']:
            set_random_seed(523456789)

    def setup(self, layers):
        if len(layers) < 3:
            return
        self.input_n = layers[0]
        self.hidden_n = len(layers) - 2  # 隐含层个数
        self.hidden_size = layers[1:-1]  # 隐含层大小
        self.output_n = layers[-1]

        # 建立 符号变量
        self.input_layer = placeholder(float32, [None, self.input_n])
        self.label_layer = placeholder(float32, [None, self.output_n])
        # 建立 隐含层
        in_size = self.input_n
        out_size = self.hidden_size[0]
        self.hidden_layers.append(self.make_layer(self.input_layer, in_size, out_size))
        for i in range(self.hidden_n-1):
            in_size = out_size
            out_size = self.hidden_size[i+1]
            inputs = self.hidden_layers[-1]
            self.hidden_layers.append(self.make_layer(inputs, in_size, out_size))
        # 建立 输出层
        self.output_layer = self.make_layer(self.hidden_layers[-1], self.hidden_size[-1], self.output_n)

    def train(self, cases, labels): 
        '''训练'''
        limit=self.init_temp['max_itera']
        learn_rate=self.init_temp['dg_initial'] * 0.00000001
        self.loss = reduce_mean(reduce_sum(square((self.label_layer - self.output_layer)), reduction_indices=[1]))
        
        learning_rate = placeholder(float32, shape=[])
        #self.train_step = #tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(self.loss)
        self.train_step = train.MomentumOptimizer(learning_rate=learning_rate, momentum=0.9, use_locking=False, use_nesterov=True).minimize(self.loss) #动量优化器
        self.session.run(global_variables_initializer())
        
        next_done = 0
        starttime = datetime.now()
        for i in range(limit):
            self.session.run(self.train_step, feed_dict={self.input_layer: cases, self.label_layer: labels, learning_rate: learn_rate})

            if i % 2 == 0:
                if not GlobalMap().get('running_global'):
                    break
                next_done = 1
                next_times = i + 1
                train_0 = self.train_step
                loss0 = self.session.run(self.loss, feed_dict={self.input_layer: cases, self.label_layer: labels})
            
            #更新前台和处理数据
            if next_done == 1 and i % next_times == 0:
                loss1 = self.session.run(self.loss, feed_dict={self.input_layer: cases, self.label_layer: labels})
                GlobalMap().set(loss_now = loss0, times = i, used_time = (datetime.now() - starttime).seconds)
                if loss1 < self.init_temp['precision']:
                    break
                        
                if (i + 1) % 50 == 0 and self.init_temp['fix_auto'] and (loss0 - loss1 <0.1 or isnan(loss1)):
                    self.auto_times += 1
                    #print(self.auto_times)
                    GlobalMap().set(progress_num = 5 + i * 100// limit +10 )  #进度条
                    if self.auto_times > 8:
                        break

                if  loss1 < loss0:  #在动量的基础上调整学习率
                    learn_rate *= 1.0 + self.init_temp['dg_adaptive']
                else:
                    learn_rate *= 1.0 - self.init_temp['dg_adaptive']
                    self.train_step = train_0
                    #print("1:", loss1)
                #print("shu:",learn_rate)
                next_done = 0
        self.saver.Saver().save(self.session, self.ckpt_path)

    def predict(self, case):
        '''预测'''
        return self.session.run(self.output_layer, feed_dict={self.input_layer: case})
        
    
    def make_layer(self, inputs, in_size, out_size, activate=None):
        '''添加神经层'''
        weights = Variable(random_normal([in_size, out_size]))
        basis = Variable(zeros([1, out_size]) + 0.1)
        result = matmul(inputs, weights) + basis
        if activate is None:
            return result
        else:
            return activate(result)

    def test(self, a, b, c):
        '''入口'''
        if a == []: #仅用于自定义模式的预测
            #print(self.ckpt_path, c)
            self.setup([2, self.init_temp['neurons_num'],  2])
            self.saver.Saver().restore(self.session, 'ckpt/modelc-'+ str(self.init_temp['time_point']) +'.ckpt')    #存在就从模型中恢复变量 
            GlobalMap().set(used_time = 0, times = 0)
            return noturn(self.predict(turn(c)))
        
        x_data = turn(a)
        y_data = turn(b)
        test_data = turn(c)
        self.setup([2, self.init_temp['neurons_num'],  2])
        if exists(self.ckpt_path + '.index') and GlobalMap().get('save_nopass'):         #判断模型是否存在  
            try:
                self.saver.Saver().restore(self.session, self.ckpt_path)    #存在就从模型中恢复变量 
                self.loss = reduce_mean(reduce_sum(square((self.label_layer - self.output_layer)), reduction_indices=[1]))
                loss_now = self.session.run(self.loss, feed_dict={self.input_layer: x_data, self.label_layer: y_data})
                GlobalMap().set(used_time = 0, times = 0,  loss_now = loss_now)
            except:
                print(2)
                self.train(x_data, y_data)
        else:  
            self.train(x_data, y_data)
        GlobalMap().set(running_global = 0, )
        return noturn(self.predict(test_data))


def main(a , b , c ):
    '''BP实例化'''
    reset_default_graph()
    with Session() as session:
        model = BPNeuralNetwork(session)
        return model.test(a, b, c)


'''数组类归一化处理和装置等'''
def turn(arr):
    a0 = (arr[0] - 112 ) *1000
    b0 = (arr[1] - 30 ) *1000
    return vstack((a0,b0)).T

def noturn(arr):
    a0 = arr.T[0]  /1000 + 112
    b0 = arr.T[1]  /1000 + 30
    return vstack((a0,b0))

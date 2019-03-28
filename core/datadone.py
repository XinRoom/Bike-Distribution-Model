from pandas import DataFrame, concat, read_csv
from os import listdir

class dataclear:
     '''原始数据整合和处理'''
     def __init__(self, date = 20180515 ):
        '''初始化路径'''
        self.date = date
        self.basedir = 'db/'+ str(date) +'/'
        self.dirlist = listdir(self.basedir)

     def run(self):
        temp1 = DataFrame(read_csv(self.basedir + self.dirlist[0] ,header=0))
        self.done = DataFrame({"id":temp1['id'],'x':temp1['distX'],'y':temp1['distY'],'time':int(self.dirlist[0][:-4])})

        for dirl in self.dirlist[1:]:
            temp2 = DataFrame(read_csv(self.basedir + dirl ,header=0))
            temp3 = DataFrame({"id":temp2['id'],'x':temp2['distX'],'y':temp2['distY'],'time':int(dirl[:-4])})
            self.done = concat([self.done, temp3])

        return self.done

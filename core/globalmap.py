from json import dumps

class GlobalMap:
    '''全局变量，用于全局数据的交互'''
    # 拼装成字典构造全局变量  借鉴map  包含变量的增删改查
    map = {}

    def set_map(self, key, value):
        if(isinstance(value,dict)):
            value = dumps(value)
        self.map[key] = value

    def set(self, **keys):
        try:
            for key_, value_ in keys.items():
                self.map[key_] = value_
        except BaseException as msg:
            raise msg

    def del_map(self, key):
        try:
            del self.map[key]
            return self.map
        except KeyError:
            pass
            
    def get(self,*args):
        try:
            dic = {}
            for key in args:
                if len(args)==1 and args[0]=='all':
                    dic = self.map
                elif len(args)==1:
                    dic = self.map[key]
                else:
                    dic[key]=self.map[key]
            return dic
        except KeyError:
            return 'Null_'
            
    

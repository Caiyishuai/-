'''
some supplement
'''
import numpy as np
# calculator in cpu to calculate, Here, i have considered to

class Calculator:

    #state=[]进位，符号位，溢出，零位

    def __init__(self,num):
        self.buffer1 = np.zeros(32)
        self.buffer2 = np.zeros(32)
        self.refer_dict= {
            'buffer1' : self.buffer1,
            'buffer2' : self.buffer2
        }
        self.buffer3 = np.zeros(32)


    def get_buffer(self,identity):
        return self.refer_dict.get(identity)

    def set_buffer(self,identity, data):
        self.refer_dict[identity] = data

    @staticmethod
    def and_func(a1,a2):
        return int(a1 and a2)
    @staticmethod
    def or_func(a1,a2):
        return  int(a1 or a2)

    @staticmethod
    def nand(a1,a2):
        return int(not (a1 and a2))

    @staticmethod
    def nor(a1,a2):

        return int(not (a1 and a2))

    @staticmethod
    def xor(a1,a2):
        return int((not (a1 and a2) )and (a1 or a2) )

    @staticmethod
    def half_adder(a,b):
        s= Calculator.xor(a,b)
        c= Calculator.and_func(a,b)

        return s, c

    @staticmethod
    def full_adder(a,b,c):
        s,c1 = Calculator.half_adder(a,b)
        s,c2 = Calculator.half_adder(c,s)
        co = Calculator.or_func(c1,c2)

        return s, co


    def __call__(self, *args, **kwargs): #实现计算功能，调用其他函数。实现运算
        pass  #可以调用多个Calculator.full_adder()



#
class Trigger:  #触发器
    pass

'''
This file aims to stimulate the memory and register...in the computer
Use the array to open up the space
I seperate the different
'''

import numpy as np

class Memory:

    __obj = None
    def __new__(cls, *args, **kwargs):
        if cls.__obj is None:
            cls.__obj = object.__new__(cls)
        return cls.__obj

    def __init__(self):
        '''According to the requirements,the size of memory is 32bit*8bit = 4GB
        here,dict[address] = array (8 bit), address is 32bit according to considering'''
        self.memory = {
            '0x0000 0000':np.zeros(8),
            '0x0000 0001':np.zeros(8),
            '0x0000 0010':np.zeros(8),
            '0x0000 0011':np.zeros(8),
        }


    def store_func(self,data, address = '0x0000 0011'):
        '''

        :param item:  address
        :param data:  the form is array
        :return:
        '''
        for index, i in enumerate(data):
            self.memory[address][index]= i
        flag = True
        return flag


    def load_func(self,address):  #load

        flag = True
        data = self.memory.get(address, flag)
        return (data,flag)






class Register:

    def __init__(self,identifier):
        '''

        :param identifier: to identify the register
        '''

        self.identifier = identifier
        self.unit = np.zeros(32)

    def re_store(self,data):
        for index,single_data in data:
            self.unit[index] = single_data


    def re_load(self):
        data = self.unit
        signal = True
        return (data, signal)

class Cpu:

    def __init__(self):
        pass

    def calculator(self):


    def state(self):
        pass



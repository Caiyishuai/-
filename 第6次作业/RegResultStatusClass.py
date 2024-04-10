# -*- coding: utf-8 -*-

class RegisterResultStatus:
    '''
    'busy':判断寄存器是都被占用
    'FU':存的数据是什么
    'Reorder':被 ROB 中的哪一行占用
    '''

    def __init__(self, r_n, f_n):
        self.Rrs = {}
        self.r_n = r_n
        self.f_n = f_n
        self.destmap = {}
        for i in range(self.r_n):
            reg_name = 'R'
            reg_name += str(i)
            self.Rrs[reg_name] = {'busy': False, 'FU': "R(" + reg_name + ")", 'Reorder': None}  # busy可以表示是否可取，FU里面内容无关
        for i in range(self.f_n):
            reg_name = 'F'
            reg_name += str(i)
            self.Rrs[reg_name] = {'busy': False, 'FU': "R(" + reg_name + ")", 'Reorder': None}  # busy可以表示是否可取，FU里面内容无关

    # 判断该寄存器是否空闲
    def is_busy(self, name):
        busy_flag = self.Rrs[name].get('busy')
        aim_rs = self.Rrs[name].get('Reorder')
        if not busy_flag:
            aim_rs = self.Rrs[name].get('FU')
        return busy_flag, aim_rs

    # 占用寄存器,被 Reorder_id 占用
    def occupy(self, name, Reorder_id):
        self.Rrs[name]['busy'] = True
        self.Rrs[name]['Reorder'] = Reorder_id
        self.destmap[Reorder_id] = name

    # 释放寄存器,Reorder_id变为None
    def release(self, Reorder_id, context):
        #        if name in self.Rrs:
        # print(self.destmap)
        name = self.destmap[Reorder_id]
        self.Rrs[name]['busy'] = False
        # print('清除数据')
        self.Rrs[name]['Reorder'] = None
        self.Rrs[name]['FU'] = context  # 改变寄存器的值,写入数据
        self.destmap.pop(Reorder_id)

    #    def modify(self, mod, name, context=""):
    #        if mod == 1:
    #            self.Rrs[name]['busy'] = True
    #            # print('写入数据')
    #            self.Rrs[name]['FU'] = context
    #        elif mod == 0:
    #            self.Rrs[name]['busy'] = False
    #            # print('清除数据')
    #            self.Rrs[name]['FU'] = context

    # 清除 ROB 中索引为 dest 的对寄存器的占用
    def clear(self, dest):
        for i in range(self.r_n):
            reg_name = 'R'
            reg_name += str(i)
            if self.Rrs[reg_name]['Reorder'] == dest:
                self.Rrs[reg_name]['Reorder'] = None
                self.Rrs[reg_name]['busy'] = False
        for i in range(self.f_n):
            reg_name = 'F'
            reg_name += str(i)
            if self.Rrs[reg_name]['Reorder'] == dest:
                self.Rrs[reg_name]['Reorder'] = None
                self.Rrs[reg_name]['busy'] = False

    # 打印reg result status数据
    def print_reg_result_status(self):
        reg_name = []
        reg_busy = []
        reg_fu = []
        reg_Reorder = []
        for key, value in self.Rrs.items():
            reg_name.append(key)
            reg_busy.append(value['busy'])
            reg_fu.append(value['FU'])
            reg_Reorder.append(value['Reorder'])
        reg_name = reg_name[0:5] + reg_name[16:21]
        reg_busy = reg_busy[0:5] + reg_busy[16:21]
        reg_fu = reg_fu[0:5] + reg_fu[16:21]
        reg_Reorder = reg_Reorder[0:5] + reg_Reorder[16:21]

        # 只输出Ri的前5个 Fi的前5个
        print("------------Reg Result Status------------")
        print("%8s" % ("name"), end='')
        for name in reg_name:
            print("%8s" % (name), end='')
        print("\n%8s" % ("busy"), end='')
        for busy in reg_busy:
            print("%8s" % (busy), end='')
        print("\n%8s" % ("FU"), end='')
        for fu in reg_fu:
            print("%8s" % (fu), end='')
        print("\n%8s" % ("Reorder"), end='')
        for Reorder in reg_Reorder:
            print("%8s" % (Reorder), end='')
        print("\n")


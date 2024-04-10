# -*- coding: utf-8 -*-

class RegisterResultStatus:
    def __init__(self):
        self.Rrs = {}
        self.clock  = 0
        for i in range(16):
            reg_name = 'R'
            reg_name += str(i)
            self.Rrs[reg_name] = {'busy': False, 'FU': "R("+reg_name+")"}   # busy可以表示是否可取，FU里面内容无关
        for i in range(16):
            reg_name = 'F'
            reg_name += str(i)
            self.Rrs[reg_name] = {'busy': False, 'FU': "R(" + reg_name + ")"}  # busy可以表示是否可取，FU里面内容无关

    def is_busy(self,name):
        busy_flag = self.Rrs[name].get('busy')
        aim_rs = self.Rrs[name].get('FU')
        return busy_flag, aim_rs

    def modify(self, mod, name, context=""):
        if mod == 1:
            self.Rrs[name]['busy'] = True
            # print('写入数据')
            self.Rrs[name]['FU'] = context
        elif mod == 0:
            self.Rrs[name]['busy'] = False
            # print('清除数据')
            self.Rrs[name]['FU'] = context

    # 打印reg result status数据
    def print_reg_result_status(self):
        reg_name = []
        reg_busy = []
        reg_fu = []
        for key, value in self.Rrs.items():
            reg_name.append(key)
            reg_busy.append(value['busy'])
            reg_fu.append(value['FU'])
        reg_name = reg_name[0:5]+reg_name[16:21]
        reg_busy = reg_busy[0:5]+reg_busy[16:21]
        reg_fu = reg_fu[0:5]+reg_fu[16:21]

        # 只输出Ri的前5个 Fi的前5个
        print("------------Reg Result Status------------")
        print("%8s" % ("name"), end='')
#        print("name\t", end='')
        for name in reg_name:
#            print("{0}\t\t".format(name), end='')
            print("%8s" % (name), end='')
#        print("\nbusy\t", end='')
        print("\n%8s" % ("busy"), end='')
        for busy in reg_busy:
#            print("{0}\t".format(busy), end='')
            print("%8s" % (busy), end='')
#        print("\nFU\t\t", end='')
        print("\n%8s" % ("FU"), end='')
        for fu in reg_fu:
#            print("{0}\t".format(fu), end='')
            print("%8s" % (fu), end='')
        print("\n")

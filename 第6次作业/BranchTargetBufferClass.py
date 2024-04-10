class Branch_Buffer:
    def __init__(self):  
        self.obj={}
# =============================================================================
# 查看BTB中是否存在匹配项
# =============================================================================
    def find(self,PC):
        '''
        :param
            PC: int型,表示需要查找的分支指令地址
        :return:
            target: int型。若存在，表示转移的目标地址，若不存在，用-1表示
            predict: bool型。True: 预测转移成功 ; False: 预测转移不成功
        '''
        target=-1
        predict=None
        for temp in self.obj:
            # 查找对应功能部件并判断是否被占用
            if temp==PC:
                return self.obj[temp]['target'],self.obj[temp]['predict']
        return target, predict
    
# =============================================================================
# 写入BTB
# 将PC值和分支目标地址写入BTB中作为一个新项
# =============================================================================
    def insert(self,PC,target):
        '''
        :param
            PC: int型,表示需要插入的分支指令地址
            target: int型,表示分支指令对应的目标地址
        '''
        self.obj[PC]={'target':target,'predict':0}
        # print(self.obj)
        
# =============================================================================
# 修改
# 分支失败后，修改对应分支指令的状态为反
# =============================================================================
    def modify(self, PC, target):
        '''
        :param
            PC: int型,表示需要修改的分支指令地址
            target: int型,表示分支指令对应的目标地址
        '''
        for temp in self.obj:
            if temp==PC:
                self.obj[temp]['target'] = target
                self.obj[temp]['predict'] = not self.obj[temp]['predict']
                # print(self.obj)

# =============================================================================
# 打印
# 将BTB数据打印出来
# =============================================================================
    def print(self):
        print("------------BTB------------")
        print("%6s %6s %6s" % ("PC", "Target", "Predict"))
        for key, value in self.obj.items():
            print("%6s %6s %6s" % (str(key), value['target'], value['predict']))

'''
# 创建类
btb = Branch_Buffer()
PC=5

# 查找是否存在该分支
print("预测PC=",PC,"时是否存在分支：")
target, predict = btb.find(PC)
print("target: ",target,",predict: ",predict,"\n")

# 插入分支指令,PC=5,目标地址1
target=1
print("插入分支指令后BTB列表：")
btb.insert(PC,target)
print()

# 再次查找
print("再次查找PC=",PC,"时是否存在分支：")
target, predict = btb.find(PC)
print("target: ",target,",predict: ",predict,"\n")

# 修改target=2
target=2
print("修改PC=",PC,"时是target=",target)
btb.modify(PC,2)

# 打印
btb.print()
'''
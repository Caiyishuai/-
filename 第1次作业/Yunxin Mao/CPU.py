# -*- coding: utf-8 -*-

class CPU:
    def __init__(self, word_len,mem_len,reg_num,Mem,Fun):
        self.word_len=word_len
        self.mem_len=mem_len
        self.reg_num=reg_num
        self.Mem=Mem
        self.Fun=Fun
        
# =============================================================================
#     寄存器
# =============================================================================
    class Register:
        registers = {}
        def __init__(self,obj):
            self.obj=obj
            # 初始化32个寄存器中的内容   
            for i in range(32):
                str_bin = bin(i).replace('0b','')
                add = (self.obj.word_len - len(str_bin))*'0'+str_bin
                self.registers[add] = []
                for j in range(self.obj.word_len):
                    self.registers[add].append(bool(0))
        
        # 写寄存器（传入寄存器的物理地址）
        def write(self,reg_address,binary_num): 
            for i in range(self.obj.word_len):
                self.registers[reg_address][i] = binary_num[i]
            
        # 读寄存器（传入物理地址和二进制补码）
        def read(self,reg_address):
            binary_num=[]
            for i in range(self.obj.word_len):
                binary_num.append(self.registers[reg_address][i])
            return binary_num

# =============================================================================
#     加法器
# =============================================================================
    class Adder:
        def __init__(self,obj):
            self.obj=obj
        
        # 求和，传入两个二进制补码
        def add(self,bin_a,bin_b):
            flag = 0
            c=[]
            for i in range(self.obj.mem_len*4-1,-1,-1): # 两二进制补码相加
                c.append(flag^bin_a[i]^bin_b[i])
                flag = (bin_a[i] and bin_b[i]) + ((bin_a[i]^bin_b[i]) and flag)
            c.reverse()
            return c
            
# =============================================================================
#     控制器
# =============================================================================
    class controller:
        def __init__(self,obj,reg,adder):
            self.obj=obj
            self.reg=reg
            self.adder=adder
        
        # 取数，从内存读到寄存器（传入寄存器序号和内存的形式地址）
        def load(self,reg_id,mem_id):
            reg_address=self.obj.Fun.To_real_address(int(reg_id[1:]))   
            mem_addlist=self.obj.Fun.MemId_toBlock(mem_id)
            temp=self.obj.Mem.read(mem_addlist)
            self.obj.Register.write(self.reg,reg_address,temp)
            print("已从内存 "+ mem_id + " 中取出数据 "+ str(self.obj.Fun.To_decimal(temp)) + " 写入到寄存器 " + reg_id+"\n")
        
        # 读数，从寄存器读到内存（传入寄存器序号和内存的形式地址）
        def store(self,reg_id,mem_id):
            reg_address=self.obj.Fun.To_real_address(int(reg_id[1:]))   
            mem_addlist=self.obj.Fun.MemId_toBlock(mem_id)
            temp=self.obj.Register.read(self.reg,reg_address)
            self.obj.Mem.write(mem_addlist,temp)
            print("已从寄存器 "+ reg_id + " 中取出数据 "+ str(self.obj.Fun.To_decimal(temp)) + " 写入到内存 " + reg_id+"\n")
            
        # 执行加法操作
        # 将寄存器序号转换成物理地址后，从寄存器中取数
        # 调用加法器相加后存入指定寄存器
        def add(self,reg_save,reg_1,reg_2):
            reg_savead=self.obj.Fun.To_real_address(int(reg_save[1:]))
            reg_1ad=self.obj.Fun.To_real_address(int(reg_1[1:]))
            reg_2ad=self.obj.Fun.To_real_address(int(reg_2[1:]))
            a=self.reg.read(reg_1ad)
            b=self.reg.read(reg_2ad)
            c=self.adder.add(a,b)
            self.reg.write(reg_savead,c)
            print("从寄存器 "+ reg_1 + " 中取出数据 "+ str(self.obj.Fun.To_decimal(a))+\
                  " ,从寄存器 "+ reg_2 + " 中取出数据 "+ str(self.obj.Fun.To_decimal(b))+\
                  ", 将相加结果 "+ str(self.obj.Fun.To_decimal(c)) + " 存入寄存器 "+ reg_save+"\n")
        

    




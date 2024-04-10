# -*- coding: utf-8 -*-

class CPU:
    def __init__(self, word_len,mem_len,reg_num,Mem,reg_add_len,Fun):
        self.word_len = word_len
        self.mem_len= mem_len
        self.reg_num = reg_num
        self.Mem = Mem
        self.Fun = Fun
        self.reg_add_len = reg_add_len
        
# =============================================================================
#     寄存器
# =============================================================================
    class Register:
        registers = {} #键是32位寄存器地址，值是32位二进制
        def __init__(self,obj):
            self.obj=obj
            # 初始化32个寄存器中的内容   
            for i in range(32):
                str_bin = bin(i).replace('0b','')
                add = (self.obj.reg_add_len - len(str_bin))*'0'+str_bin
                self.registers[add] = []
                for j in range(self.obj.word_len):
                    self.registers[add].append(0)
        
        # 写寄存器（传入寄存器的物理地址和二进制补码）
        def write(self,reg_address,binary_num): 
            for i in range(self.obj.word_len):
                self.registers[reg_address][i] = binary_num[i]
            
        # 读寄存器（传入寄存器的物理地址）
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
    class Controller:
        def __init__(self,obj,reg,adder):
            self.obj=obj
            self.reg=reg
            self.adder=adder
        
     
        # add指令，reg_savead是保存和的寄存器,reg_1ad、reg_2ad分别是两个加数的寄存器
        def ADD(self,reg_savead,reg_1ad,reg_2ad):
            a=self.reg.read(reg_1ad) #在寄存器中读出加数1，格式为32位二进制列表
            b=self.reg.read(reg_2ad) #在寄存器中读出加数2，格式为32位二进制列表
            c=self.adder.add(a,b)    #执行二进制加法，返回值为32位二进制列表
            self.reg.write(reg_savead,c) #将和写入寄存器
            print("从寄存器 R"+ str(int(reg_1ad,2)) + " 中取出数据 "+ str(self.obj.Fun.To_decimal(a))+\
                  " ,从寄存器 R"+ str(int(reg_2ad,2)) + " 中取出数据 "+ str(self.obj.Fun.To_decimal(b))+\
                  ", 将相加结果 "+ str(self.obj.Fun.To_decimal(c)) + " 存入寄存器 R"+ str(int(reg_savead,2))+"\n")
        
        # SLT指令，比较reg_1ad和reg_2ad两个寄存器中哪个值更大，若reg_2ad内的值大，reg_savead写入1；反之写入0
        def SLT(self,reg_savead,reg_1ad,reg_2ad):
            a=self.reg.read(reg_1ad) 
            a=self.obj.Fun.To_decimal(a)
            b=self.reg.read(reg_2ad)
            b=self.obj.Fun.To_decimal(b)
            if a < b:  #reg_savead存入1
                self.reg.write(reg_savead, self.obj.Fun.To_binary(1))
                print("由于 "+ str(a) + " < "+str(b) + ",设置 R"+ str(int(reg_savead,2)) + " 为 1\n")
            else:      #reg_savead存入0
                self.reg.write(reg_savead, self.obj.Fun.To_binary(0))
                print("由于 "+ str(a) + " >= "+str(b) + ",设置 R"+ str(int(reg_savead,2)) + " 为 0\n")
        
        def SUB(self,reg_savead,reg_1ad,reg_2ad):
            pass
        
        def MUL(self,reg_savead,reg_1ad,reg_2ad):
            pass
        
        def DIV(self,reg_savead,reg_1ad,reg_2ad):
            pass

        def ADDU(self,reg_savead,reg_1ad,reg_2ad):
            pass
        
        def SUBU(self,reg_savead,reg_1ad,reg_2ad):
            pass
        
        def MULU(self,reg_savead,reg_1ad,reg_2ad):
            pass
        
        def DIVU(self,reg_savead,reg_1ad,reg_2ad):
            pass

        # load指令，reg_address是寄存器地址，memadd_list是4个内存块地址组成的列表
        def LOAD(self,reg_address,memadd_list):
            temp=self.obj.Mem.read(memadd_list) #读出内存块对应的指令
            self.reg.write(reg_address,temp)    #将指令写入寄存器
            print("已从内存 #"+ str(int(int(memadd_list[0],2)/4)) + " 中取出数据 "+ str(self.obj.Fun.To_decimal(temp)) + " 写入到寄存器 R" + str(int(reg_address,2)) +"\n")
        
        # store指令，reg_address是寄存器地址，memadd_list是4个内存块地址组成的列表
        def STORE(self,reg_address,memadd_list):
            temp=self.obj.Register.read(self.reg,reg_address)  # 读出寄存器中的指令
            self.obj.Mem.write(memadd_list,temp)               # 将指令写入内存
            print("已从寄存器 R" + str(int(reg_address,2)) + " 中取出数据 "+ str(self.obj.Fun.To_decimal(temp)) + " 写入到内存 #" + str(int(int(memadd_list[0],2)/4))+"\n")
          
        # BGT指令，看reg_address内的值是否>=1,成立则跳转指令继续循环，反之结束循环
        def BGT(self,reg_address):
            a=self.reg.read(reg_address) # 读出寄存器中的数据
            a=self.obj.Fun.To_decimal(a) # 将读出来的数据转化为十进制，a>=1继续循环；a==0循环结束
            
            if a >= 1:
                print("由于寄存器 R"+ str(int(reg_address,2)) + "的数为 " + str(a) + " 跳转指令继续循环\n")
                return 1
            else:
                print("由于寄存器 R"+ str(int(reg_address,2)) + "的数为 " + str(a) + " 循环结束\n")
                return 0

        def ADDI(self,reg_savead,reg_1ad,imme):
            pass
        
        def SUBI(self,reg_savead,reg_1ad,imme):
            pass
        
        def MULI(self,reg_savead,reg_1ad,imme):
            pass
        
        def DIVI(self,reg_savead,reg_1ad,imme):
            pass
          
          
# =============================================================================
#     译码器
# =============================================================================            
    class  Decoder: 
        is_jump = 0  #是否跳转，0表示不跳，1表示跳
        jump_to_addr = "" #跳转地址，为32位二进制字符串
        is_end = 0   #是否结束循环，0表示不结束，1表示结束      
        def __init__(self,obj,control): #需要用到Controller类中的函数
            self.obj=obj
            self.control=control 
    
        def Decode(self,instruction_list):
            instruction_str = ''.join([str(i) for i in instruction_list])  # 列表转为字符串
            op = instruction_str[:6]   #取出前6位操作码
            
            #初始化
            self.is_jump = 0
            self.jump_to_addr = ""
            self.is_end = 0 
            
            if op[:3] == "001": # 属于R型指令 第6-10为寄存器1地址 第11-15为寄存器2地址 第16-20为寄存器3地址 后五位取数标志,add slt
                
                # 取数
                # get_num_flag = instruction_str[-3:] # 不需要寄存器寻址
                subop = instruction_str[-7:-5] # 辅助操作码
                reg_savead = instruction_str[6:11] # 取出形式地址       
                reg_1ad = instruction_str[11:16]      
                reg_2ad = instruction_str[16:21]
                
                # 执行指令
                if subop == "00":            
                       
                    # add 相加操作
                    if op[3:] == "000":
                        print("执行 add R" + str(int(reg_savead,2)) + ", R" + str(int(reg_1ad,2)) + ", R" + str(int(reg_2ad,2)))
                        self.control.ADD(reg_savead,reg_1ad,reg_2ad) # 传入三个寄存器的物理地址,每个都如'00001'
                        
                    # slt 比较操作 if r1<r2,reg_savead=1
                    if op[3:] == "001":
                        print("执行 slt R" + str(int(reg_savead,2)) + ", R" + str(int(reg_1ad,2)) + ", R" + str(int(reg_2ad,2)))
                        self.control.SLT(reg_savead,reg_1ad,reg_2ad) # 传入三个寄存器的物理地址,每个都如'00001'
                    
                    # sub 相减操作
                    if op[3:] == "010":
                        print("执行 sub R" + str(int(reg_savead,2)) + ", R" + str(int(reg_1ad,2)) + ", R" + str(int(reg_2ad,2)))
                        self.control.SUB(reg_savead,reg_1ad,reg_2ad) # 传入三个寄存器的物理地址,每个都如'00001'
    
                    # mul 相减操作                    # mul 相乘操作 只存储结果低位
                    if op[3:] == "011":
                        print("执行 mul R" + str(int(reg_savead,2)) + ", R" + str(int(reg_1ad,2)) + ", R" + str(int(reg_2ad,2)))
                        self.control.MUL(reg_savead,reg_1ad,reg_2ad) # 传入三个寄存器的物理地址,每个都如'00001'
    
                    # div 相除操作 有符号除
                    if op[3:] == "100":
                        print("执行 div R" + str(int(reg_savead,2)) + ", R" + str(int(reg_1ad,2)) + ", R" + str(int(reg_2ad,2)))
                        self.control.DIV(reg_savead,reg_1ad,reg_2ad) # 传入三个寄存器的物理地址,每个都如'00001'
                
                elif subop == "01":                  
                    
                    # addu 相加操作
                    if op[3:] == "000":
                        print("执行 addu R" + str(int(reg_savead,2)) + ", R" + str(int(reg_1ad,2)) + ", R" + str(int(reg_2ad,2)))
                        self.control.ADDU(reg_savead,reg_1ad,reg_2ad) # 传入三个寄存器的物理地址,每个都如'00001'
                       
                    # subu 相减操作
                    if op[3:] == "010":
                        print("执行 subu R" + str(int(reg_savead,2)) + ", R" + str(int(reg_1ad,2)) + ", R" + str(int(reg_2ad,2)))
                        self.control.SUBU(reg_savead,reg_1ad,reg_2ad) # 传入三个寄存器的物理地址,每个都如'00001'
    
                    # mulu 相减操作                    # mul 相乘操作 只存储结果低位
                    if op[3:] == "011":
                        print("执行 mulu R" + str(int(reg_savead,2)) + ", R" + str(int(reg_1ad,2)) + ", R" + str(int(reg_2ad,2)))
                        self.control.MULU(reg_savead,reg_1ad,reg_2ad) # 传入三个寄存器的物理地址,每个都如'00001'
    
                    # divu 相除操作 有符号除
                    if op[3:] == "100":
                        print("执行 divu R" + str(int(reg_savead,2)) + ", R" + str(int(reg_1ad,2)) + ", R" + str(int(reg_2ad,2)))
                        self.control.DIVU(reg_savead,reg_1ad,reg_2ad) # 传入三个寄存器的物理地址,每个都如'00001'
 
              
            elif op[:3] == "010": # 属于J型指令 第6-21为内存地址 后五位取数标志，jr
                
                # 取数
                get_num_flag = instruction_str[-3:]
                if get_num_flag == "010": #内存直接寻址
                    mem_add = instruction_str[6:22]
                if get_num_flag == "011": #内存间接寻址
                    pass  
                
                # 执行指令
                # jr 跳转指令
                if op[3:] == "000":
                    print("执行 jr #" + str(int(int(mem_add[0],2)/4)))
                    self.jump_to_addr = 16*'0'+ mem_add # 完整地址 
                    self.is_jump = 1
                
            elif op[:3] == "011": # 属于I型指令 第6-10为寄存器地址 第11-26为内存地址 后五位取数标志，load store bgt
              
                # 取数
                get_num_flag = instruction_str[-3:] # 查看取数方式
                reg_a = instruction_str[6:11] # 取寄存器形式地址
                mem_a = instruction_str[11:27] # 取内存形式地址
                reg_address = reg_a
                if get_num_flag == "001" : # 寄存器直接寻址
                    pass
                if get_num_flag == "010" : #寄存器间接寻址
                    pass
                if get_num_flag == "001": # 内存立即数寻址
                    pass
                if get_num_flag == "010": # 内存直接寻址
                    memadd_list = self.obj.Fun.FirstAddress_toBlock(mem_a)
                if get_num_flag == "011": # 内存间接寻址
                    pass           
                
                # 执行指令
                # load 
                if op[3:] == "000":
                    print("执行 load R" + str(int(reg_address,2)) + ", #" + str(int(int(memadd_list[0],2)/4)))
                    self.control.LOAD(reg_address,memadd_list)
                    
                # store 
                if op[3:] == "001":
                    print("执行 store R" + str(int(reg_address,2)) + ", #" + str(int(int(memadd_list[0],2)/4)))
                    self.control.STORE(reg_address,memadd_list)
                    
                # bgt if reg_address的数>0,跳转
                if op[3:] == "010":
                    print("执行 bgt R" + str(int(reg_address,2)) + ", #" + str(int(int(memadd_list[0],2)/4)))
                    self.is_jump = self.control.BGT(reg_address)
                    if self.is_jump:
                        self.jump_to_addr = memadd_list[0]
                        
            elif op[:3] == "100": # 属于IM型指令 第6-10为寄存器地址 第11-15为寄存器地址 第16-31为内存地址
                
                reg_savead = instruction_str[6:11] # 取出形式地址       
                reg_a1 = instruction_str[11:16]   
                imme = instruction_str[16:]
                
                if op[3:] == "000":                
                    self.control.ADDI(reg_savead,reg_a1,imme)
                if op[3:] == "010":                
                    self.control.SUBI(reg_savead,reg_a1,imme)
                if op[3:] == "011":                
                    self.control.MULI(reg_savead,reg_a1,imme)
                if op[3:] == "100":                
                    self.control.DIVI(reg_savead,reg_a1,imme)                    
                
                        
            elif op == "111111": #运行到全1指令，表示指令已经写入内存完毕，结束
                self.is_end = 1
                print("恭喜！程序运行结束！")                                     
                
            return [self.is_jump,self.jump_to_addr,self.is_end]
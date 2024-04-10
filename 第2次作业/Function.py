# -*- coding: utf-8 -*-

class Func:
    def __init__(self,word_len,mem_len):
        self.word_len=word_len
        self.mem_len=mem_len
    
    # 形式地址转物理地址
    # eg.将地址 由 15 转成物理地址 '00000000000000000000000000001111'
    def To_real_address(self,num,temp_word_len):
        str_bin = bin(num).replace('0b','')
        add = (temp_word_len - len(str_bin))*'0'+str_bin
        return add
    
    # 将十进制数转为二进制补码表示
    def To_binary(self,decimal):
        if decimal >= 0: # 如果是正数和零
            str_binary = bin(decimal).replace('0b','')
            str_binary = str_binary.zfill(self.word_len) # 0填充为32位
            binary_list = [int(j) for j in str_binary]
        else: # 如果是负数
            str_binary = bin(2**self.word_len+(decimal)).replace('0b','') # 取反+1
            binary_list = [int(j) for j in str_binary]
        return binary_list
    
    
    # 将二进制补码转为十进制数
    def To_decimal(self,binary_list):
        if binary_list[0] == 0: # 如果是正数或零
            str_binary = [str(int(j)) for j in binary_list]
            str_binary = ''.join(str_binary)
            num = int(str_binary,2)
        else: # 如果是负数
            temp = []
            for i in range(self.word_len):
                temp.append(binary_list[i])
            for i in range(self.word_len):# 取反
                temp[i] = not temp[i]
            flag = 1
            for i in range(self.word_len-1,-1,-1): # 再+1
                if flag:
                    flag = temp[i]
                    temp[i] = not temp[i] 
                else:
                    break
            str_binary = [str(int(j)) for j in temp]
            str_binary = ''.join(str_binary)
            num = -1*int(str_binary,2)
        return num
    
    # 由内存id获取对应的内存块,一个形式地址=4个cell，一个cell对应一个物理地址
    def MemId_toBlock(self,mem_id):
        memadd_list=[]
        for i in range(4):
            temp=int(mem_id[1:])*4+i #去除第一个字符，即“#”
            memadd_list.append(self.To_real_address(temp,self.word_len))
        return memadd_list
   
    # 根据第一个单元地址，返回四个单元块的地址
    # first_add = "0000100001000100"
    def FirstAddress_toBlock(self,first_add):
        # first_add = instruction_ls[11:27]
        memadd_list = []
        num = int(first_add,2)
        for i in range(4):
            mem_id =  num+i
            memadd_list.append(self.To_real_address(mem_id,self.word_len))
        return memadd_list
    
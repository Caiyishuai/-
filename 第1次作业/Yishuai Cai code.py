# -*- coding: utf-8 -*-



# 形式地址转物理地址
# eg.将地址 由 15 转成物理地址 '00000000000000000000000000001111'
# 传入：num 整型，比如 15
# 返回：add str字符串类型，比如'00000000000000000000000000000011'
def To_real_address(num):
    str_bin = bin(num).replace('0b','')
    add = (word_len - len(str_bin))*'0'+str_bin
    return add


# 将十进制数转为二进制补码表示
# 传入：decimal 整型，比如10
# 返回：binary_list  列表,列表里是32个bool类型，比如[False, True,....., False]
def To_binary(decimal):
    if decimal >= 0: # 如果是正数和零
        str_binary = bin(decimal).replace('0b','')
        str_binary = str_binary.zfill(word_len) # 0填充为32位
        binary_list = [bool(int(j)) for j in str_binary]
    else: # 如果是负数
        str_binary = bin(2**word_len+(decimal)).replace('0b','') # 取反+1
        binary_list = [bool(int(j)) for j in str_binary]
    return binary_list


# 将外部数据写入内存中
# 传入：memory_add  str字符串类型，比如 "#0"
#        num         整型，比如 15
def Write(memory_add,num):
    try:
        memory_add = int(memory_add[1:])*4
        binary_list = To_binary(num)
        
        for i in range(4):  # 将 binary_list 中的内容写入内存
            memory_add_bin = To_real_address(memory_add+i)
            for j in range(mem_len):
                memory[memory_add_bin][j] = binary_list[i*mem_len+j]
                
        print("已在内存地址第 "+ str(memory_add) +" - " + str(memory_add + 4-1) +\
              " 中写入数据："+ str(num))
    except:
        print("写入内存错误！")           


# 从内存中加载数据到寄存器
# 传入：reg_id      str字符串类型，比如 "r0"
#       memory_add  str字符串类型，比如 "#0"
def Load(reg_id,memory_add):
    try:
        reg_id = int(reg_id[1:])
        reg_add_bin = To_real_address(reg_id) # 先转为物理地址
        memory_add = int(memory_add[1:])*4
        
                
        for i in range(4): # 将内存四个单元的内容写入寄存器
            reg_add_bin = To_real_address(reg_id) 
            memory_add_bin = To_real_address(memory_add+i) # 先转为物理地址
            for j in range(mem_len): 
                registers[reg_add_bin][i*mem_len+j] = memory[memory_add_bin][j]
                
        #打印输出
        output = [str(int(j)) for j in registers[reg_add_bin]]
        print("已从内存第 "+ str(memory_add) +" - " + str(memory_add + 4-1) +\
              " 个单元中加载数据 "+ ''.join(output) + " 到寄存器 " + str(reg_id))
    except:
        print("寄存器加载数据错误！")


# 将两寄存器中的数相加存入另一寄存器
# 传入：reg1_id  reg3_id  reg2_id     str字符串类型，比如 "r0"
def Add(reg3_id,reg1_id,reg2_id): # 加法器的实现
    try:
        reg1_id = To_real_address(int(reg1_id[1:]))
        x = registers[reg1_id]
        reg2_id = To_real_address(int(reg2_id[1:]))
        y = registers[reg2_id]
        reg3_id = To_real_address(int(reg3_id[1:]))   
        z = registers[reg3_id]
        
        flag = 0
        for i in range(mem_len*4-1,-1,-1): # 两二进制补码相加
            z[i] = flag^x[i]^y[i] # ^表示异或
            flag = (x[i] and y[i]) + ((x[i]^y[i]) and flag)
    except:
        print("加法计算发生错误！")


# 将寄存器中的数据写入内存
# 传入：reg_id      str字符串类型，比如 "r0"
#       memory_add  str字符串类型，比如 "#0"
def Store(reg_id,memory_add):
    try:
        reg_id = int(reg_id[1:])
        reg_add_bin = To_real_address(reg_id)
        memory_add = int(memory_add[1:])*4
        
        for i in range(4): # 将寄存器的内容写入四个单元的内存
            memory_add_bin = To_real_address(memory_add+i)
            for j in range(mem_len):
                memory[memory_add_bin][j] = registers[reg_add_bin][i*mem_len+j]
        
        #打印输出
        output = [str(int(j)) for j in registers[reg_add_bin]]
        print("已将寄存器 "+ str(reg_id)+ " 中的数据 " + ''.join(output) + \
              " 写入内存第 "+ str(memory_add) +" - " + str(memory_add + 4-1) +" 的单元中" )
    except:
        print("寄存器写入内存错误！")


# 将二进制补码转为十进制数
# 传入： binary_list   列表,列表里是32个bool类型，比如[False, True,....., False]
# 返回： num  整型 比如 15
def To_decimal(binary_list):
    if binary_list[0] == 0: # 如果是正数或零
        str_binary = [str(int(j)) for j in binary_list]
        str_binary = ''.join(str_binary)
        num = int(str_binary,2)
    else: # 如果是负数
        
        temp = []
        for i in range(word_len): # 相当于 temp = copy.deepcopy(binary_list) 
            temp.append(binary_list[i])
        
        for i in range(word_len):# 取反
            temp[i] = not temp[i]
        flag = 1
        for i in range(word_len-1,-1,-1): # 再+1
            if flag:
                flag = temp[i]
                temp[i] = not temp[i] 
            else:
                break
            
        str_binary = [str(int(j)) for j in temp]
        str_binary = ''.join(str_binary)
        num = -1*int(str_binary,2)
        
    return num

               
# 将内存中的数据读出 
# 传入： memory_add  str字符串类型，比如 "#0"       
def Read(memory_add):
    try:
        memory_add = int(memory_add[1:])*4
        binary_list = []
        
        for i in range(4): # 将四行内存单元的内容装入 binary_list
            memory_add_bin = To_real_address(memory_add+i)
            binary_list.extend(memory[memory_add_bin]) # binary_list   列表,列表里是32个bool类型，比如[False, True,....., False]      
            
        num = To_decimal(binary_list) # 二进制补码转为十进制数
        
        print("内存第 "+ str(memory_add) +" - " + str(memory_add + 4-1) +" 单元中的数据为：" + str(num))
    except:
        print("读取内存错误！")

if __name__ == '__main__':  
    
    memory = {}
    registers = {}
    
    word_len = 32 # 字长
    mem_len = 8 # 内存一个单元的大小
   
    # 初始化内存中前四个地址中的内容,每个地址占四行
    # memory['00000000000000000000000000001111']=[False, False, False, False, False, False, False, False]
    for i in range(4*4):
        add = To_real_address(i)
        memory[add] = [] # 二进制bool类型
        for j in range(mem_len):
            memory[add].append(bool(0))
    
    
    # 初始化前4个寄存器中的内容   
    # registers['00000000000000000000000000000001']=[False, False, False, False, ....., False, False, False, False]
    for i in range(4):
        add = To_real_address(i)
        registers[add] = []
        for j in range(word_len):
            registers[add].append(bool(0))
        
    Write("#0",2147483647)             
    Write("#1",-2147483648)    
    Write("#2",0)
    Write("#3",9999999)
    
    Load("r1","#0")
    Load("r2","#1")
    Add("r3","r1","r2")
    Store("r3","#3")
    
    Read("#0")
    Read("#1")     
    Read("#2")
    Read("#3")

# =============================================================================
# #结果输出
# 已在内存地址第 0 - 3 中写入数据：2147483647
# 已在内存地址第 4 - 7 中写入数据：-2147483648
# 已在内存地址第 8 - 11 中写入数据：0
# 已在内存地址第 12 - 15 中写入数据：9999999
# 已从内存第 0 - 3 个单元中加载数据 01111111111111111111111111111111 到寄存器 1
# 已从内存第 4 - 7 个单元中加载数据 10000000000000000000000000000000 到寄存器 2
# 已将寄存器 3 中的数据 11111111111111111111111111111111 写入内存第 12 - 15 的单元中
# 内存第 0 - 3 单元中的数据为：2147483647
# 内存第 4 - 7 单元中的数据为：-2147483648
# 内存第 8 - 11 单元中的数据为：0
# 内存第 12 - 15 单元中的数据为：-1
# 
# =============================================================================

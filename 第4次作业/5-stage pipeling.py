# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 16:35:33 2021

@author: REESE
"""

# 判断指令间依赖关系
def Is_dependences(ins,nxt_ins):
    '''
    param : ins 当前指令
            nxt_ins 当前指令的前一条指令

    return : is_dep (true 具有依赖性 ; false 不具有依赖性)
    '''
    is_dep = 0 # 写后读RAW 1   写后写WAW 2  读后写WAR 3
    # 写后读   load 和 ALU
    if ins['op_type'] == 1 and nxt_ins['op_type'] == 2 and ins['rd'] == nxt_ins['rs']:
        is_dep = 1   
    # 写后读   ALU 和 store
    if ins['op_type'] == 2 and nxt_ins['op_type'] == 3 and ins['rd'] == nxt_ins['rd']:
        is_dep = 1
    # 读后写   store 和 addi 读x1,不更改x1  写x1
    if ins['op_type'] == 3 and nxt_ins['op_type'] == 4 and ins['rs'] == nxt_ins['rd']:
        is_dep = 3
    # 写后读 addi 和 bne 
    if ins['op_type'] == 4 and nxt_ins['op_type'] == 5 and ins['rd'] == nxt_ins['rd']:
        is_dep = 1
    # 读后写 load 和 addi 
    if ins['op_type'] == 1 and nxt_ins['op_type'] == 4 and ins['rs'] == nxt_ins['rd']:
        is_dep = 3
    # 读后读 load 和 store 
    if ins['op_type'] == 1 and nxt_ins['op_type'] == 3 and ins['rs'] == nxt_ins['rs']:
        is_dep = 3
    return is_dep

# 创建依赖关系表
def Make_dep_table(instruction_ls):
    '''
    :param instruction_ls: 指令列表，各项为字典。如[{'op': 'fld', 'rd': 'f0', 'rs': 'x1', 'imm': 0, 'op_type': 1, 'index': 0}, {'op': 'fadd.d', 'op_type': 2, 'rd': 'f4', 'rs': 'f0', 'rt': 'f2', 'index': 1}, {'op': 'fsd', 'rd': 'f4', 'rs': 'x1', 'imm': 0, 'op_type': 3, 'index': 2}, {'op': 'addi', 'op_type': 4, 'rd': 'x1', 'rs': 'x1', 'offset': 32, 'index': 3}, {'op': 'bne', 'op_type': 5, 'rd': 'x1', 'rs': 'x2', 'jw_addr': 'Loop', 'index': 4}, {'op': 'fld', 'rd': 'f1', 'rs': 'x3', 'imm': 0, 'op_type': 1, 'index': 5}]
    :return: 依赖关系列表，各项为字典。如[{'RAW': [], 'WAW': [], 'WAR': []}, {'RAW': [0], 'WAW': [], 'WAR': []}, {'RAW': [1], 'WAW': [], 'WAR': [0]}, {'RAW': [], 'WAW': [], 'WAR': [2, 0]}, {'RAW': [3], 'WAW': [], 'WAR': []}, {'RAW': [], 'WAW': [], 'WAR': []}]
    '''
    ins_ls_len = len(instruction_ls)
    dep_table = []
    for i in range(ins_ls_len):
        ls = {}
        ls["RAW"] = []
        ls["WAW"] = []
        ls["WAR"] = []
        nxt_ins = instruction_ls[i]
        for j in range(i-1, -1, -1):
            ins = instruction_ls[j]
            is_dep = Is_dependences(ins,nxt_ins)#判断两条指令的依赖性
            # print(i,j,is_dep)
            if is_dep == 1:
                ls["RAW"].append(j)
            elif is_dep == 2:
                ls["WAW"].append(j)
            elif is_dep == 3:
                ls["WAR"].append(j)
        dep_table.append(ls)
    return dep_table

def Get_dependences(ins_index,dep_type):
    '''
    :param ins_index: 该指令在指令列表中的下标
    :param dep_type: 依赖类型，字符串，如'RAW'
    :return:[]列表，列表内容为与该指令有依赖关系的指令下标，如[2,0]
    '''
    if dep_type == "RAW":
        return dep_table[ins_index][dep_type]#dep_table为各项为字典的列表，每个字典对应1条指令，[ins_index]为指令下标。dep_table[ins_index]为字典，[dep_type]为字典内的键值
    elif dep_type == "WAW":
        return dep_table[ins_index][dep_type]
    elif dep_type == "WAR":
        return dep_table[ins_index][dep_type]

# 输入的指令,各项为字典的列表，每个字典代表一条指令。
instruction_ls=[{'op': 'fld', 'rd': 'f0', 'rs': 'x1', 'imm': 0, 'op_type': 1, 'index':0},
                {'op': 'fadd.d', 'op_type': 2, 'rd': 'f4', 'rs': 'f0', 'rt': 'f2', 'index':1},
                {'op': 'fsd', 'rd': 'f4', 'rs': 'x1', 'imm': 0, 'op_type': 3, 'index':2},
                {'op': 'addi', 'op_type': 4, 'rd': 'x1', 'rs': 'x1', 'offset': 32, 'index':3},
                {'op': 'bne', 'op_type': 5, 'rd': 'x1', 'rs': 'x2', 'jw_addr': 'Loop', 'index':4},
                {'op': 'fld', 'rd': 'f1', 'rs': 'x3', 'imm': 0, 'op_type': 1, 'index':5}]

# 绘制输入指令的依赖关系表
dep_table = Make_dep_table(instruction_ls)

# 构建flag（阶段标记）和stall（阻塞标记），并初始化
instruction_ls_len = len(instruction_ls)
stall = [-1]*instruction_ls_len
flag = [0]*instruction_ls_len #[0,0,0,0,0,0]

# 复制待运行的指令集【python中直接赋值会使用同一内存地址，只能一一赋值】
instruction_ls_copy = []
for i in range(instruction_ls_len):
    instruction_ls_copy.append(instruction_ls[i])

# 相关标记
pc = 0  # 只会被bne指令修改，bne指令的stall
mem = 0  # IF阶段，指令一定取自内存？
decode =0 # ID&取数阶段，译码器
alu = 0 # EX阶段，运算器
data_mem = 0 # MEM阶段，访问内存
reg = 0# WB阶段，写回寄存器
i = 0 # 节拍

while instruction_ls_copy:
    i = i+1
    print("第 ", i, " 个节拍")

    # 复制待运行的指令集
    temp = []
    temp_len = len(instruction_ls_copy)
    for j in range(temp_len):
        temp.append(instruction_ls_copy[j])

    for ins in instruction_ls_copy:
        index = ins['index']# 该指令在指令列表中的下标，[0,1,2,3,4,5]
        t = flag[index] + 1# 该指令的阶段标记+1，表示该指令的下一阶段
        if t == 1:   # 下一阶段为取指阶段，表示该指令当前还未开始执行
            if(mem == 0 and pc == 0):# 指令内存和PC均未被占用（表示该指令不需要跳转，即bne指令未进行到译码阶段）
                mem = 1  # 占用取指mem
                flag[index] = t  # 更新阶段【资源均可用，可执行，所以可以更新阶段】
                stall[index] += 1  # 开始计数stall【刚开始执行，stall由初始的-1更新为0】
                continue
            if pc == 1:  # 说明前面是bne指令，即bne指令进行到译码阶段
                stall[index] += 1 # bne指令后有1拍延迟
            else: # mem==1 and pc == 0,即指令内存被占用【前一条指令因为某原因堵塞在IF阶段了】
                continue
        elif t == 2:  # 下一阶段为译码&取数阶段
            if decode == 0:# 译码器未被占用
                pre_instruction_index = Get_dependences(index,"RAW")  # 获得与该指令有RAW相关性的指令集
                is_stop = 0  # 标记是否被阻塞 0：未阻塞，1：阻塞。初始化为0
                for pre_index in pre_instruction_index:    # 遍历看相关指令是否用完相关寄存器
                    # 标记阻塞的case1:当前指令为store，相关指令运行到前4个阶段；case2：相关指令运行到前三个阶段
                    if (ins['op'] == 'fsd' and flag[pre_index] < 5) or flag[pre_index] < 4:
                        is_stop = 1  # 标记阻塞
                        break
                if is_stop == 0:  # 如果未被阻塞，即可以进入第二个阶段
                    mem = 0  # 释放取指mem
                    decode = 1  # 占用译码器
                    flag[index] = t  # 更新阶段
                    if ins['op'] == 'bne':  # bne指令在ID阶段将占用pc
                        pc = 1
                    continue
            
            # 因decode占用阻塞（decode==1） 或 因相关性阻塞（is_stop==1）
            stall[index] += 1  # stall+1
        elif t == 3:  # 下一阶段为执行阶段
            if alu == 0:# 运算器未被占用，可以成功进入到EX阶段
                decode = 0  # 释放译码器
                if ins['op'] == 'bne':  # bne在decode阶段之后已执行结束，删除指令并释放pc
                    pc = 0
                    temp.remove(ins)
                    continue
                flag[index] = t  # 更新阶段
                alu = 1  # 占用alu
            else:  # stall+1
                stall[index] += 1  # stall+1
        elif t == 4:# 当前指令的下一阶段为MEM阶段
            if data_mem == 0:# 内存未被占用，可以成功进入MEM阶段
                alu = 0  # 释放alu
                data_mem = 1  # 占用数据内存
                flag[index] = t  # 更新阶段
            else:  # stall+1
                stall[index] += 1  # stall+1
        elif t == 5:# 当前指令的下一阶段为WB阶段
            if reg == 0: #寄存器未被占用
                pre_instruction_index = Get_dependences(index, "WAW")  # 获得与该指令有“写后写”相关性的指令集
                is_stop1 = 0  # 标记是否被阻塞 0：未阻塞，1：阻塞。初始化为0
                for pre_index in pre_instruction_index:    # 遍历看相关指令是否用完相关寄存器
                    if flag[pre_index] != -1:   # 在列表说明未执行(WB)完，都应被阻塞
                        is_stop1 = 1  # 标记阻塞
                        break
                    # 如果用完寄存器或指令运行完，看下一条相关指令
                    
                pre_instruction_index = Get_dependences(index, "WAR")  # 获得具有“读后写”相关性的指令集
                is_stop2 = 0  # 标记是否被阻塞 0 未阻塞，1 阻塞
                for pre_index in pre_instruction_index:    # 遍历看相关指令是否用完相关寄存器
                    if flag[pre_index] < 3:    # 如果未运行(EX)完且未读完
                        is_stop2 = 1  # 标记阻塞
                        break
                    # 如果用完寄存器或指令运行完，看下一条相关指令

                if is_stop1 == 0 and is_stop2 == 0:  # 如果未被阻塞，可以成功进入WB阶段
                    data_mem = 0  # 释放data_mem
                    if ins['op'] == 'addi':  # addi在该阶段已执行结束，删除指令
                        temp.remove(ins)
                        continue
                    reg = 1  # 占用reg
                    flag[index] = t  # 更新阶段
                    continue
            
            # 因 reg 占用阻塞reg ==1 或因相关性阻塞is_stop1 == 1 or is_stop2 == 1
            stall[index] += 1  # stall+1
            # break
        elif t == 6:  # 指令在该阶段已执行结束，释放reg并删除指令
            reg = 0
            temp.remove(ins)

    #将待运行的指令集（temp)复制到instruction_ls_copy中
    instruction_ls_copy = [] #置为空
    temp_len = len(temp)
    for j in range(temp_len):
        instruction_ls_copy.append(temp[j])

    #输出各节拍的flag和stall
    print("flag:", flag)
    print("stall:", stall)

print("\n流水线输出:")
for index,ins in enumerate(instruction_ls):
    if ins['op_type'] == 1 or ins['op_type'] == 3:# fld,fsd
        print(ins['op']+" "+ins['rd']+" " +
              str(ins['imm'])+"("+ins['rs']+")")
    if ins['op_type'] == 2:# fadd
        print(ins['op']+" "+ins['rd']+" "+ins['rs']+" "+ins['rt'])
    if ins['op_type'] == 4:# addi
        print(ins['op']+" "+ins['rd']+" "+ins['rs']+" "+str(ins['offset']))
    if ins['op_type'] == 5:# bne
        print(ins['op']+" "+ins['rd']+" "+ins['rs']+" "+ins['jw_addr'])
    if index < instruction_ls_len - 1: # 若当前指令非最后一条指令
        stall_num = stall[index+1] # 下一条指令的受阻情况
        for i in range(stall_num):
            print("stall")
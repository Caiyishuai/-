# =============================================================================
# 判断两条指令间的依赖性
# =============================================================================
def Is_dependences(ins, nxt_ins):
    '''
    param : ins 当前指令
    param : nxt_ins 当前指令的前一条指令

    return : is_dep (true 具有依赖性 ; false 不具有依赖性)
             stall (该依赖应停顿的次数)
    '''
    is_dep = False
    stall = -1
    # 写后读   load 和 ALU
    if ins['op_type'] == 1 and nxt_ins['op_type'] == 2 and ins['rd'] == nxt_ins['rs']:
        is_dep = True
        stall = stall_page(ins, nxt_ins)
    # 写后写   ALU 和 store
    if ins['op_type'] == 2 and nxt_ins['op_type'] == 3 and ins['rd'] == nxt_ins['rd']:
        is_dep = True
        stall = stall_page(ins, nxt_ins)
    # addi 和 bne
    if ins['op_type'] == 4 and nxt_ins['op_type'] == 5 and ins['rd'] == nxt_ins['rd']:
        is_dep = True
        stall = stall_page(ins, nxt_ins)

    return is_dep, stall

# =============================================================================
# 停顿表:用于判断相关指令的停顿数
# 当两条指令具有依赖性时调用
# =============================================================================
def stall_page(ins, nxt_ins):
    '''
    param : ins 当前指令
    param : nxt_ins 当前指令的前一条指令

    op1 产生结果的指令 ; op2 使用结果的指令
        op = 1 load double (fld)
        op = 2 fp alu op (fadd.d)
        op = 3 sd double (fsd)
        op = 4 addi
        op = 5 bne

    return : stall(int) 停顿次数
    '''
    stall = 0
    op1 = ins['op_type']
    op2 = nxt_ins['op_type']
    if op1 == 2 and op2 == 2:    # fp alu op → fp alu op : stall=3
        stall = 3
    elif op1 == 2 and op2 == 3:  # fp alu op → sd double : stall=2
        stall = 2
    elif op1 == 1 and op2 == 2:  # load double → fp alu op : stall=1
        stall = 1
    elif op1 == 1 and op2 == 3:  # load double → sd double : stall=0
        stall = 0
    elif op1 == 4 and op2 == 5:  # addi → bne : stall=1
        stall = 1
    elif op1 == 5 and op2 == None:  # 这里表示bne为一次基本块的出口
        stall = 1

    return stall

# =============================================================================
# 读取文件，删除空行
# =============================================================================
def instruction_read(path):
    file = path
    with open(file, 'r') as fr:   # 删除空行
        context = fr.read().splitlines()
        context = list(filter(None, context))

    return context

# =============================================================================
# 指令译码
# 对每条指令进行字段拆分处理
# =============================================================================
def instruction_decode(context):
    '''
    param : context 指令文本内容
    return : reg_flag  寄存器使用情况
             instruction_ls 初始指令列表
    '''
    instruction_ls = []  # 指令列表
    reg_flag = []  # 寄存器使用情况

    # 初始化32个寄存器
    for i in range(32):
        reg_flag.append(0)

    # 拆分字段为
    # op_type : 指令类型(int) ; op : 指令名称(str) ;
    # rd : 目的操作数的寄存器 ; rs : 源操作数1的寄存器 ; rs : 源操作数2的寄存器
    # offset : 偏移量 ; jw_addr : 跳转地址 ; imm : 立即数
    for line in context:
        line = line.split(' ')
        print(line)
        instruction = {}
        instruction['op'] = line[0]  # 提取op,比如 fld
        op_addr = line[1].split(',')

        # 例 fld f0 0(x1)
        if instruction['op'] == 'fld' or instruction['op'] == 'fsd':
            instruction['rd'] = op_addr[0]
            imm_index = op_addr[1].index('(')
            instruction['rs'] = op_addr[1][imm_index+1:-1]

            instruction['imm'] = int(op_addr[1][:imm_index])
            if instruction['op'] == 'fld':
                instruction['op_type'] = 1  # 从内存中加载数据到寄存器
            elif instruction['op'] == 'fsd':
                instruction['op_type'] = 3  # 将寄存数据写入内存
        
        # 例 fadd.d f4 f0 f2
        elif instruction['op'] == 'fadd.d':  # ALU操作,都是寄存器的操作
            instruction['op_type'] = 2
            instruction['rd'] = op_addr[0]
            instruction['rs'] = op_addr[1]
            instruction['rt'] = op_addr[2]

            f_num = int(instruction['rt'][1:])  # 标记f2寄存器是加数存放的
            reg_flag[f_num] = 1  # 标记已经被使用

        # 例 addi x1 x1 32
        elif instruction['op'] == 'addi': 
            instruction['op_type'] = 4
            instruction['rd'] = op_addr[0]
            instruction['rs'] = op_addr[1]
            instruction['offset'] = int(op_addr[2])

        # 例 bne x1 x2 Loop
        elif instruction['op'] == 'bne': 
            instruction['op_type'] = 5
            instruction['rd'] = op_addr[0]
            instruction['rs'] = op_addr[1]
            instruction['jw_addr'] = op_addr[2]

        instruction_ls.append(instruction)

    return reg_flag, instruction_ls

# =============================================================================
# 循环展开
# =============================================================================
def instruction_unroll(reg_flag, instruction_ls, loop_num):
    '''
    param : reg_flag 寄存器使用情况
            instruction_ls 初始指令列表
            loop_num  循环次数
    return : unrolling_ls  循环展开后的指令列表
    '''
    unrolling_ls = []
    start_f = 0  # 从起始寄存器开始看
    start_x = 0  # 从内存起始位置
    overhead_index = 0  # 标记循环体的位置
    
    # 找到 addi 指令
    for instruction in instruction_ls:
        if instruction['op_type'] == 4:
            break
        else:
            overhead_index += 1
    
    # 展开指令后更新相关信息
    for i in range(loop_num):
        temp_ls = []
        for instruction in instruction_ls:
            new_ins = {}
            for k, v in instruction.items():
                new_ins[k] = v
            
            # 遇 addi 结束循环
            if instruction['op_type'] == 4:  
                break

            # load型 例 fld f0,0(x1)
            elif instruction['op_type'] == 1:  
                while reg_flag[start_f]:  #  目的寄存器找未使用过的寄存器
                    start_f += 2
                reg_flag[start_f] = 1
                new_ins['rd'] = 'f'+str(start_f)
                new_ins['imm'] = start_x
            
            # store型 例 fsd f4,0(x1)
            elif instruction['op_type'] == 3:  
                new_ins['rd'] = 'f'+str(start_f)  # 和前面相同
                new_ins['imm'] = start_x
                start_x += 8

            # ALU型 例 fadd.d f4,f0,f2
            # 均为寄存器操作
            elif instruction['op_type'] == 2:  
                new_ins['rs'] = 'f'+str(start_f)  # load存放寄存器 = fadd.d取数寄存器
                while reg_flag[start_f]:
                    start_f += 2
                reg_flag[start_f] = 1
                new_ins['rd'] = 'f'+str(start_f)  # 目的寄存器找未使用过的寄存器

            temp_ls.append(new_ins)
        unrolling_ls.append(temp_ls)

    # 调整偏移量和跳转地址
    temp_ls = []
    instruction = instruction_ls[overhead_index]  # overhead
    instruction['offset'] = instruction['offset'] * loop_num
    temp_ls.append(instruction)  # 'addi x1,x1,32'
    temp_ls.append(instruction_ls[overhead_index+1])  # 'bne x1,x2,Loop'
    unrolling_ls.append(temp_ls)
    
    # 加入stall
    unrolling_ls_flatten = []  
    for temp_ls in unrolling_ls:
        unrolling_ls_flatten.extend(temp_ls)
    unrolling_real_ls = []
    unrolling_real_ls.append(unrolling_ls_flatten[0])
    for i in range(1, len(unrolling_ls_flatten)):
        nxt_ins = unrolling_ls_flatten[i] # 取出当前指令
        
        # 判断 bne,bne后一条空指令
        if nxt_ins['op_type'] == 5:  
            stall_ins = {}
            stall_ins['op_type'] = -1
            unrolling_real_ls.append(stall_ins)
            break
        ins = unrolling_ls_flatten[i-1]  # 取出当前指令的前一条指令
        is_dep, stall = Is_dependences(ins, nxt_ins)  # 判断相关性
        
        # 若相关,插入相应 stall 数
        if is_dep:
            stall_ins = {}
            stall_ins['op_type'] = -1
            for j in range(stall):
                unrolling_real_ls.append(stall_ins)
        unrolling_real_ls.append(nxt_ins)

    # 输出循环展开结果
    print("\n循环展开:")
    for ins in unrolling_real_ls:
        if ins['op_type'] == -1:
            print("stall")
        if ins['op_type'] == 1 or ins['op_type'] == 3:
            print(ins['op']+" "+ins['rd']+" " +
                  str(ins['imm'])+"("+ins['rs']+")")
        if ins['op_type'] == 2:
            print(ins['op']+" "+ins['rd']+" "+ins['rs']+" "+ins['rt'])
        if ins['op_type'] == 4:
            print(ins['op']+" "+ins['rd']+" "+ins['rs']+" "+str(ins['offset']))
        if ins['op_type'] == 5:
            print(ins['op']+" "+ins['rd']+" "+ins['rs']+" "+ins['jw_addr'])

    return unrolling_ls

# =============================================================================
# 指令调度
# =============================================================================
def instruction_schedule(unrolling_ls):
    new_ls = []
    loop_in_len = len(unrolling_ls[0])  # 循环内指令长度
    
    # 调整指令顺序
    for i in range(loop_in_len):
        for j in range(loop_num):
            new_ls.append(unrolling_ls[j][i])

    # 插入最后两个指令
    new_ls.insert(-2, unrolling_ls[-1][0])
    new_ls.insert(-1, unrolling_ls[-1][1])

    # 找到退出循环的指令
    loop_out_index = -1
    for i, ins in enumerate(new_ls):
        if ins['op_type'] == 4:
            loop_out_index = i
            break
    
    mem_addr = new_ls[loop_out_index]['rd']    # 内存地址
    offset = new_ls[loop_out_index]['offset']  # 偏移量

    # 相对偏移量转换
    for i in range(loop_out_index, len(new_ls)):
        ins = new_ls[i]
        # 发现了读后写和插入的指令有依赖
        if ('rs' in ins) and ('imm' in ins) and (ins['rs'] == mem_addr):
            ins['imm'] -= offset
            new_ls[i] = ins

    # 输出调度后的结果
    print("\n指令调度:")
    for ins in new_ls:
        if ins['op_type'] == 1 or ins['op_type'] == 3:  # load 和 store 型
            print(ins['op']+" "+ins['rd']+" " +
                  str(ins['imm'])+"("+ins['rs']+")")
        if ins['op_type'] == 2:   # ALU 计算型
            print(ins['op']+" "+ins['rd']+" "+ins['rs']+" "+ins['rt'])
        if ins['op_type'] == 4:   # addi 型
            print(ins['op']+" "+ins['rd']+" "+ins['rs']+" "+str(ins['offset']))
        if ins['op_type'] == 5:   # bne 跳转判断型
            print(ins['op']+" "+ins['rd']+" "+ins['rs']+" "+ins['jw_addr'])

if __name__ == '__main__':
    
    # 定义路径，读取指令文件
    path = "code.txt"
    context = instruction_read(path)

    # 指令译码
    reg_flag, instruction_ls = instruction_decode(context)

    # 指令循环展开
    loop_num = 4
    unrolling_ls = instruction_unroll(reg_flag, instruction_ls, loop_num)

    # 指令调度
    instruction_schedule(unrolling_ls)
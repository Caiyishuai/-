import numpy
'''
作业要求
    write a piece code that unrolling our examples with instruction scheduling
    假设循环展开4次
    f2数据固定不变，R1里面存放的是拿来与Imm相加的操作数(在当前不变)
    op = 1 load
    op = 2 alu
    op = 3 sd
    op = 4 addi
    op = 5 bne
'''





instruction = [ 'fld f0 0(R1)',
                'fadd.d f4,f0,f2',
                'fsd f4,0(R1)',
                'addi R1,R1,8',
                'bne R1,R2,loop',]
fld = []
fadd = []
fsd = []
addi = []
ins_sequence = []
dependent_dict = {}
count = 0  # 用来计数bne
def reg(num):
    reg_list = []


def stall_page(ins_d1, ins_d2): #停顿表 (我现在写的是if 分支优化可以考虑用字典其他数据类型)
    '''
    op = 1 load double (fld)
    op = 2 fp alu op (fadd.d)
    op = 3 sd double (fsd)
    op = 4 addi
    op = 5 bne
    传入的都是具有相关性的
    op1 为产生结果的指令， op2为使用结果的指令，
    返回：停顿数(int)
    '''
    stall = 0
    op1 = ins_d1['op']
    op2 = ins_d2['op']
    if op1 == '2' and op2 == '2':
        stall = 3
    elif op1 == '2' and op2 == '3':
        stall = 2
    elif op1 == '1' and op2 == '2':
        stall = 1
    elif op1 == '1' and op2 == '3':
        stall = 1
    elif op1 == '4' and op2 == '5':
        stall = 1
    elif op1 == '5' and op2 == None :  # 这里表示bne为一次基本块的出口
        stall = 1
    return stall


def decoding(raw_ins):
    '''

    :param raw_ins: 原始的指令
    :return: 转换译码的指令,指令格式为字典，包括操作码，源和目的操作数，imm，
    index:表示指令位置(可考虑项目)
    '''
    split_ins = raw_ins.split(' ')
    if split_ins[0] == 'fld':
        addr = split_ins[2]
        imm_index = split_ins[2].index('(')
        addr_imm = addr[:imm_index]
        print(addr_imm)
        ins_d = {'op': '1', 'aim': split_ins[1], 'address_imm': addr_imm, 'index' : 1}
        fld.append(split_ins)
        return ins_d

    elif split_ins[0] == 'fadd.d':
        print(split_ins)
        operands = split_ins[-1].split(',')
        print(operands)
        ins_d = {'op': '2', 'aim': operands[0], 'row': [operands[1], operands[2]], 'index': 2}
        fadd.append(split_ins)
        return ins_d

    elif split_ins[0] == 'fsd':
        fadd.append(split_ins)
    elif split_ins[0] == 'addi':
        pass


def relationship(ins1_d, ins2_d):  #判断指令间是否存在相关性,相关则加入到dependant_dict
    # 指令i生成的结果可能会被指令j用到
    if ins1_d['aim'] in ins2_d['row']:
        print('第{}条指令{}与第{}条{}相关'.format(ins2_d['index'], ins2_d, ins1_d['index'], ins1_d))
        stall = stall_page(ins1_d, ins2_d)
        dependent_dict[ins2_d['index']] = [ins1_d['index'], stall]
        # 指令j数据相关于指令k，而指令k数据相关于指令i
        print(dependent_dict)
        ins0_d = dependent_dict.get(ins1_d['op'])
        if ins0_d:
            stall1 = stall_page(ins0_d,ins1_d)
            dependent_dict[ins2_d['op']] = [ins0_d['op'], stall1+stall]
    else:
        print('指令无关')
        dependent_dict[ins2_d['op']] = None



def modify_page():  #修改页表
    pass






def unrolling(ins): #利用循环展开，使得基本块循环4次

    '''首先对基本块的关系进行梳理,把关系放到dependant_dict,
    如果遇到addi设置标记，跳过加入一个列表，把addi的+8功能合并到'LD的取数
    遇到bne也是一样跳过（overhead），可以考虑存放到列表
    设置一个for循环或者计数器,来表示迭代到第几个基本快来设置：LD F10 -16（R1），ALU寄存器每次增加2'''

    pass
    #


ins1 = decoding('fld f0 0(R1)')
ins2 = decoding('fadd.d f4,f0,f2')
relationship(ins1, ins2)



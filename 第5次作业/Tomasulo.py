# -*- coding: utf-8 -*-
from LoadBufferClass import load_buffer
from StoreBufferClass import store_buffer
from RegResultStatusClass import RegisterResultStatus
from ReservationStationClass import res_station

'''
# 输入的指令
instruction_ls = [{'op': 'L.D', 'rd': 'F0', 'rs': 'R1', 'imm': 0, 'op_type': 1, 'index': 0},
                  {'op': 'MUL.D', 'op_type': 2, 'rd': 'F4', 'rs': 'F0', 'rt': 'F2', 'index': 1},
                  {'op': 'S.D', 'rd': 'R1', 'rs': 'F4', 'imm': 0, 'op_type': 3, 'index': 2},
                  {'op': 'DADDUI', 'op_type': 4, 'rd': 'R1', 'rs': 'R1', 'offset': -8, 'index': 3},
                  {'op': 'BNE', 'op_type': 5, 'rd': 'R1', 'rs': 'R2', 'jw_addr': 'Loop', 'index': 4},
                  {'op': 'L.D', 'rd': 'F0', 'rs': 'R1', 'imm': 0, 'op_type': 1, 'index': 5}]
'''

instruction_ls_string=["L.D F0,0(R1)",
                        "MUL.D F4,F0,F2",
                        "S.D 0(R1),F4",
                        "DADDUI R1,R1,#-8",
                        "BNE R1,R2,LOOP",
                        "L.D F0,0(R1)",
                        "MUL.D F4,F0,F2",
                        "S.D 0(R1),F4",
                        "DADDUI R1,R1,#-8",
                        "BNE R1,R2,LOOP"
                        ]

instruction_ls = [{'op': 'L.D', 'rd': 'F0', 'rs': 'R1', 'imm': 0, 'op_type': 1, 'index': 0},
                  {'op': 'MUL.D', 'op_type': 2, 'rd': 'F4', 'rs': 'F0', 'rt': 'F2', 'index': 1},
                  {'op': 'S.D', 'rd': 'R1', 'rs': 'F4', 'imm': 0, 'op_type': 3, 'index': 2},
                  {'op': 'DADDUI', 'op_type': 4, 'rd': 'R1', 'rs': 'R1', 'offset': -8, 'index': 3},
                  {'op': 'BNE', 'op_type': 5, 'rd': 'R1', 'rs': 'R2', 'jw_addr': 'Loop', 'index': 4},
                  {'op': 'L.D', 'rd': 'F0', 'rs': 'R1', 'imm': 0, 'op_type': 1, 'index': 5},
                  {'op': 'MUL.D', 'op_type': 2, 'rd': 'F4', 'rs': 'F0', 'rt': 'F2', 'index': 6},
                  {'op': 'S.D', 'rd': 'R1', 'rs': 'F4', 'imm': 0, 'op_type': 3, 'index': 7},
                  {'op': 'DADDUI', 'op_type': 4, 'rd': 'R1', 'rs': 'R1', 'offset': -8, 'index': 8},
                  {'op': 'BNE', 'op_type': 5, 'rd': 'R1', 'rs': 'R2', 'jw_addr': 'Loop', 'index': 9}
                  ]


instruction_ls_len = len(instruction_ls)

# 指令运行过程中的属性集
instruction_attribution = {}
instruction_attribution['stage'] = [0]*instruction_ls_len # 位于第几个状态
instruction_attribution['self_time'] = [-1]*instruction_ls_len # 自计时器
instruction_attribution['buffer_index'] = [""]*instruction_ls_len # 这条指令在哪个部件里运行 load1
instruction_attribution['buffer_type'] = [""]*instruction_ls_len # 这条指令在哪个部件里运行 add load store multi

# 复制待运行的指令集
instruction_ls_copy = []
for i in range(instruction_ls_len):
    instruction_ls_copy.append(instruction_ls[i])
    
LoadBuffer = load_buffer() 
StoreBuffer = store_buffer()
RegResultStatus = RegisterResultStatus()
ResStation = res_station()

# 存储用于打印输出
result_print = []
for i in range(instruction_ls_len):
    ls = [0]*3
    result_print.append(ls)

i = 0
pc_state = 0
# 使发射阶段每个时钟周期只能发射一条指令
Issue = 0

while instruction_ls_copy:
    LoadBuffer.print_load_buffer()
    StoreBuffer.print_store_buffer()
    RegResultStatus.print_reg_result_status()
    ResStation.print_res_station()

    i = i+1
    print("====================第 ", i, " 个节拍====================")
    Issue = 0
    # 复制待运行的指令集
    temp = []
    temp_len = len(instruction_ls_copy)
    for j in range(temp_len):
        temp.append(instruction_ls_copy[j])

    # 遍历每一条指令
    for ins in instruction_ls_copy:
        ins_index = ins['index']  # 获得指令的index
        ins_stage = instruction_attribution['stage'][ins_index]  # 看看它处于哪个阶段了
        if ins_stage == 0 and Issue == 0:  # 这条指令当前还没发射
            # 按序发射,检查前一条指令有没有到发射阶段,没有就不行
            if ins_index != 0 and instruction_attribution['stage'][ins_index - 1] < 1:
                continue
            if pc_state == 1:  # 说明pc正被占用
                continue
            if ins['op'] == 'L.D':
                # 返回 is_full = False,load_buffer_index="Load1"
                is_full, load_buffer_index = LoadBuffer.find()  # 看看LoadBuffer有没有位置多
                rd = ins['rd']
                # 返回 reg_is_full = False,reg_fu="M(F1)"或者"Add1"
                reg_is_busy, reg_fu = RegResultStatus.is_busy(rd)  # 看看RegResultStatus的要被写入的位置是不是空
                if is_full == False and reg_is_busy == False:  # 满足发射条件
                    # 有位置就占领一个LoadBuffer里的一行
                    context = str(ins['imm']) + "+" + ins['rs']
                    # 更改 LoadBuffer
                    # 在load_buffer_index这一行,修改 busy 为 True,在 address 中写入 context
                    LoadBuffer.modify(1, load_buffer_index, context)
                    # 更改 RegResultStatus
                    # 将rd 修改 busy 为 True,在 FU 中写入 context
                    context = load_buffer_index
                    RegResultStatus.modify(1, rd, load_buffer_index)
                    # 修改 指令状态
                    instruction_attribution['stage'][ins_index] += 1
                    # 启动自计时器
                    instruction_attribution['self_time'][ins_index] = 2
                    # 在哪种类型的组件中
                    instruction_attribution['buffer_type'][ins_index] = "load"
                    # 在保留站的哪个组件序号里
                    instruction_attribution['buffer_index'][ins_index] = load_buffer_index
                    print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "进入发射")
                    # 记录状态便于输出
                    result_print[ins_index][0] = i
                    Issue = 1  # 锁死Issue阶段
            elif ins['op'] == 'MUL.D':
                res_station_type = "mult"
                # 看看ReservationStation有没有位置多
                is_full, res_station_index = ResStation.find(res_station_type)
                rd = ins['rd']
                rd_reg_is_busy, rd_reg_fu = RegResultStatus.is_busy(rd)
                if not is_full and not rd_reg_is_busy:
                    # 那就看看操作数是否ok,不管ok不ok,都要写入保留栈
                    rs = ins['rs']
                    rt = ins['rt']
                    rs_reg_is_busy, rs_reg_fu = RegResultStatus.is_busy(rs)
                    prepare_vj_ok = not rs_reg_is_busy
                    rt_reg_is_busy, rt_reg_fu = RegResultStatus.is_busy(rt)
                    prepare_vk_ok = not rt_reg_is_busy
                    ResStation.modify(1, res_station_index, ins['op'], \
                                      prepare_vj_ok, prepare_vk_ok, \
                                      rs_reg_fu, rt_reg_fu)
                    # 修改 RegisterResultStatus
                    # RegResultStatus.modify(1,rd,"multi")
                    RegResultStatus.modify(1, rd, res_station_index)  # changed
                    # 修改 指令状态
                    instruction_attribution['stage'][ins_index] += 1
                    # 在哪种类型的组件中
                    instruction_attribution['buffer_type'][ins_index] = "multi"
                    # 在保留站的哪个组件序号里
                    instruction_attribution['buffer_index'][ins_index] = res_station_index
                    # 记录状态便于输出
                    result_print[ins_index][0] = i
                    if not rs_reg_is_busy and not rt_reg_is_busy:  # 操作数如果都备齐了
                        # 启动自计时器
                        instruction_attribution['self_time'][ins_index] = 10
                        print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "进入发射且数据准备好了")
                    else:
                        print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "进入发射")
                    Issue = 1
            elif ins['op'] == 'S.D':
                is_full, store_buffer_index = StoreBuffer.find()  # 看看LoadBuffer有没有位置多
                if not is_full:
                    rd = ins['rd']
                    reg_is_busy, reg_fu = RegResultStatus.is_busy(rd)  # 看看RegResultStatus的要被写入的位置是不是空
                    # print("SD "+rd+" "+str(reg_is_busy))
                    address = str(ins['imm']) + "+" + ins['rd']
                    prepare_ok = not reg_is_busy
                    # print("S.D prepare_ok", prepare_ok)
                    if prepare_ok:
                        rs = ins['rs']
                        rs_reg_is_busy, rs_reg_fu = RegResultStatus.is_busy(rs)
                        rs_prepare_ok = not rs_reg_is_busy
                        # 更改 StoreBuffer
                        StoreBuffer.modify(1, store_buffer_index, rs_prepare_ok, address, rs_reg_fu)
                        # print("S.D: rs_reg_fu" + rs_reg_fu+"rs_prepare_ok:"+str(rs_prepare_ok))
                        # 修改 指令状态
                        instruction_attribution['stage'][ins_index] += 1
                        # 在哪种类型的组件中
                        instruction_attribution['buffer_type'][ins_index] = "store"
                        # 在保留站的哪个组件序号里
                        instruction_attribution['buffer_index'][ins_index] = store_buffer_index
                        # 记录状态便于输出
                        result_print[ins_index][0] = i
                        if not rs_reg_is_busy:
                            # 启动自计时器
                            instruction_attribution['self_time'][ins_index] = 2
                            print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "进入发射且数据已准备")
                        else:
                            print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "进入发射")
                        Issue = 1
            elif ins['op'] == 'DADDUI':
                res_station_type = "add"
                # 看看ReservationStation有没有位置多
                is_full, res_station_index = ResStation.find(res_station_type)
                rd = ins['rd']
                rd_reg_is_busy, rd_reg_fu = RegResultStatus.is_busy(rd)
                if not is_full and not rd_reg_is_busy:
                    # 那就看看操作数是否ok,不管ok不ok,都要写入保留栈
                    rs = ins['rs']
                    rs_reg_is_busy, rs_reg_fu = RegResultStatus.is_busy(rs)
                    prepare_vj_ok = not rs_reg_is_busy
                    ResStation.modify(1, res_station_index, ins['op'], \
                                      prepare_vj_ok, 1, \
                                      rs_reg_fu, '# ' + str(ins['offset']))
                    # 修改 RegisterResultStatus
                    RegResultStatus.modify(1, rd, res_station_index)
                    # 修改 指令状态
                    instruction_attribution['stage'][ins_index] += 1
                    # 在哪种类型的组件中
                    instruction_attribution['buffer_type'][ins_index] = "addi"
                    # 在保留站的哪个组件序号里
                    instruction_attribution['buffer_index'][ins_index] = res_station_index
                    # 记录状态便于输出
                    result_print[ins_index][0] = i
                    if not rs_reg_is_busy:  # 操作数如果都备齐了
                        # 启动自计时器
                        instruction_attribution['self_time'][ins_index] = 2
                        print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "进入发射且数据准备好了")
                    else:
                        print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "进入发射")
                    Issue = 1
            elif ins['op'] == 'BNE':
                # 修改 指令状态
                instruction_attribution['stage'][ins_index] += 1
                # 修改 pc状态
                pc_state = 1
                rd = ins['rd']
                rs = ins['rs']
                rd_reg_is_busy, rd_reg_fu = RegResultStatus.is_busy(rd)
                rs_reg_is_busy, rs_reg_fu = RegResultStatus.is_busy(rs)
                # 记录状态便于输出
                result_print[ins_index][0] = i
                if not rd_reg_is_busy and not rs_reg_is_busy:
                    # 启动自计时器
                    instruction_attribution['self_time'][ins_index] = 1
                    print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "进入发射且数据准备好了")
                else:
                    print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "进入发射")
                Issue = 1
            continue
        elif ins_stage == 1:  # 这条指令当前还没执行(处于译码阶段)
            # print(instruction_ls_string[ins_index]+"  "+str(instruction_attribution['self_time'][ins_index]))
            if instruction_attribution['self_time'][ins_index] != -1:  # 在准备执行中了
                instruction_attribution['self_time'][ins_index] -= 1
                if instruction_attribution['self_time'][ins_index] == 0:  # 自计时器时间到
                    if ins['op'] == 'BNE':
                        pc_state = 0
                    instruction_attribution['stage'][ins_index] += 1  # 进入执行阶段2
                    print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "准备进入写回阶段")
                    # 记录状态便于输出
                    result_print[ins_index][1] = i
            else:  # 说明数据没有准备好
                # 再检查数据是否准备好
                if ins['op'] == 'MUL.D':
                    res_station_index = instruction_attribution['buffer_index'][ins_index]  # 获得这条指令在保留站中的索引
                    prepare_ok = ResStation.is_data_prepare(res_station_index)  # 检查数据是否已经准备好了
                    #                    print(prepare_ok)
                    if prepare_ok:  # 如果此时数据准备好了
                        # 启动自计时器
                        instruction_attribution['self_time'][ins_index] = 10
                        print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "数据准备好了")
                        # 记录状态便于输出
                        result_print[ins_index][1] = i
                elif ins['op'] == 'S.D':
                    res_station_index = instruction_attribution['buffer_index'][ins_index]  # 获得这条指令在保留站中的索引
                    prepare_ok = StoreBuffer.is_prepare_ok(res_station_index)  # 检查数据是否已经准备好了
                    if prepare_ok:  # 如果此时数据准备好了
                        # 启动自计时器
                        instruction_attribution['self_time'][ins_index] = 2
                        print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "数据准备好了")
                        # 记录状态便于输出
                        result_print[ins_index][1] = i
                elif ins['op'] == 'DADDUI':
                    res_station_index = instruction_attribution['buffer_index'][ins_index]  # 获得这条指令在保留站中的索引
                    prepare_ok = ResStation.is_data_prepare(res_station_index)  # 检查数据是否已经准备好了
                    if prepare_ok:  # 如果此时数据准备好了
                        # 启动自计时器
                        instruction_attribution['self_time'][ins_index] = 2
                        print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "数据准备好了")
                        # 记录状态便于输出
                        result_print[ins_index][1] = i
                elif ins['op'] == 'BNE':
                    rd = ins['rd']
                    rs = ins['rs']
                    rd_reg_is_busy, rd_reg_fu = RegResultStatus.is_busy(rd)
                    rs_reg_is_busy, rs_reg_fu = RegResultStatus.is_busy(rs)
                    if not rd_reg_is_busy and not rs_reg_is_busy:
                        # 启动自计时器
                        instruction_attribution['self_time'][ins_index] = 1
                        print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "数据准备好了")
                        # 记录状态便于输出
                        result_print[ins_index][1] = i
            continue
        elif ins_stage == 2:  # 这条指令在执行阶段了,接下来看是否可以写回了
            buffer_type = instruction_attribution['buffer_type'][ins_index]  # 先找到在哪种类型保留站
            buffer_index = instruction_attribution['buffer_index'][ins_index]  # 再找到在哪个保留站编号
            # print(buffer_index)
            if (ins['op'] == 'L.D') or (ins['op'] == 'MUL.D') or (ins['op'] == 'DADDUI'):
                if buffer_type == "load":
                    LoadBuffer.modify(0, buffer_index, "")  # 清除保留站中的数据
                elif buffer_type == "multi":
                    ResStation.modify(0, buffer_index)  # 清除保留站中的数据
                elif buffer_type == "addi":
                    ResStation.modify(0, buffer_index)  # 清除保留站中的数据
                # 将数据写入寄存器
                rd = ins['rd']
                context = "M" + str(ins_index)
                RegResultStatus.modify(0, rd, context)
                # 广播把数据写入
                StoreBuffer.broadcast(buffer_index, context)
                ResStation.broadcast(buffer_index, context)
                print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "运行结束")
                # 记录状态便于输出
                result_print[ins_index][2] = i
            elif ins['op'] == "S.D":
                StoreBuffer.modify(0, buffer_index)  # 清除保留站中的数据
                print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "运行结束")
                # 记录状态便于输出
                result_print[ins_index][2] = i
            elif ins['op'] == 'BNE':
                print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "运行结束")
                # 记录状态便于输出
                result_print[ins_index][2] = i
            # 把运行完的指令删除
            temp.remove(ins)
            # 将删除完的指令重新赋给 instruction_ls_copy
    instruction_ls_copy = []
    temp_len = len(temp)
    for j in range(temp_len):
        instruction_ls_copy.append(temp[j])

LoadBuffer.print_load_buffer()
StoreBuffer.print_store_buffer()
RegResultStatus.print_reg_result_status()
ResStation.print_res_station()

# 打印输出
print("\n")
print("%20s %8s %8s %8s" % ("Instruction", "Issue", "Exec Comp", "Write Result"))
for i, ins in enumerate(instruction_ls_string):
    print("%20s %8d %8d %8d" % (ins, result_print[i][0], result_print[i][1], result_print[i][2]))
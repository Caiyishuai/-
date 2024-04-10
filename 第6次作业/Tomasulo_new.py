# -*- coding: utf-8 -*-
from LoadBufferClass import load_buffer
from StoreBufferClass import store_buffer
from RegResultStatusClass import RegisterResultStatus
from ReservationStationClass import res_station
# 新增
from ReorderBufferClass import ReorderBuffer
from BranchTargetBufferClass import Branch_Buffer

# R1 = 7992   # 999*8
# R2 = 0
R1 = 80  # 10*8
R1_temp = R1
R2 = 0
loop_index = 0
instruction_ls_string = ["L.D F0,0(R1)",
                         "ADD.D F4,F0,F2",
                         "S.D F4,0(R1)",
                         "DADDUI R1,R1,-8",
                         "BNE R1,R2,LOOP"
                         ]

instruction_ls = [{'op': 'L.D', 'rd': 'F0', 'rs': 'R1', 'imm': 0, 'op_type': 1, 'index': 0},
                  {'op': 'ADD.D', 'op_type': 2, 'rd': 'F4', 'rs': 'F0', 'rt': 'F2', 'index': 1},
                  {'op': 'S.D', 'rd': 'R1', 'rs': 'F4', 'imm': 0, 'op_type': 3, 'index': 2},
                  {'op': 'DADDUI', 'op_type': 4, 'rd': 'R1', 'rs': 'R1', 'offset': -8, 'index': 3},
                  {'op': 'BNE', 'op_type': 5, 'rd': 'R1', 'rs': 'R2', 'jw_addr': 'Loop', 'index': 4}
                  ]

instruction_ls_string_all = []
# 存储用于打印输出
result_print = {}
for i in range(5):
    result_print[instruction_ls[i]['op']] = []

LoadBuffer = load_buffer(3)
StoreBuffer = store_buffer(3)
RegResultStatus = RegisterResultStatus(32, 32)
ResStation = res_station(5, 5)
# 增加 BTB ROB
ROB_len = 10
ROB = ReorderBuffer(ROB_len)
BTB = Branch_Buffer()

Clock = 0
PC = 0
Loop = True

while not ((not Loop) and Clock > 1 and ROB.isEmpty()):
    Clock += 1  # 时钟加一
    #    if Clock>40:
    #        break
    print("====================第 ", Clock, " 个节拍====================")
    # buffer print
    LoadBuffer.print_load_buffer()
    StoreBuffer.print_store_buffer()
    RegResultStatus.print_reg_result_status()
    ResStation.print_res_station()
    ROB.print_all()

    head, end = ROB.getHeadEnd()  # 找ROB中的头尾指针
    temp_end = end
    if end < head:
        temp_end = end + ROB_len
    for entry in range(head, temp_end):  # 遍历ROB，看该时钟周期哪些指令状态可以变更
        entry = entry % ROB_len
        # 从ROB取出一条正在执行的指令
        busy, ins, ins_state, rd, value, delay = ROB.find(entry)
        ins_index = ins['index']
        this_dest = "ROB" + str(entry)
        if ins_state == 1:      # 准备执行
            if delay != -1:     # 在准备执行中了
                delay -= 1
                ROB.setDelay(entry, delay)
                if delay == 0:  # 自计时器时间到
                    # ROB状态改写
                    if ins['op'] != 'BNE':
                        ROB.modify(entry, 2)
                        print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "准备进入写回阶段")
                        # 记录状态便于输出
                        result_print[ins['op']].append(Clock)
                    else:
                        # ROB状态改写
                        ROB.modify(entry, 3)
                        print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "准备进入确认阶段")
                        # 记录状态便于输出
                        result_print[ins['op']].append(Clock)
                        result_print[ins['op']].append(Clock)
                        # 看分支预测是否正确，不正确需要修改BTB并且flush掉ROB后面
                        if R1-R2 == 8:
                            Loop = False  # Loop循环结束
                            print("循环准备结束")
                            J = False  # 表明不用跳转
                        else:
                            J = True  # 表明用跳转
                            loop_index += 1
                        target, predict = BTB.find(ins_index)
                        if predict != J:  # BTB预测失败
                            if predict == 0 and J == True:
                                BTB.modify(ins_index, 0)  # 修改BTB
                                PC = 0
                            elif predict == 1 and J == False:
                                BTB.modify(ins_index, ins_index + 1)  # 修改BTB
                                # flush掉result_print中不需要的部分
                                for key in result_print:
                                    del result_print[key][(loop_index+1)*4:]
                                
                            # flush掉BNE后面取到的所有指令
                            temp_end = end
                            if end < entry:
                                temp_end = end + ROB_len
                            for i in range(entry+1, temp_end):  # 删除所有buffer中BNE后面指令的相关信息
                                mod_i = i % ROB_len
                                dest = "ROB" + str(mod_i)
                                LoadBuffer.clear(dest)
                                StoreBuffer.clear(dest)
                                RegResultStatus.clear(dest)
                                ResStation.clear(dest)
                            ROB.flush(entry)  # ROB中flushBNE后面取到的所有指令
                            break
            else:  # 说明数据没有准备好
                # 再检查数据是否准备好
                if ins['op'] == 'ADD.D':
                    prepare_ok = ResStation.is_data_prepare(this_dest)  # 检查数据是否已经准备好了
                    if prepare_ok:  # 如果此时数据准备好了
                        ROB.setDelay(entry, 2)  # 启动自计时器
                        print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "数据准备好了")

                elif ins['op'] == 'S.D':
                    prepare_ok = StoreBuffer.is_prepare_ok(this_dest)  # 检查数据是否已经准备好了
                    if prepare_ok:  # 如果此时数据准备好了
                        ROB.setDelay(entry, 2)  # 启动自计时器
                        print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "数据准备好了")

                elif ins['op'] == 'DADDUI':
                    rs = ins['rs']
                    rs_reg_is_busy, rs_reg_fu = RegResultStatus.is_busy(rs)
                    if not rs_reg_is_busy:
                        ROB.setDelay(entry, 2)  # 启动自计时器
                        print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "数据准备好了")

                elif ins['op'] == 'BNE':
                    rd = ins['rd']
                    rs = ins['rs']
                    rd_reg_is_busy, rd_reg_fu = RegResultStatus.is_busy(rd)
                    rs_reg_is_busy, rs_reg_fu = RegResultStatus.is_busy(rs)
                    if not rd_reg_is_busy and not rs_reg_is_busy:
                        ROB.setDelay(entry, 1)  # 启动自计时器
                        print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "数据准备好了")
                    else:
                        # 看ROB中对应位置是否已经写回结果
                        flag1 = not rd_reg_is_busy
                        flag2 = not rs_reg_is_busy
                        if rd_reg_is_busy:
                            aim_entry = int(rd_reg_fu[3:])
                            ins_state = ROB.getState(aim_entry)
                            if ins_state == 3:
                                flag1 = not flag1
                        if rs_reg_is_busy:
                            aim_entry = int(rd_reg_fu[3:])
                            ins_state = ROB.getState(aim_entry)
                            if ins_state == 3:
                                flag2 = not flag2
                        if flag1 and flag2:
                            # 启动自计时器
                            ROB.setDelay(entry, 1)
                            print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "数据准备好了")

        elif ins_state == 2:    # 准备进入写回阶段
            context = "M" + str(ins_index)
            # 改写ROB的Value部分
            ROB.modify(entry, 3, context)
            # 将这个 ROB 的 dest 广播到所有的 buffer
            StoreBuffer.broadcast(this_dest, value)
            ResStation.broadcast(this_dest, value)
            # 释放对应缓存
            if ins['op'] == 'L.D':
                LoadBuffer.modify(0, this_dest)
            if ins['op'] == 'ADD.D':
                ResStation.modify(0, this_dest)
            if ins['op'] == 'S.D':
                StoreBuffer.modify(0, this_dest)
            print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "进入写回阶段")
            # 记录状态便于输出
            result_print[ins['op']].append(Clock)

        elif ins_state == 3 and entry == head:  # 准备确认
            # 将 ROB 中的 value 写入寄存器或者内存
            value = ROB.getValue(entry)
            if ins['op'] != 'S.D' and ins['op'] != 'BNE':
                RegResultStatus.release(this_dest, value)
            if ins['op'] == 'DADDUI':
                R1 -= 8
            # 将它从 ROB 中删除
            ROB.modify(entry, 4)

            print("第" + str(ins_index) + "条指令 " + instruction_ls_string[ins_index] + "确认完成！")
            # 记录状态便于输出
            result_print[ins['op']].append(Clock)
            instruction_ls_string_all.append(instruction_ls_string[ins_index])

    # IF ID阶段：ROB添加指令，把指令放在对应Buffer中，查BTB表判断分支预测
    if Loop and PC < len(instruction_ls):
        ins = instruction_ls[PC]  # 根据PC获取当前指令
        # 判断ROB 以及对应Buffer是否满了
        ROB_is_full = ROB.isFull()
        if ROB_is_full == -1:
            continue
        entry = ROB_is_full
        dest = "ROB" + str(entry)
        is_issue = False
        if ins['op'] == 'L.D':
            is_full = LoadBuffer.find(dest)  # 看看LoadBuffer有没有位置多
            rd = ins['rd']
            reg_is_busy, reorder_id = RegResultStatus.is_busy(rd)  # 看看RegResultStatus的要被写入的位置是不是空
            if not is_full and not reg_is_busy:
                is_issue = True
                # 将待执行指令放入ROB
                ROB.insert(ins)
                context = str(ins['imm']) + "+" + ins['rs']
                # 将待执行指令放入order buffer
                LoadBuffer.modify(1, dest, context)
                # 占用RegResultStatus中的寄存器
                RegResultStatus.occupy(rd, dest)
                # 启动自计时器
                ROB.setDelay(entry, 2)
                print("第" + str(PC) + "条指令 " + instruction_ls_string[PC] + "进入发射")
                # 记录状态便于输出
                result_print[ins['op']].append(Clock)

        elif ins['op'] == 'ADD.D':
            res_station_type = "add"
            # 看看ReservationStation有没有位置多
            is_full = ResStation.find(dest, res_station_type)
            rd = ins['rd']
            rd_reg_is_busy, rd_reg_fu = RegResultStatus.is_busy(rd)
            if not is_full and not rd_reg_is_busy:
                is_issue = True
                # 将待执行指令放入ROB
                ROB.insert(ins)
                # 那就看看操作数是否ok,不管ok不ok,都要写入保留栈
                rs = ins['rs']
                rt = ins['rt']
                rs_reg_is_busy, rs_reg_fu = RegResultStatus.is_busy(rs)
                prepare_vj_ok = not rs_reg_is_busy
                rt_reg_is_busy, rt_reg_fu = RegResultStatus.is_busy(rt)
                prepare_vk_ok = not rt_reg_is_busy
                # 占用RegisterResultStatus中寄存器
                RegResultStatus.occupy(rd, dest)
                if prepare_vj_ok and prepare_vk_ok:  # 操作数如果都备齐了
                    # 启动自计时器
                    ROB.setDelay(entry, 2)
                    print("第" + str(PC) + "条指令 " + instruction_ls_string[PC] + "进入发射且数据准备好了")
                else:
                    if rs_reg_is_busy:
                        aim_entry = int(rs_reg_fu[3:])
                        ins_state = ROB.getState(aim_entry)
                        if ins_state == 3:
                            prepare_vj_ok = not prepare_vj_ok
                    if rt_reg_is_busy:
                        aim_entry = int(rt_reg_fu[3:])
                        ins_state = ROB.getState(aim_entry)
                        if ins_state == 3:
                            prepare_vk_ok = not prepare_vk_ok
                    if prepare_vj_ok and prepare_vk_ok:
                        # 启动自计时器
                        ROB.setDelay(entry, 2)
                        print("第" + str(PC) + "条指令 " + instruction_ls_string[PC] + "进入发射且数据准备好了")
                    else:
                        print("第" + str(PC) + "条指令 " + instruction_ls_string[PC] + "进入发射")
                # 修改 RS 保存站
                ResStation.modify(1, dest, ins['op'], prepare_vj_ok, prepare_vk_ok, rs_reg_fu, rt_reg_fu)
                # 记录状态便于输出
                result_print[ins['op']].append(Clock)
        elif ins['op'] == 'S.D':
            is_full = StoreBuffer.find(dest)  # 看看StoreBuffer有没有位置多
            rd = ins['rd']
            reg_is_busy, reg_fu = RegResultStatus.is_busy(rd)  # 看看RegResultStatus的要被写入的位置是不是空
            # print("S.D StoreBuffer is_full:" + str(is_full) + " reg_is_busy:" + str(reg_is_busy)+" reg_fu:"+reg_fu)
            # if reg_is_busy:
            #     busy, ins, state, des, val, delay = ROB.find(int(reg_fu[3:]))
            #     print("ins:" + ins['op'])
            if not is_full and not reg_is_busy:
                address = str(ins['imm']) + "+" + ins['rd']
                is_issue = True
                # 将待执行指令放入ROB
                ROB.insert(ins)
                rs = ins['rs']
                rs_reg_is_busy, rs_reg_fu = RegResultStatus.is_busy(rs)
                rs_prepare_ok = not rs_reg_is_busy
                if not rs_reg_is_busy:
                    # 启动自计时器
                    ROB.setDelay(entry, 2)
                    print("第" + str(PC) + "条指令 " + instruction_ls_string[PC] + "进入发射且数据已准备")
                else:
                    aim_entry = int(rs_reg_fu[3:])
                    ins_state = ROB.getState(aim_entry)
                    if ins_state == 3:
                        rs_prepare_ok = True
                        # 启动自计时器
                        ROB.setDelay(entry, 2)
                        print("第" + str(PC) + "条指令 " + instruction_ls_string[PC] + "进入发射且数据已准备")
                    else:
                        print("第" + str(PC) + "条指令 " + instruction_ls_string[PC] + "进入发射")
                # 更改 StoreBuffer
                StoreBuffer.modify(1, dest, rs_prepare_ok, address, rs_reg_fu)
                # 记录状态便于输出
                result_print[ins['op']].append(Clock)

        elif ins['op'] == 'DADDUI':
            rd = ins['rd']
            rd_reg_is_busy, rd_reg_fu = RegResultStatus.is_busy(rd)
            if not rd_reg_is_busy:
                is_issue = True
                # 将待执行指令放入ROB
                ROB.insert(ins)
                # 看操作数是否ok
                rs = ins['rs']
                rs_reg_is_busy, rs_reg_fu = RegResultStatus.is_busy(rs)
                # 占用RegResultStatus中的寄存器
                RegResultStatus.occupy(rd, dest)
                if not rs_reg_is_busy:  # 操作数如果都备齐了
                    # 启动自计时器
                    ROB.setDelay(entry, 1)
                    print("第" + str(PC) + "条指令 " + instruction_ls_string[PC] + "进入发射且数据准备好了")
                else:
                    print("第" + str(PC) + "条指令 " + instruction_ls_string[PC] + "进入发射")
                # 记录状态便于输出
                result_print[ins['op']].append(Clock)

        elif ins['op'] == 'BNE':
            is_issue = True
            # 将待执行指令放入ROB
            ROB.insert(ins)
            rd = ins['rd']
            rs = ins['rs']
            rd_reg_is_busy, rd_reg_fu = RegResultStatus.is_busy(rd)
            rs_reg_is_busy, rs_reg_fu = RegResultStatus.is_busy(rs)
            if not rd_reg_is_busy and not rs_reg_is_busy:
                # 启动自计时器
                ROB.setDelay(entry, 1)
                print("第" + str(PC) + "条指令 " + instruction_ls_string[PC] + "进入发射且数据准备好了")
            else:
                # 看ROB中对应位置是否已经写回结果
                flag1 = not rd_reg_is_busy
                flag2 = not rs_reg_is_busy
                if rd_reg_is_busy:
                    aim_entry = int(rd_reg_fu[3:])
                    ins_state = ROB.getState(aim_entry)
                    if ins_state == 3:
                        flag1 = not flag1
                if rs_reg_is_busy:
                    aim_entry = int(rd_reg_fu[3:])
                    ins_state = ROB.getState(aim_entry)
                    if ins_state == 3:
                        flag2 = not flag2
                if flag1 and flag2:
                    # 启动自计时器
                    ROB.setDelay(entry, 1)
                    print("第" + str(PC) + "条指令 " + instruction_ls_string[PC] + "进入发射且数据准备好了")
                else:
                    print("第" + str(PC) + "条指令 " + instruction_ls_string[PC] + "进入发射")
            # 记录状态便于输出
            result_print[ins['op']].append(Clock)

        if not is_issue:
            continue
        else:  # 进行分支预测
            target, predict = BTB.find(PC)  # target！=-1查到
            if target != -1:
                PC = target
            else:
                if ins['op'] == 'BNE':
                    BTB.insert(PC, 0)
                PC += 1

# 打印输出
# buffer print
print("\n")
LoadBuffer.print_load_buffer()
StoreBuffer.print_store_buffer()
RegResultStatus.print_reg_result_status()
ResStation.print_res_station()
ROB.print_all()
print("\n")
print("%20s %8s %8s %8s %8s" % ("Instruction", "Issue", "ExecComp", "WriteResult", "Commit"))

for i in range(int(R1_temp / 8)):
    for j, ls in enumerate(result_print):
        ls = result_print[ls]
        print("%20s %6d %6d %9d %12d" % (
        instruction_ls_string[j], ls[i * 4], ls[i * 4 + 1], ls[i * 4 + 2], ls[i * 4 + 3]))

print("\n注意：S.D的发射延迟主要是因为上一个循环中的DADDUI锁住了R1")
# print(result_print)
#

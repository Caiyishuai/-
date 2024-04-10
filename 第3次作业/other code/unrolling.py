mem = [0x0000] * 32
new = []


def run(memory):
    pc = 0
    plan = input()
    fld = []
    fadd_d = []
    fsd = []
    addi = []
    bne = []
    # result = 0
    if plan == '1':
        memory = [0x01000001,  # 0 fld f0 0(x1)
                  0x03040002,  # 1 fadd.d f4 f0 f2
                  0x02040001,  # 2 fsd f4 0(x1)
                  0x01060801,  # 3 fld f6 8(x1)
                  0x03080602,  # 4 fadd.d f8 f6 f2
                  0x02080801,  # 5 fsd f8 8(x1)
                  0x01001001,  # 6 fld f0 16(x1)
                  0x030c0002,  # 7 fadd.d f12 f0 f2
                  0x020c1001,  # 8 fsd f12 16(x1)
                  0x010e1801,  # 9 fld f14 24(x1)
                  0x03100e02,  # 10 fadd.d f16 f14 f2
                  0x02101801,  # 11 fsd f16 24(x1)
                  0x04010120,  # 12 addi x1 x1 32
                  0x05000102,  # 13 bne x1 x2 loop
                  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0
                  ]
        while memory[pc] != 0:
            instruction = memory[pc]
            op = instruction >> 24
            if op == 1:  # fld
                fld.append(instruction)
                pc = pc + 1
            elif op == 2:  # fsd
                fsd.append(instruction)
                pc = pc + 1
            elif op == 3:  # fadd.d
                fadd_d.append(instruction)
                pc = pc + 1
            elif op == 4:  # addi
                addi.append(instruction)
                pc = pc + 1
            elif op == 5:  # bne
                bne.append(instruction)
                pc = pc + 1
        pc = 0
        while True:
            ins = memory[pc]
            if pc == 0:
                new.append(ins)
            op = ins >> 24
            if op == 1:  # fld
                if (ins in new) and pc != 0:
                    pc = pc + 1
                    continue
                rd = ins >> 16
                rd = rd & 31
                next_ins = memory[pc+1]
                next_op = next_ins >> 24
                if next_op == 3:  # fadd.d
                    next_r1 = next_ins >> 8
                    next_r1 = next_r1 & 31
                    next_r2 = next_ins & 31
                    next_rd = next_ins >> 16
                    next_rd = next_rd & 31
                    if (rd == next_r1 or rd == next_r2) and fld.index(ins) % 2 == 0:
                        tianchong_ins = fld[fld.index(ins)+1]
                        tianchong_rd = tianchong_ins >> 16
                        tianchong_rd = tianchong_rd & 31
                        if tianchong_rd != next_rd:  # tianchong_rd != next_r1 and tianchong_rd != next_r2 and
                            new.append(tianchong_ins)
                            new.append(next_ins)
                            fld.remove(ins)
                            fld.remove(tianchong_ins)
                pc = pc + 1
                if len(new) == 14:
                    break
            elif op == 3:  # fadd.d
                if (ins in new) and pc != 1:
                    pc = pc + 1
                    continue
                next_ins = memory[pc+1]
                next_op = next_ins >> 24
                if next_op == 2:  # fsd
                    if (ins in new) and ((new[new.index(ins)-1] >> 24) == 1):
                        tianchong_add_ins = fadd_d[fadd_d.index(ins)+1]
                        new.append(tianchong_add_ins)
                        fadd_d.remove(ins)
                        fadd_d.remove(tianchong_add_ins)
                        while len(fld) != 0:
                            tianchong_fld_ins = fld[0]
                            new.append(tianchong_fld_ins)
                            fld.remove(tianchong_fld_ins)
                            if memory[memory.index(tianchong_fld_ins)+1] >> 24 == 3:
                                fld_rd = tianchong_fld_ins >> 16
                                fld_rd = fld_rd & 32
                                r1 = memory[memory.index(tianchong_fld_ins)+1] >> 24
                                r1 = r1 & 32
                                r2 = memory[memory.index(tianchong_fld_ins)+1] & 32
                                if fld_rd == r1 or fld_rd == r2:
                                    new.append(memory[memory.index(tianchong_fld_ins)+1])
                                    fadd_d.remove(memory[memory.index(tianchong_fld_ins)+1])
                                    if len(fld) != 0:
                                        tianchong_fld_ins = fld[0]
                                        new.insert(-1, tianchong_fld_ins)
                                        fld.remove(tianchong_fld_ins)
                    else:
                        new.append(ins)
                pc = pc + 1
                if len(new) == 14:
                    break
            elif op == 2:  # fsd
                if ins in new:
                    pc = pc + 1
                    continue
                pc = pc + 1
                if len(new) == 14:
                    break
            elif op == 4:  # addi
                if ins in new:
                    pc = pc + 1
                    continue
                while len(fsd) > 2:
                    tianchong_ins = fsd[0]
                    new.append(tianchong_ins)
                    fsd.remove(tianchong_ins)
                new.append(ins)
                addi.remove(ins)
                new.append(fsd[0])
                fsd.pop(0)
                pc = pc + 1
                if len(new) == 14:
                    break
            elif op == 5:  # bne
                if ins in new:
                    pc = pc + 1
                    continue
                new.append(ins)
                bne.remove(ins)
                new.append(fsd[0])
                fsd.pop()
                pc = pc + 1
                for inss in new:
                    # print(hex(inss))
                    if inss >> 24 == 1:  # fld
                        rd = (inss >> 16) & 31
                        bias = (inss >> 8) & 63
                        mem_address = inss & 31
                        print('fld', 'r' + str(rd), str(bias) + '(x' + str(mem_address) + ')')
                    elif inss >> 24 == 2:  # fsd
                        rd = (inss >> 16) & 31
                        bias = (inss >> 8) & 63
                        mem_address = inss & 31
                        print('fsd', 'r' + str(rd), str(bias) + '(x' + str(mem_address) + ')')
                    elif inss >> 24 == 3:  # fadd.d
                        rd = (inss >> 16) & 31
                        r1 = (inss >> 8) & 31
                        r2 = inss & 31
                        print('fadd.d', 'r' + str(rd), 'r' + str(r1), 'r' + str(r2))
                    elif inss >> 24 == 4:  # addi
                        mem_d = (inss >> 16) & 31
                        mem_1 = (inss >> 8) & 31
                        imm = inss & 63
                        print('addi', str(mem_d), str(mem_1), str(imm))
                    elif inss >> 24 == 5:  # bne
                        mem_2 = inss & 31
                        mem_1 = (inss >> 8) & 31
                        print('bne', 'x'+str(mem_1), 'x'+str(mem_2), 'LOOP')
                if len(new) == 14:
                    break


run(mem)

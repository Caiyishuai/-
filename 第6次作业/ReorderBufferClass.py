class ReorderBuffer:
    def __init__(self, n):  # init the ReorderBuffer

        '''
        :param n: the number of buffer
        self.head: point to the begin of robs
        self.end: point to the end of robs
        busy: 0--不忙  1--忙
        state：0--初始  1--issue  2--execute  3-- write commit  4--commit
        '''

        self.Robs = {}
        for index in range(n):
            self.Robs[index] = {'busy': False, 'instruction': None, 'state': 0,
                                'Destination': None, 'value': None, 'delay': 0}
        self.head = 0
        self.end = 0
        self.n = n

    def isFull(self):
        '''
        利用头尾指针位置(self.end+1)%self.n == self.head判断是否满,
        且利用了循环列表牺牲了一个buffer的空间。所以实际空间大小为n-1
        '''
        if (self.end+1) % self.n == self.head:
        # if (self.end + self.n-self.head) % self.n == self.n:
            return -1
        else:
            return self.end

    def isEmpty(self):  # self.end == self.head判断是否为空
        if self.end == self.head:
            return True
        else:
            return False

    def insert(self, instruction):  # 插入指令，返回对应的entry
        '''
        :param instruction:  指令格式{'op': 'L.D', 'rd': 'F0', 'rs': 'R1', 'imm': 0, 'op_type': 1, 'index': 0}
        :param entry
        :return: entry
        '''
        self.Robs[self.end]['busy'] = True
        self.Robs[self.end]['instruction'] = instruction
        self.Robs[self.end]['state'] = 1
        self.Robs[self.end]['delay'] = -1
        self.Robs[self.end]['Destination'] = instruction['rd']
        self.end = (self.end+1) % self.n

    def find(self, entry):  # 通过entry找到对应一整条信息, 并返回
        '''
        :param entry:  入口
        :return:  返还 一整条信息  return busy, ins, state, des, val, delay
        '''
        aim_entry = self.Robs[entry]
        busy = aim_entry['busy']
        ins = aim_entry['instruction']
        state = aim_entry['state']
        des = aim_entry['Destination']
        val = aim_entry['value']
        delay = aim_entry['delay']
        return busy, ins, state, des, val, delay

    def modify(self, entry, state, value = None):   # 修改rob对应参数
        aim_entry = self.Robs[entry]
        aim_entry['state'] = state
        if state == 4:   # 如果状态为commit
            aim_entry['busy'] = False
            self.head = (self.head+1) % self.n
        if value:
            aim_entry['value'] = value

    def setDelay(self, entry, delay):  # 对clock的delay进行设置
        '''
        :param delay: 延迟
        '''
        self.Robs[entry]['delay'] = delay

    def getDelay(self, entry):   # 获得clock的delay
        '''
        :param entry: 入口
        :return: 返回delay的值
        '''
        return self.Robs[entry]['delay']

    def getHeadEnd(self):    # 获得头尾指针
        # print('head:{},end:{}'.format(self.head, self.end))
        return self.head, self.end

    def flush(self, entry):     # 当分支预测失败的时候，把entry指向的后续指令给删掉
        temp_end = self.end
        if self.end < entry:
            temp_end = self.end + self.n
        for index in range(entry+1, temp_end):
            index = index % self.n
            self.Robs[index]['busy'] = False
            self.Robs[index]['instruction'] = None
            self.Robs[index]['state'] = 0
            self.Robs[index]['Destination'] = None
            self.Robs[index]['value'] = None
            self.Robs[index]['delay'] = 0

        self.end = (entry+1) % self.n

    def getValue(self, entry):  # 获得指令运算结果
        return self.Robs[entry]['value']

    def getState(self, entry):  # 获得指令当前状态
        return self.Robs[entry]['state']

    def print_all(self):        # 全部数据打印
        print("-----------------------------ROB-------------------------------")
        print("HeadPoint:", self.head, "\tEndPoint:", self.end)
        print("entry\tbusy\tinstruction\t\t\tstate\t\tDestination\t\tvalue\t")
        state_ls = ['None', 'Issue', 'ExecComp', 'WriteResult', 'Commit']
        for key, value in self.Robs.items():
            busy = str(value['busy'])
            op = "None"
            if not value['instruction'] is None:
                op = value['instruction']['op']
            state = state_ls[value['state']]
            dest = "None"
            if not value['Destination'] is None:
                dest = value['Destination']
            val = "None"
            if not value['value'] is None:
                val = value['value']
            print("%3s %8s %10s %17s %12s %14s " % (str(key), busy, op, state,
                                                    dest, val))
    def print_valid(self):      # 有效数据打印
        print("-----------------------------ROB-------------------------------")
        print("entry\tbusy\tinstruction\t\t\tstate\t\tDestination\t\tvalue\t")
        temp_head = self.head
        temp_end = self.end
        state_ls = ['Issue', 'ExecComp', 'WriteResult', 'Commit']
        if temp_end < temp_head:
            temp_end = temp_end + self.n
        for entry in range(temp_head, temp_end):
            entry = entry % self.n
            busy, ins, state, des, val, delay = self.find(entry)
            print("%4s %7s %11s %18s %10s %14s " % (str(entry), str(busy), ins['op'], state_ls[state-1], des, val))
            # print("{0}\t\t{1}\t\t{2}\t\t{3}\t\t{4}\t\t{5}\t\t".format(entry, busy, ins['op'], state_ls[state-1], des, val))

# =============================================================================
# #初始化
# Rob = ReorderBuffer(3)
#
# #检测是否为空
# empty_flag = Rob.isEmpty()
# print('empty_flag:{}'.format(empty_flag))
#
# #插入第一条
# Rob.insert({'op': 'L.D', 'rd': 'F0', 'rs': 'R1', 'imm': 0, 'op_type': 1, 'index': 0})
# Rob.getHeadEnd()
# print(Rob.Robs)
#
# #插入第二条
# Rob.insert({'op': 'ADD.D', 'op_type': 2, 'rd': 'F4', 'rs': 'F0', 'rt': 'F2', 'index': 1})
# Rob.getHeadEnd()
# print(Rob.Robs)
#
# #插入第四条
# Rob.insert({'op': 'S.D', 'rd': 'R1', 'rs': 'F4', 'imm': 0, 'op_type': 3, 'index': 2})
# Rob.getHeadEnd()
# print(Rob.Robs)
#
# #判断是否为满
# end_index = Rob.isFull()
# Rob.getHeadEnd()
#
# #修改对应的一条
# Rob.modify(1, 3, '#4 + #1')
# busy, ins, state, des, val, delay = Rob.find(1)
# print( busy, ins, state, des, val, delay )
#
# #修改到状态为4
# Rob.modify(0, 4)
# Rob.getHeadEnd()
# print(Rob.Robs)
#
# Rob.print_all()
# Rob.print_valid()
# =============================================================================





class store_buffer_item:
    def __init__(self):
        self.busy = False
        self.Vj = ""
        self.Qj = ""
        self.address = ""
        self.Dest = ""


class store_buffer:
    def __init__(self,n):
        self.obj=[]
        self.n = n
        self.destmap={} # 已知 ROB 索引找到 storebuffer 索引
        for i in range(n):
            self.obj.append(store_buffer_item())
    def find(self,dest):
        '''
        找出store buffers中从上至下第一个空闲着的store buffer的下标和store buffers的状态
        :return:
            index_str：字符串型，store buffers中从上至下第一个空闲着的store buffer的下标，若字符串为空，则表示store buffers已满
            is_full：布尔型，表示store buffers的状态，若buffers已满，则为True;反之为False
        '''
        is_full = True
        for i in range(self.n):
            if not self.obj[i].busy:
                index_str = 'store'+str(i)
                is_full = False
                self.destmap[dest]=index_str
                break
        return is_full

    def modify(self, mod, dest, prepare_ok=0, address="", context=""):
        '''
        修改store buffer
        :param mod: 模式，int型。==1：占用store buffer； ==0：释放store buffer
        :param store_buffer_index: 进行修改的store buffer的在all buffers中的下标，字符串型。字符串为空时，表示无空闲store buffer
        :param context: 字符串型，进行修改的store buffer的内容
        :return:
        '''
        if dest in self.destmap:
            store_buffer_index = self.destmap[dest]
            if mod == 1:  # 占用store buffer
                self.obj[int(store_buffer_index[5:])].busy = True
                self.obj[int(store_buffer_index[5:])].address = address  #
                if prepare_ok == 1:
                    self.obj[int(store_buffer_index[5:])].Vj = context
                else:
                    self.obj[int(store_buffer_index[5:])].Qj = context
                self.obj[int(store_buffer_index[5:])].Dest = dest
            elif mod == 0:  # mod == 0，释放store buffer
                self.obj[int(store_buffer_index[5:])].busy = False
                self.obj[int(store_buffer_index[5:])].address = ''  # 此时context为空字符串'',直接赋为''也可
                self.obj[int(store_buffer_index[5:])].Vj = ''
                self.obj[int(store_buffer_index[5:])].Qj = ''
                self.obj[int(store_buffer_index[5:])].Dest = ''
                self.destmap.pop(dest)
        else:
            print("Can't find " + dest + "in ROB, error!")


    def broadcast(self, rob_index, context):
        '''
        遍历所有busy是True的buffers，找到Qj==rob_index对应的buffer下标,并将Vj改为context
        :param res_station_index: 保留站下标，字符串型，Qj
        :param context: 值，字符串型，Vj
        :return: null
        '''
        for i in range(self.n):
            if self.obj[i].busy is True:
                if self.obj[i].Qj == rob_index:
                    self.obj[i].Vj = context
                    self.obj[i].Qj = ''

    def is_prepare_ok(self, dest):
        '''
        判断store buffers中下标为store_buffer_index的buffer是否准备好，即是否可以直接从Vj中取出数据
        :param store_buffer_index:
        :return:
        '''
        if dest in self.destmap:
            store_buffer_index = self.destmap[dest]
            if self.obj[int(store_buffer_index[5:])].Qj == '':
                return True
            else:
                return False
        else:
            print("Can't find " + dest + " in ROB, error!")
            return False

    # 打印store buffer数据
    def print_store_buffer(self):
        print("------------Store Buffer------------")
        print("index\tbusy\taddress\tVj\tQj\tDest")
        for i in range(len(self.obj)):
            print("store{0}\t{1}\t{2}\t{3}\t{4}\t{5}".format(i, self.obj[i].busy, self.obj[i].address,
                                                        self.obj[i].Vj, self.obj[i].Qj,self.obj[i].Dest))
            
    def clear(self,dest):
        if dest in self.destmap:
            store_buffer_index = self.destmap[dest]
            self.obj[int(store_buffer_index[5:])].busy = False
            self.obj[int(store_buffer_index[5:])].address = ''  # 此时context为空字符串'',直接赋为''也可
            self.obj[int(store_buffer_index[5:])].Vj = ''
            self.obj[int(store_buffer_index[5:])].Qj = ''
            self.obj[int(store_buffer_index[5:])].Dest = ''
            self.destmap.pop(dest)


# =============================================================================
# sb = store_buffer(5)
# sb.print_store_buffer()
# is_full = sb.find('ROB1')
# context = "ROB2"
# 
# sb.modify(1, "ROB1" , 0,"",context)
# sb.print_store_buffer()
# 
# sb.clear( "ROB1")
# sb.print_store_buffer()
# 
# sb.broadcast("ROB2",context=context)
# sb.print_store_buffer()
# 
# print("is_prepare_ok: ",sb.is_prepare_ok('ROB1'))
# sb.print_store_buffer()
# 
# sb.modify(0, "ROB1")
# sb.print_store_buffer()
# 
# =============================================================================

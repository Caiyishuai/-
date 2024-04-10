class store_buffer_item:
    def __init__(self):
        self.busy = False
        self.Vj = ""
        self.Qj = ""
        self.address = ""


class store_buffer:
    def __init__(self):
        self.obj=[]
        for i in range(3):
            self.obj.append(store_buffer_item())
    def find(self):
        '''
        找出store buffers中从上至下第一个空闲着的store buffer的下标和store buffers的状态
        :return:
            index_str：字符串型，store buffers中从上至下第一个空闲着的store buffer的下标，若字符串为空，则表示store buffers已满
            is_full：布尔型，表示store buffers的状态，若buffers已满，则为True;反之为False
        '''
        for i in range(3):
            if not self.obj[i].busy:
                index_str = 'store'+str(i)
                is_full = False
                break
            else:
                index_str = ''
                is_full = True
        return is_full, index_str

    def modify(self, mod, store_buffer_index, prepare_ok=0, address="", context=""):
        '''
        修改store buffer
        :param mod: 模式，int型。==1：占用store buffer； ==0：释放store buffer
        :param store_buffer_index: 进行修改的store buffer的在all buffers中的下标，字符串型。字符串为空时，表示无空闲store buffer
        :param context: 字符串型，进行修改的store buffer的内容
        :return:
        '''
        if mod == 1:  # 占用store buffer
            self.obj[int(store_buffer_index[5:])].busy = True
            self.obj[int(store_buffer_index[5:])].address = address  #
            if prepare_ok == 1:
                self.obj[int(store_buffer_index[5:])].Vj = context
            else:
                self.obj[int(store_buffer_index[5:])].Qj = context
        elif mod == 0:  # mod == 0，释放store buffer
            self.obj[int(store_buffer_index[5:])].busy = False
            self.obj[int(store_buffer_index[5:])].address = ''  # 此时context为空字符串'',直接赋为''也可
            self.obj[int(store_buffer_index[5:])].Vj = ''
            self.obj[int(store_buffer_index[5:])].Qj = ''

    def broadcast(self, res_station_index, context):
        '''
        遍历所有busy是True的buffers，找到Qj==res_station_index对应的buffer下标,并将Vj改为context
        :param res_station_index: 保留站下标，字符串型，Qj
        :param context: 值，字符串型，Vj
        :return: null
        '''
        for i in range(3):
            if self.obj[i].busy is True:
                if self.obj[i].Qj == res_station_index:
                    self.obj[i].Vj = context
                    self.obj[i].Qj = ''

    def is_prepare_ok(self, store_buffer_index):
        '''
        判断store buffers中下标为store_buffer_index的buffer是否准备好，即是否可以直接从Vj中取出数据
        :param store_buffer_index:
        :return:
        '''
        if self.obj[int(store_buffer_index[5:])].Qj == '':
            return True
        else:
            return False

    # 打印store buffer数据
    def print_store_buffer(self):
        print("------------Store Buffer------------")
        print("index\tbusy\taddress\tVj\tQj")
        for i in range(len(self.obj)):
            print("store{0}\t{1}\t{2}\t{3}\t{4}".format(i, self.obj[i].busy, self.obj[i].address,
                                                        self.obj[i].Vj, self.obj[i].Qj))


#sb = store_buffer()
#is_full, store_buffer_index = sb.find()
#context = "0+R1"
#sb.modify(mod=1, prepare_ok = 1,store_buffer_index=store_buffer_index, address=" ",context=context)
#
#is_full, store_buffer_index = sb.find()

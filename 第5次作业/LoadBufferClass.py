class load_buffer_item:
    def __init__(self):
        self.busy = False
        self.address = ""


class load_buffer:
    def __init__(self):
        self.obj = []
        for i in range(3):
            self.obj.append(load_buffer_item())

    def find(self):
        '''
        找出load buffers中从上至下第一个空闲着的load buffer的下标和load buffers的状态
        :return:
            index_str：字符串型，load buffers中从上至下第一个空闲着的load buffer的下标，若字符串为空，则表示load buffers已满
            is_full：布尔型，表示load buffers的状态，若buffers已满，则为True;反之为False
        '''
        index_str = 'load'
        for i in range(3):
            if not self.obj[i].busy:
                #index_str = 'load'+str(i)
                index_str += str(i)
                is_full = False
                break
            else:
                index_str = ''
                is_full = True
        return is_full, index_str

    def modify(self, mod, load_buffer_index, context=""):
        '''
        修改load buffer
        :param mod: 模式，int型。==1：占用load buffer； ==0：释放load buffer
        :param load_buffer_index: 进行修改的load buffer的在all buffers中的下标，字符串型。字符串为空时，表示无空闲load buffer
        :param context: 字符串型，进行修改的load buffer的address
        :return:
        '''
        if mod == 1:  # 占用load buffer
            self.obj[int(load_buffer_index[4:])].busy = True
            self.obj[int(load_buffer_index[4:])].address = context  # 格式如'34+R1'
        else:  # mod == 0，释放load buffer
            self.obj[int(load_buffer_index[4:])].busy = False
            self.obj[int(load_buffer_index[4:])].address = context  # 此时context为空字符串'',直接赋为''也可

    # 打印load buffer数据
    def print_load_buffer(self):
        print("------------Load Buffer------------")
        print("%6s %6s %6s" % ("Index","Busy","Address"))
        for i in range(len(self.obj)):
            print("%6s %6s %6s" % ("load"+str(i), self.obj[i].busy, self.obj[i].address))
#            print("load{0}\t{1}\t{2}".format(i, self.obj[i].busy, self.obj[i].address))

#lb = load_buffer()
## 初始化输出测试
##for i in range(3):
##    print(lb.obj[i].busy, lb.obj[i].address)
#
#is_full, load_buffer_index = lb.find()
#context = "0+R1"
#lb.modify(mod=1, load_buffer_index=load_buffer_index, context=context)
#
#is_full, load_buffer_index = lb.find()
class res_station:
    def __init__(self,add_num,mult_num):  
        self.obj={}
#        self.add_num=5  # 加法器个数
#        self.mult_num=2  # 乘法器个数
#        self.num=self.add_num+self.mult_num
        self.num=add_num+mult_num
        self.destmap={} # 已知 ROB 索引找到 res 索引
        for i in range(add_num): # 创建add_num个add buffer
            name='add'+str(i)
            self.obj[name] = {'busy': 0,'op':'','Vj':'','Vk':'','Qj':'','Qk':'','Dest':''}
        for i in range(mult_num): # 创建mult_num个mult buffer
            name='mult'+str(i)
            self.obj[name] = {'busy': 0,'op':'','Vj':'','Vk':'','Qj':'','Qk':'','Dest':''}

# =============================================================================
# 查找是否有空的运算部件
# 根据指令所需的计算部件，找出中从上至下第一个空闲着的相应功能部件的状态和部件名称
# =============================================================================
    def find(self,dest,res_station_type):
        '''
        :param
            res_station_type:string型,表示需要的运算部件，如"add"、"mult"
        :return:
            is_full: bool型。表示功能部件状态，若均已使用已满，则为True;反之为False
            index_str: string型。从上至下第一个空闲部件名，若字符串为空，则表示均已被占用
        '''
        for temp in self.obj:
            # 查找对应功能部件并判断是否被占用
            if res_station_type[0:3]==temp[0:3] and self.obj[temp]['busy']==0:
                index_str = temp
                is_full = False
                self.destmap[dest] = index_str
                break
            else:  # 如果无空闲
                index_str = ''
                is_full = True
        
        return is_full
    
# =============================================================================
# 修改保留站内容
# =============================================================================
    def modify(self, mod, dest ,op="",\
               prepare_vj_ok=False,prepare_vk_ok=False,j_context="",k_context=""):
        '''
        :param
            mod: int型。==1:将占用 buffer; ==0:将释放 buffer
            reg_buffer_index: string型。将要修改的功能部件名称
            op: string型。填入的指令名
            prepare_vj_ok: int型。==1:写入Vj;==0:写入Qj
            prepare_vk_ok: int型。==1:写入Vk;==0:写入Qk
            j_context: string型。写入j的内容
            k_context: string型。写入k的内容
        '''
        reg_buffer_index = self.destmap[dest]
        if mod == 1:  # 占用 buffer
            self.obj[reg_buffer_index]["busy"] = 1
            self.obj[reg_buffer_index]["op"] = op  # 修改op
            self.obj[reg_buffer_index]["Dest"] = dest
            if prepare_vj_ok == 1:  # 写Vj
                self.obj[reg_buffer_index]["Vj"] = j_context
            else:                   # 写Qj
                self.obj[reg_buffer_index]["Qj"] = j_context
            if prepare_vk_ok == 1:  # 写Vk
                self.obj[reg_buffer_index]["Vk"] = k_context
            else:                   # 写Qk
                self.obj[reg_buffer_index]["Qk"] = k_context
            
        elif mod == 0:  # 释放 buffer
            self.obj[reg_buffer_index]["busy"] = 0
            self.obj[reg_buffer_index]["op"] = ''  # 此时context为空字符串'',直接赋为''也可
            self.obj[reg_buffer_index]["Vj"] = ''
            self.obj[reg_buffer_index]["Vk"] = ''
            self.obj[reg_buffer_index]["Qj"] = ''
            self.obj[reg_buffer_index]["Qk"] = ''
            self.obj[reg_buffer_index]["Dest"] = ''
            self.destmap.pop(dest)
#        print(reg_buffer_index)
#        print("busy: "+str(self.obj[reg_buffer_index]["busy"]))
#        print("op: "+self.obj[reg_buffer_index]["op"])
#        print("Vj: "+self.obj[reg_buffer_index]["Vj"])
#        print("Vk: "+self.obj[reg_buffer_index]["Vk"])
#        print("Qj: "+self.obj[reg_buffer_index]["Qj"])
#        print("Qk: "+self.obj[reg_buffer_index]["Qk"])
        
# =============================================================================
# 广播
# 若被占用的功能部件已经可以获得数据，则替换内容
# 遍历所有功能部件，若Q中有对应标记的功能部件可获得数据
# 则清空Q,在V中填入数据
# =============================================================================
    def broadcast(self, rob_index, context):
        '''
        :param
            rob_index: string型。获得数据的ROB索引
            context: string型。获得的数据内容
        '''
        for temp in self.obj:
            if not self.obj[temp]["busy"]:
                continue
            if self.obj[temp]["Qj"] == rob_index:
                self.obj[temp]["Qj"] = ''
                self.obj[temp]["Vj"] = context
#                print(temp)
#                print("busy: "+str(self.obj[temp]["busy"]))
#                print("op: "+self.obj[temp]["op"])
#                print("Vj: "+self.obj[temp]["Vj"])
#                print("Vk: "+self.obj[temp]["Vk"])
#                print("Qj: "+self.obj[temp]["Qj"])
#                print("Qk: "+self.obj[temp]["Qk"])
            if self.obj[temp]["Qk"] == rob_index:
                self.obj[temp]["Qk"] = ''
                self.obj[temp]["Vk"] = context
#            print(temp)
#            print("busy: "+str(self.obj[temp]["busy"]))
#            print("op: "+self.obj[temp]["op"])
#            print("Vj: "+self.obj[temp]["Vj"])
#            print("Vk: "+self.obj[temp]["Vk"])
#            print("Qj: "+self.obj[temp]["Qj"])
#            print("Qk: "+self.obj[temp]["Qk"])

# =============================================================================
# 判断数据是否准备完毕
# =============================================================================
    def is_data_prepare(self, dest):
        '''
        :param 
            res_station_index: string型。需要检查数据完成度的功能部件名
        :return
            bool型。若两个数据均准备完毕，则返回True,反之返回False
        '''
        res_station_index = self.destmap[dest]
        if self.obj[res_station_index]['Vj']!='' and self.obj[res_station_index]['Vk']!='':
            return True
        return False

# =============================================================================
# 打印数据
# =============================================================================
    def print_res_station(self):
        print("------------Res Station------------")
        print("name\tbusy\top\tVj\tVk\tQj\tQk\tDest")
        for key, value in self.obj.items():
            print("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(key, value['busy'], value['op'], value['Vj'],
                                                             value['Vk'], value['Qj'], value['Qk'],value['Dest']))

# =============================================================================
# 回退清空索引为 dest 的在保留站中的数据
# =============================================================================
    def clear(self, dest):
        if dest in self.destmap:
            reg_buffer_index = self.destmap[dest]
            self.obj[reg_buffer_index]["busy"] = 0
            self.obj[reg_buffer_index]["op"] = ''  # 此时context为空字符串'',直接赋为''也可
            self.obj[reg_buffer_index]["Vj"] = ''
            self.obj[reg_buffer_index]["Vk"] = ''
            self.obj[reg_buffer_index]["Qj"] = ''
            self.obj[reg_buffer_index]["Qk"] = ''
            self.obj[reg_buffer_index]["Dest"] = ''
            self.destmap.pop(dest)   
            
            
            
# =============================================================================
# # 创建类
# sb = res_station(5,3)
# # 查找空mult
# is_full = sb.find("add","ROB1")
# # 修改
# sb.modify(1,"ROB1",'SUB',0,0,'ROB4','ROB2')
# sb.print_res_station()
# # 广播
# sb.broadcast('ROB2','M(A0)')
# 
# # 数据是否准备完毕
# is_pre=sb.is_data_prepare("ROB1")
# print("两个数据是否准备好: "+str(is_pre))
# sb.print_res_station()
# # 广播，再次判断数据是否准备完毕
# sb.broadcast('ROB4','M(A1)')
# is_pre=sb.is_data_prepare("ROB1")
# print("两个数据是否准备好: "+str(is_pre))
# sb.print_res_station()
# =============================================================================

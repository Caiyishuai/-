# =============================================================================
# 仅实现内存读入和读出，不涉及数据格式转换
# Memory:32bit address,8 bit cell
# =============================================================================
class Memory:
    memory = {}
    # 初始化
    def __init__(self,word_len,mem_len):
        self.word_len=word_len
        self.mem_len=mem_len
        
        # 初始化前四个地址,每个地址占四行
        for i in range(4*4):
            str_bin = bin(i).replace('0b','')
            add = (word_len - len(str_bin))*'0'+str_bin
            self.memory[add] = [] # 二进制bool类型
            for j in range(self.mem_len):
                self.memory[add].append(bool(0))    

    # 将外部数据写入内存中
    # 传入4个内存块下标和二进制补码
    def write(self,add_list,binary_list):
        for k,i in enumerate(add_list):
            for j in range(self.mem_len):
                self.memory[i][j] = binary_list[k*self.mem_len+j]
        
    # 将内存中的数据读出
    def read(self,add_list):
        binary_list = []
        for k,i in enumerate(add_list):
            for j in range(self.mem_len):
                binary_list.append(self.memory[i][j])
        return binary_list
            

# =============================================================================
# 仅实现内存读入和读出，不涉及数据格式转换
# Memory:32bit address,8 bit cell
# =============================================================================
class Memory:
    memory = {} #key为各个内存单元的32位地址，value为存储在各个内存单元上的8位数据
    # 初始化
    def __init__(self,word_len,mem_len):
        self.word_len=word_len
        self.mem_len=mem_len

        # #0中存指令Jr #10，在内存#10开始初始化指令和程序，存到#17，故要初始化18个内存地址，18*4个内存单元
        # 初始化18个地址,每个地址占四行，即获取18*4个内存单元的32位地址
        for i in range(18*4):
# =============================================================================
#            str_bin = bin(i).replace('0b','')
#            add = (word_len - len(str_bin))*'0'+str_bin
# =============================================================================
            add = bin(i).replace('0b','').zfill(32)   # 内存单元地址
            self.memory[add] = []                     # 初始化各内存单元上值是空的，只有键值
            for j in range(self.mem_len):             # 将各内存单元的各位存入0
                self.memory[add].append(0)
                
    # 将外部数据写入内存中
    # 传入4个内存块物理地址组成的列表add_list和二进制补码列表
    def write(self,add_list,binary_list):
        for k,i in enumerate(add_list):               # k是地址列表中遍历到的地址的下标，i是对应的地址add_list[k]
            for j in range(self.mem_len):             # j是内存块对应的下标  
                self.memory[i][j] = binary_list[k*self.mem_len+j] # self.memory[i][j]，i是键值——地址，self.memory[i]是内存块，self.memory[i][j]是内存块的各个元素
        
    # 将内存中的数据读出
    def read(self,add_list):
        binary_list = []
        for k,i in enumerate(add_list):
            for j in range(self.mem_len):
                binary_list.append(self.memory[i][j])
        return binary_list
            

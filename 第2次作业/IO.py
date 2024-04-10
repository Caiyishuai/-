# =============================================================================
# 负责外存→内存和内存→外存
# 传入的是形式地址
# 转换为物理地址后再传入memory
# =============================================================================
class IO:
    def __init__(self, word_len,Mem,Fun):
        self.word_len=word_len
        self.Mem=Mem
        self.Fun=Fun
    
    # 传入形式地址和数字
    # 由外存写入内存
    def write(self,mem_id,num):
        memadd_list=self.Fun.MemId_toBlock(mem_id)
        bin_num=self.Fun.To_binary(num)
        self.Mem.write(memadd_list,bin_num)
        print("已在内存地址 "+ mem_id + " 中写入数据："+ str(num)+"\n")
    
    # 从内存读到外存
    def read(self,mem_id):
        memadd_list=self.Fun.MemId_toBlock(mem_id)
        temp=self.Mem.read(memadd_list)
        print("已从内存地址 "+ mem_id + " 中读出数据："+ str(self.Fun.To_decimal(temp))+"\n")
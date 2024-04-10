# -*- coding: utf-8 -*-

from IO import IO
from CPU import CPU
from Function import Func
from Memory import Memory

if __name__ == "__main__":
    word_len = 32 # 字长
    mem_len = 8 # 内存一个单元的大小
    reg_num = 16 # 寄存器个数
    
    Fun=Func(word_len,mem_len)
    # Memory
    Mem=Memory(word_len,mem_len)  # 内存实例
    
    # CPU,含32个寄存器、加法器和控制器
    Cpu=CPU(word_len,mem_len,reg_num,Mem,Fun)  # CPU实例
    Cpu.reg=Cpu.Register(Cpu)  # CPU中寄存器实例
    Cpu.Adder=Cpu.Adder(Cpu)  # CPU中加法器实例
    Cpu.controller=Cpu.controller(Cpu,Cpu.reg,Cpu.Adder)  # CPU中控制器实例
    
    # I/O
    Io=IO(word_len,Mem,Fun)  # I/O实例
# =============================================================================
#     内存中 #0 表示形式地址，含四个cell，一个cell=8bit
# =============================================================================
    Io.write("#0",2147483640)   # 写入内存
    Io.read("#0")               # 从内存读出
    Io.write("#1",-2147483648)
    Io.read("#1") 
    Io.write("#3",9999999)
# =============================================================================
#     Program项目实现
# =============================================================================
    Cpu.controller.load("r1","#0")         # Load  r1, #0
    Cpu.controller.load("r2","#1")         # Load  r2, #1
    Cpu.controller.add("r3","r1","r2")     # Add   r3, r1, r2 
    Cpu.controller.store("r3","#3")        # Store r3, #3
    Io.read("#3")                          # 读取#3中数据
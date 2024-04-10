import argparse
import re

def compile(file):
    # 读取文件，删除空行
    with open(args.file, 'r') as fr:
        context = fr.read().splitlines()
        context = list(filter(None, context))

    dis = 0
    for i in range(len(context)):
        if ':' in context[i]:
            context[i] = re.split(r'[ ]*:[ ]*', context[i])
        else:
            context[i] = ['', context[i]]


    # print(context)

    context_split = []
    for i in context:
        context_split.append([i[0]] + re.split(r'[ ]*[\t ,:][ ]*', i[1]))
    # print(context_split)
    return context_split


def unrolled(loop, num = 1):
    result = loop[:3]
    for i in range(1, num):
        result.append([''] + [loop[0][1]] + ['f'+str(2+i*4)] + [str(i*8) + loop[0][-1][1:]])
        result.append(loop[1][:2] + ['f'+str(4+i*4)] + ['f'+str(2+i*4)] + loop[1][-1:])
        result.append(loop[2][:2] + ['f'+str(4+i*4)] + [str(i*8) + loop[2][-1][1:]])
    result.append(loop[-2][:-1] + [str(num*8)])
    result.append(loop[-1])
    return result

def scheduled(loop):
    result = []
    for i in loop:
        if i[1] == 'fld':
            result.append(i)
    for i in loop:
        if i[1] == 'fadd.d':
            result.append(i)
    for i in loop:
        if i[1] == 'fsd':
            result.append(i)
    result = result[:-2] + [loop[-2]] + result[-2:-1] + [loop[-1]] + [result[-1]]

    a = int(result[-4][-1])
    for i in range(-3, 0, 1):
        if result[i][1] == 'fsd':
            result[i][-1] = str(int(result[i][-1][:-4])-a) + result[i][-1][-4:]
    return result

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('--file', type=str)
args = parser.parse_args()

if __name__ == '__main__':
    # print(args)
    loop = compile(args)
    result = unrolled(loop, 4)
    a = scheduled(result)
    for i in a:
        if i[0] != '':
            print(i[0] + ':' + i[1] + ' ' + ','.join(i[2:]))
        else:
            print(i[1] + ' ' + ','.join(i[2:]))
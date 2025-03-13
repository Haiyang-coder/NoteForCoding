import numpy as np
import matplotlib.pyplot as plt
import math
import numpy as np
from readQr import *    # 读取二维码
from DNA import *   # DNA编码解码

# chen混沌系统


def Chen(x0, y0, z0, a, b, c, T):
    h = 0.001
    x = []
    y = []
    z = []
    for t in range(T):
        xt = x0+h*(a*(y0-x0))
        yt = y0+h*((c-a)*x0-x0*z0+c*y0)
        zt = z0+h*(x0*y0-b*z0)

        # x0、y0、z0统一更新
        x0, y0, z0 = xt, yt, zt
        x.append(x0)
        y.append(y0)
        z.append(z0)

    return x, y, z


# 参数设置
a = 35.0  # 系统参数a
b = 3.0   # 系统参数b
c = 28.0  # 系统参数c
x0, y0, z0 = 1.03201, 1.0, 1.0  # 初始条件
num_steps = 600 * 600 * 6  # 生成的步数
dt = 0.01  # 时间步长

# 生成Chen混沌序列
x_vals, y_vals, z_vals = Chen(x0, y0, z0, a, b, c, num_steps)


# 把一维矩阵编程m×n的二维矩阵
def list_to_matrix(lst, m, n):
    return [lst[i*n: (i+1)*n] for i in range(m)]


# 把一个大矩阵按照4×4分块
def split_4x4_blocks(matrix):
    n = len(matrix)
    m = len(matrix[0])  # 防止空矩阵的情况
    if n <= 0 or m <= 0:
        raise ValueError("矩阵行列数必须大于0")
    if n % 4 != 0:
        raise ValueError("矩阵行数必须是4的倍数")
    if m % 4 != 0:
        raise ValueError("矩阵列数必须是4的倍数")

    blocks = []
    # 按4×4步长遍历行列
    for i in range(0, n, 4):
        for j in range(0, m, 4):
            # 提取子矩阵块
            block = [row[j:j+4] for row in matrix[i:i+4]]
            blocks.append(block)
    return blocks


def combine_matrices(matrices, k, l):
    # 假设输入的矩阵为一个列表，包含k*l个m*n矩阵
    # 获取每个矩阵的形状 (m, n)
    temp = matrices[0]
    m = len(temp)
    n = len(temp[0])
    # 初始化一个空的大矩阵，形状为 (m*k, n*l)
    result = np.zeros((m * k, n * l), dtype=int)

    for i in range(k):
        for j in range(l):
            # 获取当前矩阵的位置
            idx = i * l + j
            # 将当前的 m*n 矩阵放到 result 中对应的位置
            result[i * m:(i + 1) * m, j * n:(j + 1) * n] = matrices[idx]

    return result


def main():
    # 混沌扩散的次数
    times = 1
    in_path = r"C:\Users\lenovo\Desktop\coding\note\NoteForCoding\test\jianqie\erweima_zhiluan.jpg"
    # 获得原始的一维图像序列,图像的高，图像的宽，这里是一样的
    picarry, pic_height, pic_width = decode_qrcode(in_path)
    # 将原始图像序列转成m×n的矩阵
    pic_M_N = list_to_matrix(picarry, pic_height, pic_width)
    # 将48×48的矩阵分成4×4的块
    pic_blocks = split_4x4_blocks(pic_M_N)

    # 扩散矩阵,一共times个m×n的扩散矩阵,n的大小来自于原始矩阵的大小
    tempkuosan = []
    for i in range(0, times):
        tempkuosan.append(list_to_matrix(
            x_vals[i*pic_height*pic_width: (i+1)*pic_height*pic_width], pic_height, pic_width))
    # 把tempkuosan中的六个矩阵的值都×100000取整数部分，对2取模,这样扩散矩阵就只有0，1
    for i in range(0, times):
        for j in range(0, pic_height):
            for k in range(0, pic_width):
                tempkuosan[i][j][k] = math.floor(
                    tempkuosan[i][j][k] * 100000) % 2
    # 将所有置乱矩阵分成4×4的块（一共有times×12×12块）
    tempkuosan_blocks = []
    for i in range(0, times):
        tempkuosan_blocks.append(split_4x4_blocks(tempkuosan[i]))
    # 每次一的运算方式(一共要进行 12×12 × times 次运算方式)
    opration_rule = []
    # 每次一的编码方式(一共要进行 12×12 × times 次运算方式)
    code_rule = []
    # 每次一的解码方式(一共要进行 12×12 × times 次运算方式)
    decode_rule = []
    # 横向分多少块
    ever_pic_time_x = pic_height//4
    # 纵向分多少块
    ever_pic_time_y = pic_width//4
    for i in range(ever_pic_time_x*ever_pic_time_y*times):
        opration_rule.append(math.floor(y_vals[i] * 100000) % 3 + 1)

    for i in range(ever_pic_time_x*ever_pic_time_y*times):
        code_rule.append(math.floor(x_vals[i] * 100000) % 8 + 1)

    for i in range(ever_pic_time_x*ever_pic_time_y*times, ever_pic_time_y*ever_pic_time_x*times*2):
        decode_rule.append(math.floor(z_vals[i] * 100000) % 8 + 1)

    # # 这个记录着原始矩阵每一次置乱后结果
    pic_diffuse = []
    # 开始进行运算
    # 首先先写大循环，一共times次扩散置乱，每次扩散置乱都要进行 heigh//4 * width//4次运算。奇数次的扩散是横向扩散，偶数次的扩散是纵向扩散
    for i in range(0, times):
        # 每一轮大循环有 heigh//4 * width//4次运算
        pic_diffuse_onetime = []  # 记录一次扩散置乱后的原图结果
        for j in range(0, ever_pic_time_x*ever_pic_time_y):
            pic_blocks_temp = []  # 记录一次扩散置乱后图块的结果
            # 原图的一个小图块先进行DNA编码
            pic_blocks_code = dna_encode(
                pic_blocks[j], code_rule[i*ever_pic_time_x*ever_pic_time_y + j], i % 2)
            # 扩散矩阵进行DNA编码
            tempkuosan_blocks_code = dna_encode(
                tempkuosan_blocks[i][j], code_rule[i*ever_pic_time_x*ever_pic_time_y + j], i % 2)
            # 进行DNA运算和解码
            pic_blocks_temp = dna_operation(pic_blocks_code, tempkuosan_blocks_code,
                                            opration_rule[i*ever_pic_time_x*ever_pic_time_y + j], decode_rule[i*ever_pic_time_x*ever_pic_time_y + j], i % 2)
            # 将一个小块的结果加入到一次扩散置乱后的结果中
            pic_diffuse_onetime.append(pic_blocks_temp)
        # 将每次扩散置乱后的结果更新到pic_diffuse中
        pic_diffuse = combine_matrices(
            pic_diffuse_onetime, pic_height // 4, pic_width // 4)

    # 把最后的扩散结果转成二值图像
    create_black_white_image(
        pic_diffuse.flatten(), pic_height, r"C:\Users\lenovo\Desktop\coding\note\NoteForCoding\test\jianqie\erweima_kuosan.jpg")

    # 读取扩散后的图像
    in_path = r"C:\Users\lenovo\Desktop\coding\note\NoteForCoding\test\jianqie\zaosheng\zoasheng_0.1.png"
    # 获得原始的一维图像序列,图像的高，图像的宽，这里是一样的
    picarry, pic_height, pic_width = decode_qrcode(in_path)
    # 将原始图像序列转成m×n的矩阵
    pic_M_N = list_to_matrix(picarry, pic_height, pic_width)
    # 将48×48的矩阵分成4×4的块
    pic_blocks = split_4x4_blocks(pic_M_N)
    # 逆扩散操作
    # 这个记录着原始矩阵每一次恢复后结果
    pic_rese = []
    # 扩散进行了times次，逆扩散也要进行times次
    # 首先先写大循环，一共times次扩散置乱，每次扩散置乱都要进行12×12次运算。奇数次的扩散是横向扩散，偶数次的扩散是纵向扩散
    for i in range(times - 1, -1, -1):
        # 每一次进行 heigh//4 * width//4 次逆扩散
        pic_inver_onetime = []  # 记录一次逆扩散置乱后结果
        for j in range(0, ever_pic_time_x*ever_pic_time_y):
            # 原始图一个小图块先进行DNA编码，这里用的decode_rule
            pic_blocks_code = dna_encode(
                pic_blocks[j], decode_rule[i*ever_pic_time_x*ever_pic_time_y + j], i % 2)
            # 扩散矩阵进行DNA编码
            tempkuosan_blocks_code = dna_encode(
                tempkuosan_blocks[i][j], code_rule[i*ever_pic_time_x*ever_pic_time_y + j], i % 2)
            # 进行DNA运算和解码
            # 这里如果之前是加就用减，如果用的异或就不变
            opt = opration_rule[i*ever_pic_time_x*ever_pic_time_y + j]
            if opt == 1:
                opt = 2
            elif opt == 2:
                opt = 1
            else:
                opt = 3  # 异或不变
            pic_blocks_temp = dna_operation(pic_blocks_code, tempkuosan_blocks_code,
                                            opt, code_rule[i*ever_pic_time_x*ever_pic_time_y + j], i % 2)
            # 将一个小块的结果加入到一次扩散置乱后的结果中
            pic_inver_onetime.append(pic_blocks_temp)

        # 将每次扩散置乱后的结果更新到pic_diffuse中
        pic_rese = combine_matrices(
            pic_inver_onetime, pic_height // 4, pic_width // 4)
        pic_blocks = split_4x4_blocks(pic_rese)

    # 把最后的扩散结果转成二值图像
    create_black_white_image(
        pic_rese.flatten(), pic_height, r"C:\Users\lenovo\Desktop\coding\note\NoteForCoding\test\jianqie\zaosheng\zoasheng_zhiluan_0.1.png")


if __name__ == "__main__":
    main()

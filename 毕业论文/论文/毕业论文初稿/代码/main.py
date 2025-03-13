
import cv2
import numpy as np
from PIL import Image
from skimage import io, color
from QR.QRCode import *
from QR.loadQR2arrary import *
from hundunxitong.yiweihundun import *
from tools.zhiluankuosan import *
from mixtools.mixOperation import *
from DNAtools.DNAduffsion import *
from pyzbar.pyzbar import decode


from DCT.DCT import *
from DCT.HVS import *
from DCT.pictools import *


# 参数设置
a = 35.0  # 系统参数a
b = 3.0   # 系统参数b
c = 28.0  # 系统参数c
x0, y0, z0 = 1.03201, 1.0, 1.0  # 初始条件
num_steps = 600 * 600 * 6  # 生成的步数
dt = 0.01  # 时间步长
# 嵌入强35度
r = 35
# 提取阈值
shell_threshold = 0.5
# 载体图像路径
zaiti_image_path = "lena.png"
# 扩散次数
times = 1

# 生成Chen混沌序列
x_vals, y_vals, z_vals = Chen(x0, y0, z0, a, b, c, num_steps)

pic_height = 48
pic_width = 48
vector_size = 18

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


def insert_PicMAC(original_image_path, image_hash, metadata, encryption_key):
    """
    插入版权信息到图片的鉴权模块入口函数。
    参数：
    - original_image (pic): 原始图片。
    - image_hash (str): 图片哈希值。
    - metadata (str): 图片元数据。
    - encryption_key (bytes): 加密密钥。
    返回：
    - Image: 带有嵌入版权信息的图片对象。
    """

    # 将哈希值转换成二维码
    generate_fixed_size_qr_code(image_hash, "hash.png")

    # 将二维码序列化一维0,1数组
    binary_array, height, width = decode_qrcode("hash.png")
    # inary_array, height, width = decode_qrcodeEx("newhash.png")
    print(height, width)

    generate_qrcode_from_array(binary_array, height, width, "newhash.png")

    # 获取一维混沌序列
    chaos_sequence = logistic_tent_sequence(
        encryption_key, 0.2, height * width*100)

    # 根据一维混沌序列将二维码打乱，打乱6次
    messArry = []
    for i in range(0, 6):
        messArry = knuth_durstenfeld_shuffle(
            binary_array, chaos_sequence[i*height*width:(i+1)*height*width])

    # 将打乱的二维码转换成图片
    # generate_qrcode_from_array(messArry, height, width, "newMix.png")
    create_black_white_image(messArry, height, "newMix.png")

    # 获得原的一维图像序列,图像的高，图像的宽，这里是一样的
    picarry, pic_height, pic_width = decode_qrcodeEx("newMix.png")
    # 将原始图像序列转成m×n的矩阵提取阈值
    pic_M_N = list_to_matrix(picarry, pic_height, pic_width)
    # 将m×n的矩阵分成4×4的块
    pic_blocks = split_4x4_blocks(pic_M_N)

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
    generate_qrcode_from_array(
        pic_diffuse.flatten(), pic_height, pic_width, "duffion.png")

    # 获取载体图像的宽和高
    pic_width, pic_height = get_image_size(original_image_path)

    # 将生成的扩散二值图像用DCT隐写到图像中
    # 读取图像，将图像按照8×8分块，对所有的分块都做DCT变换
    lena_block_dct = image_blocks_dct(original_image_path, 8)

    # 对所有的图像分块打分,获得排序后的图片队列
    lena_block_sorce = calculate_mean_variance_matrix(
        zaiti_image_path,  8)
    sort_sorce = select_top_k_blocks(lena_block_sorce, height * width)

    # 将置乱-扩散后的二维码序列化成一位0，1数组
    picarry, pic_height, pic_width = decode_qrcodeEx("duffion.png")

    random01 = [(1 if num % 1 >= 0.5 else 0)
                for num in chaos_sequence[0:48*48*vector_size]]

    sort_random01 = split_and_sort_by_ones(
        random01, pic_height*pic_width, vector_size)
    end_sort_random01 = adjust_group_ones(sort_random01)

    # 循环0，1数组，将0和1插入到DCT系数中
    DCT_end = apply_dct_and_modify_blocks(
        picarry, lena_block_dct, sort_sorce, r, end_sort_random01)

    # 对所有的分块做逆DCT变换
    reconstruct_image_from_dct(DCT_end, 8, "lena_new.png")


def extract_PicMAC(image_path, encryption_key):
    """
    插入版权信息到图片的鉴权模块入口函数。
    参数：
    - image (pic): 待鉴图片。
    - encryption_key (bytes): 解密密钥。
    返回：
    - str: 解密后的版权信息。
    """

    # 对所有的图像分块打分,获得排序后的图片队列
    lena_block_sorce = calculate_mean_variance_matrix(
        zaiti_image_path, 8)
    sort_sorce = select_top_k_blocks(lena_block_sorce, 48*48)

    # 获得排序后的图像后和载密图像进行相似度对比
    # 原始图像和载体图像都计算DCT系数
    lena_orignal = image_blocks_dct(zaiti_image_path, 8)
    lena_new = image_blocks_dct(image_path, 8)

    # 获取嵌入的随机0，1序列
    chaos_sequence = logistic_tent_sequence(
        encryption_key, 0.2, 48*48*100)
    random01 = [(1 if num % 1 >= 0.5 else 0)
                for num in chaos_sequence[0:48*48*vector_size]]

    sort_random01 = split_and_sort_by_ones(random01, 48*48, vector_size)

    end_sort_random01 = adjust_group_ones(sort_random01)
    # print(end_sort_random01)

    # 将end_sort_random01每个元素的值加一
    for i in range(0, len(end_sort_random01)):
        for j in range(0, len(end_sort_random01[i])):
            end_sort_random01[i][j] = end_sort_random01[i][j] * r

    # 按sort_sorce顺序对比两个图像的DCT系数
    blockes = extract_dct_blocks(
        lena_new, lena_orignal, end_sort_random01, sort_sorce, r, shell_threshold)

    # # 将随机的0，1序列编程二维的二值图像
    generate_qrcode_from_array(
        blockes, 48, 48, "Extract_duffion.png")

    # 获得原始的一维图像序列,图像的高，图像的宽，这里是一样的
    picarry, pic_height, pic_width = decode_qrcodeEx("Extract_duffion.png")
    print(pic_height, pic_width)
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
        pic_rese.flatten(), pic_height, "Extract_mix.png")

    # 将扩散图像的二值图像读成一维数组
    binary_array, height, width = decode_qrcodeEx("Extract_mix.png")

    orArry = []
    for i in range(0, 6):
        orArry = knuth_durstenfeld_shuffle_inverse(
            binary_array, chaos_sequence[(5-i)*height*width:(6-i)*height*width])
    # 根据一维数组生成图片并展示
    generate_qrcode_from_array(orArry, height, width, "he.png")


def save_grayscale_image(input_path, output_path):
    """
    将指定路径的图片转换为灰度图并保存

    参数:
    input_path (str): 输入图片路径
    output_path (str): 输出图片路径
    """
    # 打开图片文件
    with Image.open(input_path) as img:
        # 转换为灰度图像
        grayscale_img = img.convert('L')
        # 保存灰度图像
        grayscale_img.save(output_path)


def test(original_image_path, image_hash, metadata, encryption_key):
    # 将生成的扩散二值图像用DCT隐写到图像中
    # 读取图像，将图像按照8×8分块，对所有的分块都做DCT变换
    lena_block_dct = image_blocks_dct(original_image_path, 8)

    # 对所有的分块做逆DCT变换
    reconstruct_image_from_dct(lena_block_dct, 8, "lena_new.png")


def main():
    # test("lena.png", "111111111efadfafdfdsaf", "dddfd", 3.712345678)
    insert_PicMAC("lena.png", "111111111efadfafdfdsaf", "dddfd", 3.712345678)

    # save_grayscale_image("lena_new_18.png", "lena_18.png")

    extract_PicMAC("lena_new.png", 3.712345678)


if __name__ == '__main__':
    main()

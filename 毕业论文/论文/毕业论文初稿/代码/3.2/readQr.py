import cv2
import numpy as np
import qrcode
from PIL import Image
import matplotlib.pyplot as plt
import math


# logistic_tent函数
def logistic_tent_sequence(a, r0, num_values=1000):
    """
    生成Logistic-Tent混沌映射序列
    :param a: 控制参数（建议范围3.6-4.0）
    :param r0: 初始值（0 < r0 < 1）
    :param num_values: 需要生成的数值数量
    :return: 混沌序列列表
    """
    sequence = [r0]
    for _ in range(num_values - 1):
        current = sequence[-1]
        if current < 0.5:
            next_val = a * current * (1 - current) + (4 - a) * (current / 2)
        else:
            next_val = a * current * (1 - current) + \
                (4 - a) * ((1 - current) / 2)
        next_val = next_val % 1  # 确保结果在[0,1)范围内
        sequence.append(next_val)
    return sequence


# 参数设置（可根据需要修改）
a = 3.7    # 控制参数（典型混沌范围3.6-4.0）
r0 = 0.8   # 初始值（必须满足0 < r0 < 1）
n = 100000   # 生成数量

# 生成混沌序列
chaos_sequence = logistic_tent_sequence(a, r0, n)

# 将二维码转换成0，1序列


def decode_qrcode(image_path):
    # 使用 OpenCV 读取二维码图像
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # 二值化处理，确保图像是黑白的
    _, binary_img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)

    # 获取二维码图像的尺寸
    height, width = binary_img.shape

    # 将黑色为1，白色为0，转换成一维数组
    one_dimensional_array = []
    for i in range(height):
        for j in range(width):
            # 如果是黑色（像素值为0），就记录1，否则记录0
            one_dimensional_array.append(1 if binary_img[i, j] == 0 else 0)

# 将 one_dimensional_array 保存到 mmm.txt 文件
    with open('mmm.txt', 'w') as f:
        for i in range(height):
            for j in range(width):
                # 写入每个元素，注意要转换为字符串并加上空格
                f.write(f"{one_dimensional_array[i * width + j]} ")
            f.write('\n')  # 每行写完后换行

    return one_dimensional_array, height, width


# 将0，1序列转成黑白图像
def create_black_white_image(arr, n, output_path=None):
    # 将一维数组转换为二维数组
    if len(arr) != n * n:
        raise ValueError("输入数组的长度必须为 n * n")

    # 创建一个白色背景的 n x n 图像
    img = Image.new('1', (n, n), 1)  # '1' 是模式，代表黑白图像（0 为黑色，1 为白色）
    pixels = img.load()  # 获取图像的像素对象

    # 将数组值填充到图像上
    for i in range(n):
        for j in range(n):
            # 根据数组值设置像素（0 -> 白色, 1 -> 黑色）
            if arr[i * n + j] == 1:
                pixels[j, i] = 0  # 黑色

    # 展示图像
    img.show()

    # 保存图像（如果需要）
    img.save(output_path)


# 洗牌算法
def knuth_durstenfeld_shuffle(arr, randomArry):
    # 从数组的最后一个元素开始
    for i in range(len(arr) - 1, 0, -1):
        # 随机选择一个索引 j，满足 0 <= j <= i
        j = math.floor(i * randomArry[i])
        # 交换 i 和 j 处的元素
        arr[i], arr[j] = arr[j], arr[i]

    return arr

# 洗牌算法的逆算法


def knuth_durstenfeld_shuffle_inverse(arr, randomArry):
    # 从数组的第一个元素开始逆向恢复
    for i in range(0, len(arr) - 1, +1):
        # 计算在洗牌时对应的交换位置 j
        j = math.floor(i * randomArry[i])  # 根据 chaos_sequence 计算 j
        # 执行逆向交换
        arr[i], arr[j] = arr[j], arr[i]

    return arr

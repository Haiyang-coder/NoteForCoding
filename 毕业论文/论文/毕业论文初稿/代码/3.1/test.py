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
n = 600*600*6   # 生成数量

# 生成序列
chaos_sequence = logistic_tent_sequence(a, r0, n)

# 将二维码转换成一维数组


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

    return one_dimensional_array, height, width


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


def knuth_durstenfeld_shuffle(arr, randomArry):
    # 从数组的最后一个元素开始
    for i in range(len(arr) - 1, 0, -1):
        # 随机选择一个索引 j，满足 0 <= j <= i
        j = math.floor(i * randomArry[i])
        # 交换 i 和 j 处的元素
        arr[i], arr[j] = arr[j], arr[i]

    return arr


def knuth_durstenfeld_shuffle_inverse(arr, randomArry):
    # 从数组的第一个元素开始逆向恢复

    for i in range(1, len(arr)):
        # 使用相同的随机数计算 j
        j = math.floor(i * randomArry[i])
        # 交换 i 和 j 处的元素，即撤销之前对应的交换
        arr[i], arr[j] = arr[j], arr[i]

    # for i in range(0, len(arr) - 1, +1):
    #     # 计算在洗牌时对应的交换位置 j
    #     j = math.floor(i * randomArry[i])  # 根据 chaos_sequence 计算 j
    #     # 执行逆向交换
    #     arr[i], arr[j] = arr[j], arr[i]

    return arr


def main():
    # 读取二维码并转为一维数组
    image_path = "newhash.png"  # 输入二维码文件路径
    binary_array, height, width = decode_qrcode(image_path)
    # 将二维码图像的尺寸设置为 n x n (取最小边长作为 n)
    n = min(height, width)
    output_path = "newMix.png"  # 输出二维码文件路径

    # 将一维数组完全置乱，生成新的0，1序列
    # 进行连续的6次置乱
    messArry = []
    for i in range(0, 6):
        messArry = knuth_durstenfeld_shuffle(
            binary_array, chaos_sequence[i*height*width:(i+1)*height*width])
    create_black_white_image(messArry, n, output_path)

    # 将完全置乱一维数组,复原
    # 因为置乱了6次，所以逆置乱也要进行6次
    # 读取二维码并转为一维数组
    image_path = "newMix.png"  # 输入二维码文件路径
    binary_array, height, width = decode_qrcode(image_path)
    output_path = "he.png"  # 输出二维码文件路径
    orArry = []  # 复原的数组
    for i in range(0, 6):
        orArry = knuth_durstenfeld_shuffle_inverse(
            binary_array, chaos_sequence[(5-i)*height*width:(6-i)*height*width])
    # 根据一维数组生成图片并展示
    create_black_white_image(orArry, n, output_path)


if __name__ == "__main__":
    main()

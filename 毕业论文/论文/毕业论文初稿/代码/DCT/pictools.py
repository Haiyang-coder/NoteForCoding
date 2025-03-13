from PIL import Image
import numpy as np
from scipy.fftpack import dct
import math


def get_image_size(image_path):
    img = Image.open(image_path)
    width, height = img.size
    return width, height

# 把n*n的图片切成m*m的块


def split_image_into_blocks(image_path,  m):
    image = Image.open(image_path)
    image_array = np.array(image)

    height, width = image_array.shape[:2]

    if height % m != 0:
        raise ValueError(
            "Image dimensions must be divisible by block size")

    if width % m != 0:
        raise ValueError(
            "Image dimensions must be divisible by block size")

    blocks = []

    for i in range(0, height, m):
        row_blocks = []
        for j in range(0, width, m):
            block = image_array[i:i + m, j:j + m]
            row_blocks.append(block)
        blocks.append(row_blocks)

    return blocks

# 把一个序列按照混沌序列和洗牌算法打乱


def shuffle_blocks(blocks, randomArry):
    # 从数组的最后一个元素开始
    for i in range(len(blocks) - 1, 0, -1):
        # 随机选择一个索引 j，满足 0 <= j <= i
        j = math.floor(i * randomArry[i])
        # 交换 i 和 j 处的元素
        blocks[i], blocks[j] = blocks[j], blocks[i]

    return blocks

# 把一个序列按照混沌序列和洗牌算法恢复


def shuffle_blocks_inverse(blocks, randomArry):
    # 从数组的第一个元素开始逆向恢复
    for i in range(0, len(blocks) - 1, +1):
        # 计算在洗牌时对应的交换位置 j
        j = math.floor(i * randomArry[i])  # 根据 chaos_sequence 计算 j
        # 执行逆向交换
        blocks[i], blocks[j] = blocks[j], blocks[i]

    return blocks

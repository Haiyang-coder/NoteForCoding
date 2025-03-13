import cv2
import numpy as np
from .pictools import *

# 选出分数最高的前 k 个图像块，并记录坐标


def select_top_k_blocks(score_matrix, k):
    flat_scores = [(i, j, score_matrix[i, j])
                   for i in range(score_matrix.shape[0])
                   for j in range(score_matrix.shape[1])]

    # 按分数降序排序，如果分数相同按行列顺序
    top_k_blocks = sorted(flat_scores, key=lambda x: (-x[2], x[0], x[1]))[:k]

    return [(i, j) for i, j, _ in top_k_blocks]

# 计算每个小块的均值和方差之和，并保存到二维矩阵


def calculate_mean_variance_matrix(image_path, m):
    blocks = split_image_into_blocks(image_path,  m)
    result_matrix = np.zeros((len(blocks), len(blocks[0])))

    max_variance, min_variance = calculate_max_min_variance(image_path, m)

    for i, row in enumerate(blocks):
        for j, block in enumerate(row):
            mean, variance = calculate_mean_variance_inmatrix(block)
            result_matrix[i, j] = 0.6*(
                abs(mean-128)/128) + 0.4*((variance-min_variance) / (max_variance-min_variance))

    return result_matrix


def calculate_mean_variance_inmatrix(matrix):
    # 计算输入矩阵的均值和方差
    mean = np.mean(matrix)
    variance = np.var(matrix)
    return mean, variance


def calculate_mean_variance_inPic(image_path):
    # 读取灰度图像，计算均值和方差
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        print("无法读取图像，请检查路径！")
        return

    # 计算均值和方差
    mean = np.mean(image)
    variance = np.var(image)

    return mean, variance


# 计算每个小块的均值和方差之和，找出最大方差，最小方差
def calculate_max_min_variance(image_path,  m):
    blocks = split_image_into_blocks(image_path,  m)

    max_variance = 0
    min_variance = 0

    for i, row in enumerate(blocks):
        for j, block in enumerate(row):
            mean, variance = calculate_mean_variance_inmatrix(block)
            if variance > max_variance:
                max_variance = variance
            if variance < min_variance:
                min_variance = variance

    return max_variance, min_variance

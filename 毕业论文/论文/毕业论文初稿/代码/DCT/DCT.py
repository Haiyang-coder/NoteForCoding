from scipy.fftpack import dct
from scipy.fftpack import idct
import cv2
from skimage import io, color
from skimage.color import rgb2gray

from .HVS import *
from .pictools import *

mid_freq_indices = [(2, 1), (1, 2), (2, 2), (3, 0), (0, 3), (3, 1), (1, 3),
                    (3, 2), (2, 3), (4, 0), (0, 4), (4, 1), (1, 4), (4, 2),
                    (2, 4), (4, 3), (3, 4), (5, 0), (0, 5), (5, 1), (1, 5), (5, 2)]


mid_freq_indices_short = [(2, 2), (3, 1), (1, 3),
                          (3, 2), (2, 3), (4, 0), (0, 4), (4, 1), (1, 4), (4, 2),
                          (2, 4), (4, 3), (3, 4), (5, 0), (0, 5), (5, 1), (1, 5), (5, 2)]


mid_freq_indices_change = [(3, 2), (2, 3)]

# 根据坐标列表对 DCT 系数矩阵的中频系数加上一个r*num的值


def apply_dct_and_modify_blocks(picCode, blocks, coords, r, num):
    number = 0
    for i, j in coords:
        if picCode[number] == 1:
            twenty_two_block = num[number]
            blocks[i][j] = add_one_to_mid_freq_coefficients(
                blocks[i][j], r, twenty_two_block)
        number += 1
    return blocks

# 按照坐标列表对DCT系数矩阵的中频系数提取出嵌入的信息


def extract_dct_blocks(newblocks, oldblocks, vectorblocks, coords, r,  shell_threshold):
    number = []
    num = 0
    for i, j in coords:
        new_dct_matrix = newblocks[i][j]
        old_dct_matrix = oldblocks[i][j]
        onenum = extract_one_coefficients(
            new_dct_matrix, old_dct_matrix, vectorblocks[num], r, shell_threshold)
        number.append(onenum)
        num += 1

    return number


# 提取中频系数的向量值
def extract_one_coefficients(new_dct_matrix, oldblocks, vector_orginal, r, shell_threshold):
    vector = []
    for i, j in mid_freq_indices_short:
        temp = new_dct_matrix[i][j] - oldblocks[i][j]
        vector.append(temp)

    return is_insertedEx(vector, vector_orginal, r, shell_threshold)


# 判断是否插入
def is_inserted(new_vector, old_vector, r, shell_threshold=0.1):

    # 确保向量长度一致
    if len(new_vector) != len(old_vector):
        raise ValueError("两个向量的维度不一致")
    # 计算归一化互相关
    numerator = np.dot(new_vector, old_vector)
    denominator = np.linalg.norm(new_vector) * np.linalg.norm(old_vector)

    # 避免除以零
    # if denominator == 0:
    #     return 0

    if (numerator / denominator) >= shell_threshold:
        return 1
    else:
        return 0

    # 判断是否插入


def is_insertedEx(new_vector, old_vector,  r, shell_threshold):

    # 确保向量长度一致
    if len(new_vector) != len(old_vector):
        raise ValueError("两个向量的维度不一致")

    # if (sum(new_vector) - sum(old_vector) < 8):
    #     return 0

    vec1 = np.array(new_vector)
    vec2 = np.array(old_vector)
    similarity = np.dot(vec1, vec2) / \
        (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    if similarity >= shell_threshold:
        return 1

    else:
        return 0


# 对图片切成m*m的块，然后对每个块做DCT变换，返回二维的DCT变换后的矩阵


def image_blocks_dct(image_path,  m):
    image = io.imread(image_path, as_gray=True)  # 读取并转换为灰度图像
    image = image.astype(np.float64)

    # 获得图片的高和宽
    height, width = image.shape[:2]
    height = height // m
    width = width // m

    blocks = []
    block_size = m
    for i in range(0, image.shape[0], block_size):
        row_blocks = []
        for j in range(0, image.shape[1], block_size):
            block = image[i:i+block_size, j:j+block_size]
            if block.shape[0] == block_size and block.shape[1] == block_size:
                dct_matrix = dct(dct(block.T, norm='ortho').T, norm='ortho')
                row_blocks.append(dct_matrix)
        if row_blocks:
            blocks.append(row_blocks)
    return blocks


# 对m*m的块做DCT变换，返回二维的DCT变换后的矩阵
def apply_dct(matrix):
    return dct(dct(matrix.T, norm='ortho').T, norm='ortho')


# 增加中频系数加上一个r*num的值
def add_one_to_mid_freq_coefficients_long(dct_matrix,  r, num):
    number = 0
    for i, j in mid_freq_indices:

        temp = dct_matrix[i, j]
        dct_matrix[i, j] = temp + r * num[number]
        number += 1

    return dct_matrix


# 增加中频系数加上一个r*num的值
def add_one_to_mid_freq_coefficients(dct_matrix,  r, num):
    number = 0
    for i, j in mid_freq_indices_short:
        dct_matrix[i, j] = dct_matrix[i, j] + r * num[number]
        number += 1

    return dct_matrix


# 执行逆 DCT 变换，恢复图像块
def apply_inverse_dct(dct_matrix):
    """
    对输入的 DCT 系数矩阵执行逆 DCT 变换。

    参数：
    dct_matrix (np.array): 输入的 DCT 系数矩阵。

    返回：
    np.array: 逆变换后的图像块。
    """
    return idct(idct(dct_matrix.T, norm='ortho').T, norm='ortho')


# 将存储 DCT 系数的二维矩阵恢复成完整图像
def reconstruct_image_from_dct(dct_blocks, m, save_path=None):
    """
    通过逆 DCT 变换将二维矩阵中的 DCT 系数块还原成完整图像。

    参数：
    dct_blocks (list of list of np.array): 存储 DCT 系数的二维数组。
    m (int): 每个块的大小，例如 8 表示 8x8。

    返回：
    np.array: 重构后的完整图像。
    """
    rows = len(dct_blocks)
    cols = len(dct_blocks[0])

    reconstructed_image = np.zeros((rows * m, cols * m), dtype=np.float64)

    for i in range(rows):
        for j in range(cols):
            block = idct(
                idct((dct_blocks[i][j]).T, norm='ortho').T, norm='ortho')
            reconstructed_image[i * m:(i + 1) * m, j * m:(j + 1) * m] = block

    if save_path:
        cv2.imwrite(save_path, np.clip(
            np.round(reconstructed_image), 0, 255).astype(np.uint8))

    return reconstructed_image

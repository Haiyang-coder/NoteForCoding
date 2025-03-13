
import numpy as np

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

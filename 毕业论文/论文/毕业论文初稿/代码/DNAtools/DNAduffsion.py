
import numpy as np


dna_code_rules = {
    1: {'00': 'A', '11': 'T', '10': 'C', '01': 'G'},
    2: {'00': 'A', '11': 'T', '01': 'C', '10': 'G'},
    3: {'11': 'A', '00': 'T', '10': 'C', '01': 'G'},
    4: {'11': 'A', '00': 'T', '01': 'C', '10': 'G'},
    5: {'01': 'A', '10': 'T', '11': 'C', '00': 'G'},
    6: {'01': 'A', '10': 'T', '00': 'C', '11': 'G'},
    7: {'10': 'A', '01': 'T', '00': 'C', '11': 'G'},
    8: {'10': 'A', '01': 'T', '11': 'C', '00': 'G'}
}


dna_decode_rules = {
    rule_num: {v: k for k, v in mapping.items()}
    for rule_num, mapping in dna_code_rules.items()
}

# 定义DNA字符到索引的映射
dna_to_index = {'A': 0, 'G': 1, 'C': 2, 'T': 3}
index_to_dna = {0: 'A', 1: 'G', 2: 'C', 3: 'T'}

# 定义DNA运算表
add_table = [
    [0, 1, 2, 3],
    [1, 0, 3, 2],
    [2, 3, 1, 0],
    [3, 2, 0, 1]
]

sub_table = [
    [0, 1, 3, 2],
    [1, 0, 2, 3],
    [2, 3, 0, 1],
    [3, 2, 1, 0]
]

xor_table = [
    [0, 1, 2, 3],
    [1, 0, 3, 2],
    [2, 3, 0, 1],
    [3, 2, 1, 0]
]

# 运算函数


def two_dna_operation(a, b, operation):
    a_idx = dna_to_index[a]
    b_idx = dna_to_index[b]

    if operation == 1:  # 加法
        result_idx = add_table[a_idx][b_idx]
    elif operation == 2:  # 减法
        result_idx = sub_table[a_idx][b_idx]
    elif operation == 3:  # 异或
        result_idx = xor_table[a_idx][b_idx]
    else:
        print("无效的运算类型")
        return None

    return index_to_dna[result_idx]


def dna_encode(binary_matrix: list, rule: int, opt: int) -> list:
    if opt == 1:
        return dna_horizontal_encode(binary_matrix, rule)
    else:
        return dna_vertical_encode(binary_matrix, rule)


def dna_horizontal_encode(binary_matrix: list, rule: int) -> list:
    # DNA横向编码规则
    """
    将n×n的0-1矩阵按指定DNA规则编码为n×(n/2)的碱基矩阵

    参数:
        binary_matrix (list): n×n二维列表，元素为0或1
        rule (int): DNA编码规则编号（1-8）

    返回:
        list: n×(n/2)的DNA编码矩阵

    异常:
        ValueError: 输入不符合要求时抛出
    """
    # 验证输入合法性‌:ml-citation{ref="1,2" data="citationList"}
    n = len(binary_matrix)
    if not all(len(row) == n for row in binary_matrix) or n % 2 != 0:
        raise ValueError("输入矩阵必须是n×n且n为偶数")
    if any(cell not in {0, 1} for row in binary_matrix for cell in row):
        raise ValueError("矩阵元素必须为0或1")
    if not 1 <= rule <= 8:
        raise ValueError("规则编号必须为1-8的整数")

    # 转换二进制序列为DNA编码‌:ml-citation{ref="4,5" data="citationList"}
    encoded = []
    rule_dict = dna_code_rules[rule]

    for row in binary_matrix:
        # 将二进制列表转为字符串‌:ml-citation{ref="6" data="citationList"}
        binary_str = ''.join(map(str, row))
        # 每两位分割并编码‌:ml-citation{ref="3" data="citationList"}
        encoded_row = [
            rule_dict[binary_str[i:i+2]]
            for i in range(0, len(binary_str), 2)
        ]
        encoded.append(encoded_row)

    return encoded


def dna_vertical_encode(binary_matrix: list, rule: int) -> list:
    """
    将n×n的0-1矩阵按列编码为(n/2)×n的DNA碱基矩阵

    参数:
        binary_matrix (list): n×n二维列表，元素为0或1
        rule (int): DNA编码规则编号（1-8）

    返回:
        list: (n/2)×n的DNA编码矩阵
    """
    # 输入验证（同横向编码）‌:ml-citation{ref="1,2" data="citationList"}
    n = len(binary_matrix)
    if not all(len(row) == n for row in binary_matrix) or n % 2 != 0:
        raise ValueError("输入矩阵必须是n×n且n为偶数")
    if any(cell not in {0, 1} for row in binary_matrix for cell in row):
        raise ValueError("矩阵元素必须为0或1")
    if not 1 <= rule <= 8:
        raise ValueError("规则编号必须为1-8的整数")

    # 初始化结果矩阵（n/2行 × n列）
    encoded = [[None for _ in range(n)] for _ in range(n//2)]
    rule_dict = dna_code_rules[rule]

    # 按列处理二进制数据
    for col in range(n):
        # 提取当前列的二进制序列
        binary_str = ''.join(str(binary_matrix[row][col]) for row in range(n))

        # 每两位分割并编码‌:ml-citation{ref="3" data="citationList"}
        encoded_col = [
            rule_dict[binary_str[i:i+2]]
            for i in range(0, len(binary_str), 2)
        ]

        # 填充到结果矩阵的对应列
        for row in range(n//2):
            encoded[row][col] = encoded_col[row]

    return encoded


def dna_horizontal_operation(matrix_a: list, matrix_b: list,
                             operation: int, decode_rule: int) -> list:
    """
    对两个横向编码矩阵执行DNA运算，返回n×n二进制矩阵

    参数:
        matrix_a (list): n×(n/2) DNA编码矩阵
        matrix_b (list): n×(n/2) DNA编码矩阵
        operation (int): 运算类型(1-3: 异或/加法/减法)
        decode_rule (int): 解码规则编号(1-8)

    返回:
        list: n×n二进制矩阵
    """
    # 输入验证‌:ml-citation{ref="1,5" data="citationList"}
    n = len(matrix_a)
    if n != len(matrix_b) or any(len(row) != len(matrix_b[i]) for i, row in enumerate(matrix_a)):
        raise ValueError("输入矩阵尺寸不一致")
    if not all(len(row) == n//2 for row in matrix_a):
        raise ValueError("输入矩阵尺寸不符合n×(n/2)要求")
    if not 1 <= operation <= 3 or not 1 <= decode_rule <= 8:
        raise ValueError("参数范围错误")

    # 执行矩阵运算‌:ml-citation{ref="2,3" data="citationList"}
    result = []
    for row_a, row_b in zip(matrix_a, matrix_b):
        binary_row = []
        for a, b in zip(row_a, row_b):
            # 执行二进制运算
            res_DNAcode = two_dna_operation(a, b, operation)

            res_end = dna_decode_rules[decode_rule][res_DNAcode]
            # print("他的解码是")
            # print(res_end)
            # 转换为0-1列表‌:ml-citation{ref="3" data="citationList"}
            binary_row.extend([int(bit) for bit in res_end])
        result.append(binary_row)

    return result


def dna_vertical_operation(matrix_a: list, matrix_b: list,
                           operation: int, decode_rule: int) -> list:
    """
    对两个纵向编码矩阵执行DNA运算，返回n×n二进制矩阵

    参数:
        matrix_a (list): (n/2)×n DNA编码矩阵
        matrix_b (list): (n/2)×n DNA编码矩阵
        operation (int): 运算类型(1-3: 异或/加法/减法)
        decode_rule (int): 解码规则编号(1-8)

    返回:
        list: n×n二进制矩阵
    """
    # 输入验证‌:ml-citation{ref="1,3" data="citationList"}
    n_half = len(matrix_a)
    n = num_cols = len(matrix_a[0]) if matrix_a else 0  # 防止空矩阵的情况
    if len(matrix_b) != n_half or any(len(row) != n for row in matrix_a + matrix_b):
        raise ValueError("输入矩阵尺寸不匹配(n/2)×n要求")
    if n_half * 2 != n or not all(c in {'A', 'T', 'C', 'G'} for row in matrix_a+matrix_b for c in row):
        raise ValueError("输入矩阵元素或尺寸非法")
    if not 1 <= operation <= 3 or not 1 <= decode_rule <= 8:
        raise ValueError("参数范围错误")

    result = []
    for y in range(0, n):
        binary_row = []
        for x in range(0, n_half):

            # 解码碱基为二进制，这个应该用解码方式，比如当时编码用的1，你解码也得用1
            # print("现在执行运算的是")
            # print(matrix_a[x][y])
            # print(matrix_b[x][y])

            # 执行二进制运算
            res_DNAcode = two_dna_operation(
                matrix_a[x][y], matrix_b[x][y], operation)
            # print("运算的结果是")
            # print(res_DNAcode)
            res_end = dna_decode_rules[decode_rule][res_DNAcode]
            # print("解码的结果是")
            # print(res_end)
            # 转换为0-1列表‌:ml-citation{ref="3" data="citationList"}
            # 这里帮我改一下，我想binary_row是个一维数组，每次脂肪res_end里面的值，不保存他的结构
            binary_row.extend([int(bit) for bit in res_end])

        result.append(binary_row)  # 这里帮我一下，我想讲这个relust的

    return [list(row) for row in zip(*result)]


def dna_operation(matrix_a: list, matrix_b: list,
                  operation: int, decode_rule: int, opt: int) -> list:
    if opt == 1:
        return dna_horizontal_operation(matrix_a, matrix_b, operation, decode_rule)
    else:
        return dna_vertical_operation(matrix_a, matrix_b, operation, decode_rule)


# # 示例调用
# if __name__ == "__main__":
#     #     # 测试4×4矩阵，规则1
#     #     test_matrix = [
#     #         [0, 0, 0, 1],
#     #         [1, 0, 1, 1],
#     #         [0, 1, 1, 0],
#     #         [1, 1, 0, 0]
#     #     ]
#     #     result1 = dna_vertical_encode(test_matrix, 1)
#     #     result2 = dna_horizontal_encode(test_matrix, 1)
#     #     print("竖向编码结果:")
#     #     for row in result1:
#     #         print(row)

#     #     print("横向编码结果:")
#     #     for row in result2:
#     #         print(row)

#     # test_hengA = [
#     #     ['A', 'T'],
#     #     ['C', 'G'],
#     #     ['T', 'C'],
#     #     ['G', 'A']
#     # ]
#     # test_hengB = [
#     #     ['C', 'G'],
#     #     ['A', 'C'],
#     #     ['A', 'G'],
#     #     ['G', 'T']
#     # ]
#     # # 原始矩阵
#     # test_hengC = [
#     #     ['C', 'A', 'A', 'G'],
#     #     ['G', 'C', 'G', 'T']

#     # ]
#     # # 扩散矩阵
#     # test_hengD = [
#     #     ['A', 'C', 'T', 'G'],
#     #     ['T', 'G', 'C', 'A']
#     # ]
#     # # reslut3 = dna_horizontal_operation(test_hengA, test_hengB, 1, 8, 1)
#     # # print("两个横向的扩散矩阵运算的结果是:")
#     # # print(reslut3)

#     testA = [
#         [0, 0, 0, 1],
#         [1, 0, 1, 1],
#         [0, 1, 1, 0],
#         [1, 1, 0, 0]
#     ]

#     testB = [
#         [1, 0, 0, 1],
#         [1, 0, 1, 1],
#         [0, 1, 1, 0],
#         [1, 1, 0, 0]
#     ]

#     testC = [
#         [1, 1, 0, 1],
#         [1, 0, 0, 1],
#         [0, 1, 0, 1],
#         [1, 0, 0, 0]
#     ]
#     # 先对矩阵竖向扩散A 加 B 得到 reslutAB
#     testA_shu = dna_vertical_encode(testA, 1)
#     testB_shu = dna_vertical_encode(testB, 1)

#     reslutAB = dna_vertical_operation(testA_shu, testB_shu, 1, 8)

#     # 对reslutAB 横向扩散，用异或 和 C 得到ABC
#     testAB_heng = dna_horizontal_encode(reslutAB, 2)
#     testC_heng = dna_horizontal_encode(testC, 2)
#     reslutABC = dna_horizontal_operation(testAB_heng, testC_heng, 3, 6)

#     print("reslutABC")
#     print(reslutABC)

#     # ABC 异或 C得到AB
#     reslutABC_heng = dna_horizontal_encode(reslutABC, 6)
#     reslutAB_back = dna_horizontal_operation(reslutABC_heng, testC_heng, 3, 2)

#     # AB 减矩阵 B 得到矩阵A
#     reslutAB_back_k = dna_vertical_encode(reslutAB_back, 8)
#     out = dna_vertical_operation(reslutAB_back_k, testB_shu, 2, 1)
#     print(out)

#     # # 将 reslutAB 减B得到A
#     # reslutAB_back = dna_vertical_encode(reslutAB, 8)
#     # out = dna_vertical_operation(reslutAB_back, testB_shu, 2, 1)
#     # print(out)

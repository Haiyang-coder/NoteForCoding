

import math
# 这里面都是置乱的算法，还有扩散的算法


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
        # 计算在洗牌时对应的交换位置 j
        j = math.floor(i * randomArry[i])  # 根据 chaos_sequence 计算 j
        # 执行逆向交换
        arr[i], arr[j] = arr[j], arr[i]

    return arr

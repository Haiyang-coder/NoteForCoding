# logistic_tent函数
def logistic_tent_sequence(a, r0, num_values):
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


def split_and_sort_by_ones(arr, n, size):
    # 确保数组长度是 22 * n
    length = size * n
    arr = arr[:length]

    # 将数组划分为 n 个长度为 22 的小组
    groups = [arr[i:i + size] for i in range(0, length, size)]

    # 按照每个小组中 1 的数量排序，数量多的在前
    sorted_groups = sorted(groups, key=lambda x: -sum(x))

    return sorted_groups


def adjust_group_ones(groups):
    adjusted_groups = groups
    for group in adjusted_groups:
        ones_count = sum(group)

        # 如果 1 的数量超过 16，从头开始改 1 为 0
        if ones_count > 16:
            excess = ones_count - 16
            for i in range(len(group)):
                if group[i] == 1 and excess > 0:
                    group[i] = 0
                    excess -= 1
                if excess == 0:
                    break
        elif ones_count <= 16:
            break

    for i in range(len(adjusted_groups) - 1, -1, -1):
        ones_count = sum(adjusted_groups[i])
        if sum(adjusted_groups[i]) < 8:
            excess = 8 - ones_count
            for j in range(len(adjusted_groups[i])):
                if adjusted_groups[i][j] == 0 and excess > 0:
                    adjusted_groups[i][j] = 1
                    excess -= 1
                if excess == 0:
                    break
        # 如果 1 的数量少于 8，从尾开始改 0 为 1
        elif ones_count >= 8:
            break

    return adjusted_groups

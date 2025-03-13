import numpy as np
import matplotlib.pyplot as plt

# Henon 映射函数
def henon_map(x, y, a, b=0.3):
    return 1 - a * x ** 2 + y, b * x

# 参数范围与初始条件
a_values = np.linspace(1.0, 1.4, 1000)  # 控制参数 a 的范围
iterations = 1000  # 总迭代次数
last = 100         # 绘制最后的 100 次结果

x, y = 0, 0  # 初始值

# 绘制分岔图
plt.figure(figsize=(10, 7))

for a in a_values:
    x, y = 0, 0  # 每个 a 重新初始化
    for _ in range(iterations):
        x, y = henon_map(x, y, a)
        if _ >= (iterations - last):  # 只绘制最后的稳定状态
            plt.plot(a, x, ',k', alpha=0.25)  # 使用逗号标记加快绘图速度

plt.xlabel('a')
plt.ylabel('x')
plt.title('Henon Map Bifurcation Diagram')
plt.show()

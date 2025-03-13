import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# 参数设置
a_values = np.linspace(0.5, 1.5, 5000)  # 可变参数 a 的范围
b = 0.3      # Henon 映射中的 b 参数
c = 0.1      # 改进项的耦合参数

iterations = 1000  # 预迭代次数，去除瞬态影响
last = 200         # 最后绘制的迭代次数

plt.figure(figsize=(10, 8))

# 对每个 a 值进行迭代
for a in tqdm(a_values):
    # 初始化初值
    x, y = 0.1, 0.1
    # 先预迭代，去除初始瞬态
    for _ in range(iterations):
        x, y = 1 - a * x**2 + y + c * x * y, b * x
    # 记录后续迭代结果进行绘图
    for _ in range(last):
        x, y = 1 - a * x**2 + y + c * x * y, b * x
        plt.plot(a, x, ',b', alpha=0.25)  # 蓝色点标记

plt.xlabel('a')
plt.ylabel('x')
plt.title('改进型二维 Henon 映射分岔图\n(公式: xₙ₊₁ = 1 - a xₙ² + yₙ + c xₙ yₙ,  yₙ₊₁ = b xₙ)')
plt.xlim(0.5, 1.5)
plt.ylim(0, 1.2)
plt.show()

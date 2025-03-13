
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm


def TentMap():
    r_values = np.linspace(0, 2, 10000)
    iterations = 1000
    last = 200
    x = np.full_like(r_values, 0.5)  # 初始值

    plt.figure(figsize=(10, 8))
    for i in tqdm(range(iterations + last)):
        x = np.where(x < 0.5, r_values * x, r_values * (1 - x))
        if i >= iterations:
            plt.plot(r_values, x, ',b', alpha=0.5)  # 蓝色线条

    plt.title(r'Tent Map Bifurcation Diagram')
    plt.xlabel('r')
    plt.ylabel('x')
    plt.xlim(0, 2)
    plt.ylim(0, 1)
    plt.show()


# 绘制 Tent 映射分岔图
TentMap()

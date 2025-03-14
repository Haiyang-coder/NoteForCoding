from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
fig = plt.figure(figsize=(10, 8), dpi=100)


def LogisticMap():
    mu = np.arange(0, 4, 0.01)
    x = 0.1  # 初值
    iters = 1000  # 不进行输出的迭代次数
    last = 200  # 最后画出结果的迭代次数
    for i in tqdm(range(iters+last)):
        x = mu * x * (1 - x)
        if i >= iters:
            plt.plot(mu, x, color='blue', alpha=0.5)  #
            plt.ylim(0, 1)
            plt.xlim(0, 4)

            plt.title(r'Logistic Map Bifurcation Diagram')
            plt.ylabel('x-Random number')
            plt.xlabel('μ-Rate')
    plt.show()


LogisticMap()

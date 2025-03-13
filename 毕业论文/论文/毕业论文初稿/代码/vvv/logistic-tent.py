import numpy as np
import matplotlib.pyplot as plt

# Logistic-Tent映射函数


def logistic_tent(x, eta):
    if x < 0.5:
        return (eta * x * (1 - x) + (4 - eta) * x / 2)
    else:
        return (eta * x * (1 - x) + (4 - eta) * (1 - x) / 2)

# 分岔图函数


def bifurcation(eta_min, eta_max, num_points, num_iterations, last_iterations):
    eta_values = np.linspace(eta_min, eta_max, num_points)
    x_values = np.zeros((num_points, last_iterations))

    for i, eta in enumerate(eta_values):
        x = 0.4  # 初始值
        for _ in range(num_iterations):
            x = logistic_tent(x, eta)
        for j in range(last_iterations):
            x = logistic_tent(x, eta)
            x_values[i, j] = x

    plt.figure(figsize=(10, 7))
    plt.plot(eta_values, x_values, ',k', color='blue', alpha=0.25)  # 绘制分岔图
    plt.title('logistic_tent Bifurcation Diagram')
    plt.xlabel('Parameter η')
    plt.ylabel('Variable x')
    plt.show()


# 参数设置
eta_min = 1.0
eta_max = 4.0
num_points = 10000  # η的点数
num_iterations = 1000  # 总迭代次数
last_iterations = 100  # 用于绘制的最后迭代次数

bifurcation(eta_min, eta_max, num_points, num_iterations, last_iterations)

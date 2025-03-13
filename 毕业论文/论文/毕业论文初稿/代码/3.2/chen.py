import numpy as np
import matplotlib.pyplot as plt


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


# 参数设置
a = 35.0  # 系统参数a
b = 3.0   # 系统参数b
c = 28.0  # 系统参数c
x0, y0, z0 = 1.001, 1.0, 1.0  # 初始条件
num_steps = 100000  # 生成的步数
dt = 0.01  # 时间步长

# 生成Chen混沌序列
x_vals, y_vals, z_vals = Chen(x0, y0, z0, a, b, c, num_steps)

# 绘制三维轨迹
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot(x_vals, y_vals, z_vals, lw=0.5)
ax.set_title("Chen Chaos System - 3D Trajectory")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
plt.show()

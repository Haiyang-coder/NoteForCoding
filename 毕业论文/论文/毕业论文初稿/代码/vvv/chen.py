import numpy as np
import matplotlib.pyplot as plt
# 绘制三维图像
import mpl_toolkits.mplot3d as p3d


'''
Chen吸引子生成函数
参数为三个初始坐标，三个初始参数,迭代次数
返回三个一维数组(坐标)
'''


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


def main():
    # 设定参数
    a = 35
    b = 3
    c = 28
    # 迭代次数
    T = 10000
    # 设初值
    x0 = 0
    y0 = 1
    z0 = 0
    # fig=plt.figure()
    # ax=p3d.Axes3D(fig)
    x, y, z = Chen(x0, y0, z0, a, b, c, T)
    ax = plt.subplot(121, projection="3d")
    ax.scatter(x, y, z, s=5)
    ax.set_xlabel('x(t)')
    ax.set_ylabel('y(t)')
    ax.set_zlabel('z(t)')
    ax.set_title('x0={0} y0={1} z0={2}'.format(x0, y0, z0))
    # plt.axis('off')
    # 消除网格

    ax.grid(False)
    # 初值微小的变化
    x0 = 0
    y0 = 1.0001
    z0 = 0
    xx, yy, zz = Chen(x0, y0, z0, a, b, c, T)
    ax = plt.subplot(122, projection="3d")
    ax.scatter(xx, yy, zz, s=5)
    ax.set_xlabel('x(t)')
    ax.set_ylabel('y(t)')
    ax.set_zlabel('z(t)')
    ax.set_title('x0={0} y0={1} z0={2}'.format(x0, y0, z0))
    ax.grid(False)
    plt.show()

    t = np.arange(0, T)

    plt.scatter(t, x, s=1)
    plt.scatter(t, xx, s=1)
    plt.xlabel('Iteration')  # 添加x轴标签
    plt.ylabel('x(t) Value')  # 添加y轴标签
    plt.show()


if __name__ == '__main__':
    main()

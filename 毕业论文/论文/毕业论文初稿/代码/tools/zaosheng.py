import numpy as np
import cv2


def add_salt_and_pepper_noise(image, noise_ratio):
    """
    向图像添加椒盐噪声。

    参数：
    - image: 输入图像（numpy数组）。
    - noise_ratio: 噪声比例，取值范围为0到1，表示图像中被噪声替换的像素比例。

    返回：
    - 添加噪声后的图像。
    """
    # 创建一个与输入图像相同形状的随机数矩阵
    random_matrix = np.random.rand(*image.shape)

    # 创建一个副本以避免修改原始图像
    noisy_image = image.copy()

    # 将随机矩阵中小于噪声比例的元素设置为0（椒噪声）
    noisy_image[random_matrix < noise_ratio / 2] = 0

    # 将随机矩阵中大于1 - 噪声比例的元素设置为255（盐噪声）
    noisy_image[random_matrix > 1 - noise_ratio / 2] = 255

    return noisy_image


# 读取原始图像
image = cv2.imread("lena_new.png", cv2.IMREAD_GRAYSCALE)

# 设置噪声比例，例如0.05表示5%的噪声
noise_ratio = 1


# 添加椒盐噪声
noisy_image = add_salt_and_pepper_noise(image, noise_ratio)

# 显示原始图像和添加噪声后的图像
cv2.imshow('Original Image', image)
cv2.imshow('Noisy Image', noisy_image)
cv2.imwrite("lena_zaosheng.png", noisy_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

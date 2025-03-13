import cv2
import numpy as np
import qrcode
from PIL import Image
import matplotlib.pyplot as plt

# Step 1: 读取二维码并转为一维数组


def decode_qrcode(image_path):
    # 使用 OpenCV 读取二维码图像
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # 二值化处理，确保图像是黑白的
    _, binary_img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)

    # 获取二维码图像的尺寸
    height, width = binary_img.shape

    # 将黑色为1，白色为0，转换成一维数组
    one_dimensional_array = []
    for i in range(height):
        for j in range(width):
            # 如果是黑色（像素值为0），就记录1，否则记录0
            one_dimensional_array.append(1 if binary_img[i, j] < 128 else 0)
        one_dimensional_array.append(0)
    for j in range(width+1):
        # 如果是黑色（像素值为0），就记录1，否则记录0
        one_dimensional_array.append(0)
    return one_dimensional_array, height+1, width+1

# 读取二维码生成一维数组


def decode_qrcodeEx(image_path):
  # 读取图像并检查有效性
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Image at {image_path} could not be loaded.")

    # 二值化处理
    _, binary_img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)

    # 转换为 0/1 一维数组（黑色为1，白色为0）
    one_dimensional_array = (binary_img == 0).astype(int).flatten().tolist()

    # 获取尺寸
    height, width = binary_img.shape

    # 将一维数组重塑为与图像相同尺寸的二维数组
    reshaped_array = np.array(one_dimensional_array).reshape((height, width))

    # 保存到文件
    output_file = "tes.txt"
    np.savetxt(output_file, reshaped_array,
               fmt='%d', delimiter=' ', newline='\n')

    return one_dimensional_array, height, width


def generate_qrcode_from_array(binary_array, height, width, output_path):
    # 将一维数组转成二维数组
    binary_2d_array = np.array(binary_array).reshape((height, width))

    # 将 0 映射为 255，1 映射为 0
    inverted_array = (binary_2d_array == 0).astype(np.uint8) * 255

    # 使用 numpy 数组生成一个新的二维码图像
    img = Image.fromarray(inverted_array)  # 黑白图像
    img.save(output_path)

    # # 展示二维码图像
    # plt.imshow(img, cmap='gray')
    # plt.axis('off')  # 不显示坐标轴
    # plt.show()

# 主程序


def main():
    # 读取二维码并转为一维数组
    image_path = r"C:\Users\lenovo\Desktop\coding\note\NoteForCoding\test\ceshi280.png"  # 输入二维码文件路径
    binary_array, height, width = decode_qrcodeEx(image_path)

    # 根据一维数组生成二维码并展示
    output_path = '测试水印out.png'  # 输出二维码文件路径
    generate_qrcode_from_array(binary_array, height, width, output_path)

    print(f'二维码转换并保存为: {output_path}')


def create_black_white_image(arr, n, output_path=None):
    # 将一维数组转换为二维数组
    if len(arr) != n * n:
        raise ValueError("输入数组的长度必须为 n * n")

    # 创建一个白色背景的 n x n 图像
    img = Image.new('1', (n, n), 1)  # '1' 是模式，代表黑白图像（0 为黑色，1 为白色）
    pixels = img.load()  # 获取图像的像素对象

    # 将数组值填充到图像上
    for i in range(n):
        for j in range(n):
            # 根据数组值设置像素（0 -> 白色, 1 -> 黑色）
            if arr[i * n + j] == 1:
                pixels[j, i] = 0  # 黑色

    # 展示图像
    # img.show()

    # 保存图像（如果需要）
    img.save(output_path)

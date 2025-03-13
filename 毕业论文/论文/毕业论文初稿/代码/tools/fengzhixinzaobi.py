import cv2

# 读取原始图像和处理后的图像
image1 = cv2.imread(
    "lena.png")
image2 = cv2.imread(
    "lena_new.png")


# 计算PSNR
psnr_value = cv2.PSNR(image1, image2)
print(f'PSNR值为：{psnr_value:.2f} dB')

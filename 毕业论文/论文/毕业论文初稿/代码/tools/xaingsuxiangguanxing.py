import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# 1. 加载图片并转换为灰度图
# 请确保图片文件在当前目录下或者指定正确的路径
image = Image.open(
    r"C:\Users\lenovo\Desktop\coding\note\NoteForCoding\test\jianqie\ceshi_kuosan.png").convert('L')
img_array = np.array(image)

# 2. 提取相邻像素数据
# 水平方向：每行中相邻像素（当前位置与右侧像素）
x_hor = img_array[:, :-1].flatten()
y_hor = img_array[:, 1:].flatten()

# 垂直方向：每列中相邻像素（当前位置与下方像素）
x_ver = img_array[:-1, :].flatten()
y_ver = img_array[1:, :].flatten()

# 对角方向：每个像素与其右下方像素
x_diag = img_array[:-1, :-1].flatten()
y_diag = img_array[1:, 1:].flatten()

# 3. 计算相关系数
corr_hor = np.corrcoef(x_hor, y_hor)[0, 1]
corr_ver = np.corrcoef(x_ver, y_ver)[0, 1]
corr_diag = np.corrcoef(x_diag, y_diag)[0, 1]

# 4. 绘制散点图
plt.figure(figsize=(15, 5))

# 水平相关性图
plt.subplot(1, 3, 1)
plt.scatter(x_hor, y_hor, s=0.5, alpha=0.5)
plt.title(f"水平相关性: {corr_hor:.2f}")
plt.xlabel("像素值")
plt.ylabel("右侧像素值")

# 垂直相关性图
plt.subplot(1, 3, 2)
plt.scatter(x_ver, y_ver, s=0.5, alpha=0.5)
plt.title(f"垂直相关性: {corr_ver:.2f}")
plt.xlabel("像素值")
plt.ylabel("下方像素值")

# 对角相关性图
plt.subplot(1, 3, 3)
plt.scatter(x_diag, y_diag, s=0.5, alpha=0.5)
plt.title(f"对角相关性: {corr_diag:.2f}")
plt.xlabel("像素值")
plt.ylabel("右下方像素值")

plt.tight_layout()

# 5. 保存并展示结果
plt.savefig(
    r"C:\Users\lenovo\Desktop\coding\note\NoteForCoding\test\jianqie\xiangsuxiangguanxing\ceshi.png")
plt.show()

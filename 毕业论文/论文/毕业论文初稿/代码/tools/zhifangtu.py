import cv2
import matplotlib.pyplot as plt
import numpy as np

# 读取二值图像（确保路径正确）
input_path = r"C:\Users\lenovo\Desktop\coding\note\NoteForCoding\test\jianqie\erweima_kuosan.png"  # 替换为实际路径
# 强制灰度读取‌:ml-citation{ref="1,4" data="citationList"}
img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

# 计算像素分布
pixels = img.ravel()  # 展平为一维数组‌:ml-citation{ref="1,3" data="citationList"}

# 绘制直方图
plt.figure(figsize=(8, 5), dpi=100)
plt.hist(pixels,
         bins=2,  # 仅分0和255两个区间‌:ml-citation{ref="2,4" data="citationList"}
         range=(0, 255),  # 覆盖全部像素值范围‌:ml-citation{ref="3" data="citationList"}
         color='dimgray',
         alpha=0.8,
         rwidth=0.7)  # 调整柱子宽度‌:ml-citation{ref="2,5" data="citationList"}

# 设置坐标轴
# 标记二值含义‌:ml-citation{ref="4" data="citationList"}
plt.xticks([0, 255], labels=['0 (Black)', '255 (White)'])
plt.xlabel("Pixel Value")
plt.ylabel("Frequency")
plt.title("Binary Image Histogram")

# 保存到指定路径
output_path = r"C:\Users\lenovo\Desktop\coding\note\NoteForCoding\test\jianqie\zhifangtu\erweima_kuosan.png"  # 替换为实际路径
# 紧凑布局‌:ml-citation{ref="3,5" data="citationList"}
plt.savefig(output_path, bbox_inches='tight', pad_inches=0.2)
plt.close()

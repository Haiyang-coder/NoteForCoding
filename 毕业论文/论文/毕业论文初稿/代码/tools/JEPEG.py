
import cv2


def compress_image_to_jpeg(input_path, output_path, quality=90):
    """
    将图片压缩为 JPEG 格式。

    参数：
    input_path (str): 输入图片路径。
    output_path (str): 输出压缩后的图片路径。
    quality (int): JPEG 压缩质量，范围 0-100，值越高质量越好。
    """
    img = cv2.imread(input_path)
    cv2.imwrite(output_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])

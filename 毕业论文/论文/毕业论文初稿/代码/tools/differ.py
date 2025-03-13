from PIL import Image


def compare_binary_images(img1_path, img2_path):
    """比较两张二值图片的像素差异"""
    try:
        # 打开图片并转换为灰度模式
        img1 = Image.open(img1_path).convert('L')
        img2 = Image.open(img2_path).convert('L')

        # 验证图片尺寸
        if img1.size != img2.size:
            raise ValueError("错误：图片尺寸不一致")

        width, height = img1.size
        pixels1 = img1.load()
        pixels2 = img2.load()

        diff_count = 0
        differences = []

        # 遍历每个像素
        for y in range(height):
            for x in range(width):
                p1 = pixels1[x, y]
                p2 = pixels2[x, y]
                if p1 != p2:
                    diff_count += 1
                    differences.append((x, y, p1, p2))

        # 输出结果

        if diff_count > 0:
            print("\n差异详情（格式：坐标 (x, y) | 图片1值 -> 图片2值）:")
            for diff in differences:
                print(
                    f"({diff[0]:>3}, {diff[1]:>3}) | {diff[2]:>3} -> {diff[3]:>3}")

        print(f"不同的像素总数：{diff_count}")

        return diff_count, differences

    except Exception as e:
        print(f"发生错误：{str(e)}")
        return None, None


# 使用示例
if __name__ == "__main__":
    # 替换为你的图片路径
    image1 = "newhash.png"
    image2 = "he.png"

    compare_binary_images(image1, image2)

import qrcode


def generate_fixed_size_qr_code(data,  file_path=None):
    """
    生成固定尺寸的二维码（例如 50x50 像素）。
    :param data: 二维码包含的数据（例如文本或URL）
    :param target_size: 目标图像的大小（单位：像素）
    :param border: 边框宽度（单位：模块）
    :param file_path: 保存二维码图像的路径（可选）
    :return: 二维码图像对象
    """
    # 计算二维码版本和 box_size 使得二维码最终大小接近目标尺寸
    # version=1 box_size=8 border=1大小是280
    version = 7  # 初始版本
    # 创建二维码对象
    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 容错率 L
        box_size=1,  # 每个模块的像素大小
        border=1  # 边框宽度（单位：模块）
    )

    # 添加数据
    qr.add_data(data)
    qr.make(fit=True)

    # 创建图像
    img = qr.make_image(fill='black', back_color='white')

    # 保存图像（如果需要）
    if file_path:
        img.save(file_path)

    return img

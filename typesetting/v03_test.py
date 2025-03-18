import os
import numpy as np
from PIL import Image
from rectpack import newPacker, PackingMode, PackingBin

# 容器参数配置
FABRIC_WIDTH_CM = 140  # 幅宽140厘米
TARGET_DPI = 300  # 生产标准DPI
CM_TO_INCH = 2.54  # 厘米转英寸系数


def load_images(folder_path):
    """
    加载并预处理所有透明PNG图片
    :return: 图片数据列表 (图像数组, 宽, 高)
    """
    images = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.png'):
            file_path = os.path.join(folder_path, filename)
            try:
                with Image.open(file_path) as img:
                    # 转换为RGBA模式并旋转
                    img = img.convert("RGBA").rotate(90, expand=True)

                    # 裁剪透明区域
                    non_alpha = np.array(img)[:, :, 3] > 10
                    if non_alpha.any():
                        coords = np.argwhere(non_alpha)
                        y0, x0 = coords.min(axis=0)
                        y1, x1 = coords.max(axis=0) + 1
                        img = img.crop((x0, y0, x1, y1))

                    # 转换为numpy数组
                    img_array = np.array(img)
                    images.append((img_array, img.width, img.height, filename))
                    print(f"Loaded: {filename} ({img.width}x{img.height})")

            except Exception as e:
                print(f"加载 {filename} 失败: {str(e)}")

    return images


from rectpack import newPacker, PackingMode


def create_layout(images):
    """
    修正后的排料函数
    """
    # 计算幅宽像素
    fabric_width = int(FABRIC_WIDTH_CM / CM_TO_INCH * TARGET_DPI)

    # 初始化排料器（关键修正点）
    packer = newPacker(
        mode=PackingMode.Offline,
        rotation=True,
        bin_algo='BLD_SSS',  # 改为字符串传参
        pack_algo='maxrects',  # 明确指定排料算法
        sort_algo='SORT_AREA'  # 按面积排序
    )

    # 添加容器（无限高度）
    packer.add_bin(fabric_width, 999999)

    # 添加所有图片
    for idx, (_, w, h, _) in enumerate(images):
        packer.add_rect(w, h, rid=idx)

    # 执行排料
    packer.pack()

    # 提取位置信息
    layout = []
    for rect in packer.rect_list():
        idx = rect.rid
        x, y = rect.x, rect.y
        rotated = rect.rotated
        layout.append((idx, x, y, rotated))

    return fabric_width, layout


def render_result(images, layout, fabric_width):
    """
    生成最终拼接图像
    """
    # 计算总高度
    max_y = max(y + h for _, (_, _, h, _), (x, y, _) in zip(range(len(layout)), images, layout))

    # 创建透明画布
    canvas = np.zeros((max_y, fabric_width, 4), dtype=np.uint8)

    # 按顺序贴图
    for idx, (img_array, w, h, name), (x, y, rotated) in zip(range(len(layout)), images, layout):
        if rotated:
            img_array = np.rot90(img_array, k=1)
            w, h = h, w

        # 确保在画布范围内
        if x + w > fabric_width or y + h > max_y:
            print(f"警告: {name} 超出画布范围")
            continue

        # 混合像素（保留透明度）
        alpha = img_array[:, :, 3:4].astype(float) / 255.0
        canvas[y:y + h, x:x + w, :3] = (1 - alpha) * canvas[y:y + h, x:x + w, :3] + alpha * img_array[:, :, :3]
        canvas[y:y + h, x:x + w, 3] = np.maximum(canvas[y:y + h, x:x + w, 3], img_array[:, :, 3])

        print(f"Placed: {name} at ({x},{y}) {'(rotated)' if rotated else ''}")

    # 转换为PIL图像并保存
    result_img = Image.fromarray(canvas, 'RGBA')
    result_img.save('final_layout.png', dpi=(TARGET_DPI, TARGET_DPI))
    print(f"\n拼接完成! 保存至 final_layout.png")


if __name__ == "__main__":
    # 加载图片
    image_folder = "gender_png"
    images = load_images(image_folder)

    # 计算排料方案
    fabric_width, layout = create_layout(images)

    # 生成结果图像
    render_result(images, layout, fabric_width)
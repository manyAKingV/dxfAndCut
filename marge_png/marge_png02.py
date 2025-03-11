from PIL import Image, ImageOps, ImageDraw
import numpy as np


def overlay_images(img1_path, small_images_info, output_path):
    try:
        # 打开图一
        img1 = Image.open(img1_path).convert("RGBA")
        img1_array = np.array(img1)

        for info in small_images_info:
            small_img_path = info["path"]
            position = info["position"]
            size = info["size"]
            scale = info["scale"]
            rotation = info["rotation"]
            opacity = info["opacity"]

            # 打开小图片
            small_img = Image.open(small_img_path).convert("RGBA")

            # 调整小图片大小
            new_size = (int(size[0] * scale), int(size[1] * scale))
            small_img = small_img.resize(new_size, Image.Resampling.LANCZOS)

            # 旋转小图片
            small_img = small_img.rotate(rotation, expand=True)

            # 调整透明度
            r, g, b, a = small_img.split()
            a = a.point(lambda p: p * opacity)
            small_img = Image.merge("RGBA", (r, g, b, a))

            small_img_array = np.array(small_img)

            # 计算小图片在大图上的放置区域
            x, y = position
            x_end = x + small_img_array.shape[1]
            y_end = y + small_img_array.shape[0]

            # 确保放置区域在大图范围内
            if x < 0 or y < 0 or x_end > img1_array.shape[1] or y_end > img1_array.shape[0]:
                continue

            # 提取大图上对应区域
            target_area = img1_array[y:y_end, x:x_end]

            # 找到大图像素值为透明或全黑的位置
            transparent_or_black = np.all(target_area[:, :, :3] == [0, 0, 0], axis=-1)

            # 在这些位置使用小图片的像素值
            target_area[transparent_or_black] = small_img_array[transparent_or_black]

            # 将修改后的区域放回大图
            img1_array[y:y_end, x:x_end] = target_area

        # 将结果数组转换回图片
        result_img = Image.fromarray(img1_array)

        # 保存结果图片
        result_img.save(output_path)
        print(f"图片已保存到 {output_path}")
    except FileNotFoundError:
        print("错误: 未找到指定的图片文件!")
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")


if __name__ == "__main__":
    img1_path = "image01.png"
    output_path = "output02.png"
    # TODO 读取图一的属性
    # 小图片信息示例
    small_images_info = [
        {
            "path": "small_image01.png",
            "position": (100, 100),
            "size": (200, 200),
            "scale": 1.5,
            "rotation": 30,
            "opacity": 0.8
        },
        {
            "path": "small_image02.png",
            "position": (300, 300),
            "size": (150, 150),
            "scale": 1.2,
            "rotation": -15,
            "opacity": 0.7
        }
    ]

    overlay_images(img1_path, small_images_info, output_path)

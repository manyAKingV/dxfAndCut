import os
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

# 幅宽 和 像素的转换
DPI = 200
FABRIC_WIDTH = 140 # 面料宽度
RESOLUTION = int(DPI * FABRIC_WIDTH / 2.54)  # 分辨率


# 放到空图上
# 形参：图片，边界点
# def calculate(image,borders,result,x_offset):
#     # 获取图片的宽度和高度
#     width, height = image.size
#     result.paste(image,(x_offset,0))
#     x_offset += image.width

def get_png_sizes():
    # 检查 create_png 目录是否存在
    if not os.path.exists('create_png'):
        print("create_png 目录不存在。")
        return

    # 设置边界点
    borders = []
    borders.append((0,0))
    borders.append((0,RESOLUTION))
    # 创建空白图片
    totle_width = 0
    x_offset = 0
    result = Image.new("RGBA", (totle_width,RESOLUTION))

    # 遍历 create_png 目录中的所有文件
    for filename in os.listdir('create_png'):
        if filename.endswith('.png'):
            # 构建文件的完整路径
            file_path = os.path.join('create_png', filename)
            try:
                # 打开图片文件
                with Image.open(file_path) as img:
                    # calculate(img,borders,result,x_offset)
                    width, height = img.size
                    result.paste(img, (x_offset, 0))
                    x_offset += img.width

            except Exception as e:
                print(f"读取文件 {filename} 时出现错误: {e}")

    result.save('output.png')
    print("succeed")


if __name__ == "__main__":
    get_png_sizes()

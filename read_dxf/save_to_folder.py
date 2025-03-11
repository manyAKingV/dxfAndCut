import matplotlib.pyplot as plt
import os

MARKER_SIZE = 0.1  # 点的大小
LINE_WIDTH = 0.5   # 线的宽度
LINE_COLOR = 'blue' # 线和点的颜色

def painting_line(points,name):
    plt.figure()

    x_coords = [point[0] for point in points]
    y_coords = [point[1] for point in points]
    # 绘制当前多段线
    plt.plot(x_coords, y_coords, marker='o', linestyle='-', markersize=MARKER_SIZE, linewidth=LINE_WIDTH,
             color=LINE_COLOR)

    plt.axis('equal')
    plt.axis('off')  # 不显示坐标系
    save_to_folder("create_png", name)
    plt.close()


# 保存到指定位置 目录位置，文件名
def save_to_folder(folder_path,file_name):
    # 若不存在则创建一个create_png
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 拼接完整文件路径
    output_png = os.path.join(folder_path,f"{file_name}.png")
    plt.savefig(output_png)

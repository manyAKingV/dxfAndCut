import dxfgrabber
import matplotlib.pyplot as plt


def polyline_to_png(dxf_file_path):
    try:
        # 读取 DXF 文件
        dxf = dxfgrabber.readfile(dxf_file_path)

        all_polylines = []
        # 遍历所有块
        for b in dxf.blocks:
            print(f"当前块名: {b.name}")
            # 遍历块中的实体
            for e in b._entities:
                if e.dxftype == "POLYLINE":
                    print(f"找到多段线，顶点坐标: {e.points}")
                    all_polylines.append(e)

        if not all_polylines:
            print("未找到多段线实体。")
            return


        # 设置点的大小、线的宽度和颜色
        marker_size = 0.1  # 点的大小
        line_width = 1  # 线的宽度
        line_color = 'blue'  # 线和点的颜色

        for i,polyline in enumerate(all_polylines):
            plt.figure()
            # 获取多段线的顶点
            points = []
            for vertex in polyline.vertices:
                points.append((vertex.location[0], vertex.location[1]))
            # 首尾相连
            points.append((polyline.vertices[0].location[0],polyline.vertices[0].location[1]))
            # 提取 x 和 y 坐标
            x_coords = [point[0] for point in points]
            y_coords = [point[1] for point in points]
            # 绘制当前多段线
            plt.plot(x_coords, y_coords, marker='o', linestyle='-',markersize=marker_size, linewidth=line_width, color=line_color)

            plt.axis('equal')
            # 保存为 PNG 图片
            output_png = f"polylines_{i}.png"
            plt.savefig(output_png)
            print(f"多段线已保存为 {output_png}")
            plt.close()

    except FileNotFoundError:
        print(f"错误：未找到 DXF 文件 {dxf_file_path}。")
    except Exception as e:
        print(f"发生未知错误：{e}")


# 使用示例
dxf_file = "7302626959761240064.dxf"
polyline_to_png(dxf_file)
import dxfgrabber
import re
import matplotlib.pyplot as plt
import os

MARKER_SIZE = 0.1  # 点的大小
LINE_WIDTH = 1     # 线的宽度
LINE_COLOR = 'black'  # 线和点的颜色
DPI = 72           # 图像分辨率


def transform_point(point, insert_x, insert_y, scale_x, scale_y):
    """应用INSERT变换到点坐标，去除旋转逻辑"""
    x_block, y_block = point
    # 缩放
    x_scaled = x_block * scale_x
    y_scaled = y_block * scale_y
    # 平移
    x_model = x_scaled + insert_x
    y_model = y_scaled + insert_y
    return (x_model, y_model)


def painting_line(lines, name):
    """绘制所有线段并保存为PNG"""
    if not lines:
        return  # 无数据不绘制

    # 收集所有点计算边界框
    all_points = [point for line in lines for point in line]
    x_coords = [p[0] for p in all_points]
    y_coords = [p[1] for p in all_points]
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)

    # 处理所有点重合的情况
    if max_x == min_x and max_y == min_y:
        min_x -= 0.5
        max_x += 0.5
        min_y -= 0.5
        max_y += 0.5
    elif max_x == min_x:
        expand = (max_y - min_y) * 0.1
        min_x -= expand
        max_x += expand
    elif max_y == min_y:
        expand = (max_x - min_x) * 0.1
        min_y -= expand
        max_y += expand

    # 设置图形大小和坐标轴
    fig_width = max(max_x - min_x, 1) * 0.6
    fig_height = max(max_y - min_y, 1) * 0.6
    length = max(fig_width,fig_height)
    plt.figure(figsize=(length, length), dpi=DPI)
    plt.xlim(min_x, max_x)
    plt.ylim(min_y, max_y)
    plt.axis('equal')
    plt.axis('off')

    # 绘制每个线段
    for line in lines:
        if not line:
            continue
        x = [p[0] for p in line]
        y = [p[1] for p in line]
        if len(line) == 1:
            plt.plot(x, y, 'o', markersize=MARKER_SIZE, color=LINE_COLOR)
        else:
            plt.plot(x, y, linewidth=LINE_WIDTH, color=LINE_COLOR)

    # 保存图像
    save_to_folder("create_png", name)
    plt.close()


def save_to_folder(folder_path, file_name):
    """保存图像到指定目录"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    output_png = os.path.join(folder_path, f"{file_name}.png")
    plt.savefig(output_png, dpi=DPI, bbox_inches='tight', pad_inches=0)


def process_entity(entity, insert_x, insert_y, scale_x, scale_y):
    """处理单个实体并返回变换后的线段列表，去除旋转逻辑"""
    lines = []

    if entity.dxftype in ['LWPOLYLINE', 'POLYLINE']:
        vertices = []
        # 处理多段线顶点
        points = getattr(entity, 'points', [])
        if not points and hasattr(entity, 'vertices'):
            points = [v.location[:2] for v in entity.vertices if v.dxftype == 'VERTEX']
        for pt in points:
            transformed = transform_point(pt[:2], insert_x, insert_y, scale_x, scale_y)
            vertices.append(transformed)
        # 闭合处理
        if getattr(entity, 'closed', False) and len(vertices) > 1:
            vertices.append(vertices[0])
        if vertices:
            lines.append(vertices)
    # 去掉中心线部分
    # elif entity.dxftype == 'LINE':
    #     start = transform_point(entity.start[:2], insert_x, insert_y, scale_x, scale_y)
    #     end = transform_point(entity.end[:2], insert_x, insert_y, scale_x, scale_y)
    #     lines.append([start, end])
    return lines


def polyline_to_png(dxf_file):
    """主函数：读取DXF并转换块为PNG"""
    try:
        dxf = dxfgrabber.readfile(dxf_file)
        for entity in dxf.entities:
            if entity.dxftype == 'INSERT' and entity.name in dxf.blocks:
                block = dxf.blocks[entity.name]
                # 获取INSERT变换参数
                insert_x, insert_y = entity.insert[0], entity.insert[1]
                scale_x = entity.scale[0] if hasattr(entity, 'scale') and len(entity.scale) > 0 else 1
                scale_y = entity.scale[1] if hasattr(entity, 'scale') and len(entity.scale) > 1 else 1
                # 处理块内所有实体
                all_lines = []
                for e in block._entities:
                    all_lines.extend(process_entity(e, insert_x, insert_y, scale_x, scale_y))
                # 过滤边界框块
                if not re.match(r'^BoundingBox_-\d+$', entity.name):
                    painting_line(all_lines, entity.name)
    except Exception as e:
        print(f"处理DXF文件时出错: {e}")


if __name__ == "__main__":
    dxf_file = "1741602961191.dxf"  # 修改为你的DXF文件路径
    polyline_to_png(dxf_file)
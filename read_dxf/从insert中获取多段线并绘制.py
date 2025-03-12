import dxfgrabber
import matplotlib.pyplot as plt
import os
import save_to_folder


# 设置点
def deal_line(polyline,name):
    print(f"开始绘制: {name}")
    # plt.figure()
    # 获取多段线的顶点
    points = []
    for e in polyline:
        if e.dxftype == "POLYLINE":
            points.extend(e.points)

    # TODO 去掉内部线
    # TODO 获取 裁片实际大小
    # 首尾相连
    points.append((points[0][0],points[0][1]))
    save_to_folder.painting_line(points,name)

def polyline_to_png(dxf_file):
    try:
        # 读取 DXF 文件
        dxf = dxfgrabber.readfile(dxf_file)

        # 遍历所有实体
        for i,entity in enumerate(dxf.entities):
            if entity.dxftype == 'INSERT':
                # 获取 INSERT 实体的属性
                block_name = entity.name
                print(f"块名: {block_name}")
                if block_name in dxf.blocks:
                    block = dxf.blocks[block_name]
                    print(f"找到块名: {block_name}")
                    deal_line(block._entities,block_name)
                print("-" * 30)

    except FileNotFoundError:
        print(f"错误：未找到 DXF 文件 {dxf_file}")
    except Exception as e:
        print(f"发生未知错误：{e}")


if __name__ == "__main__":
    dxf_file = "1741602961191.dxf"
    polyline_to_png(dxf_file)
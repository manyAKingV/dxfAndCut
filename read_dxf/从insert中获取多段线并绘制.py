import dxfgrabber
import save_to_folder
import re
# 目前dxf换算png v01版本

# 设置点
def deal_line(polyline,name):
    print(f"开始绘制: {name}")
    pattern = r'^BoundingBox_-\d+$'
    if re.match(pattern, name):
        return
    # plt.figure()
    # 获取多段线的顶点
    points = []
    for e in polyline:
         if e.dxftype == "POINT":
             point = [e.point[0], e.point[1]]
             points.append(point)

    # TODO 去掉内部线
    # 首尾相连
    points.append([points[0][0],points[0][1]])
    save_to_folder.painting_line(points,name)

    # for e in polyline:
    #     if e.dxftype == "POLYLINE":
    #         points.extend(e.points)
    #
    # # TODO 去掉内部线
    # # 首尾相连
    # points.append((points[0][0],points[0][1]))
    # save_to_folder.painting_line(points,name)

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
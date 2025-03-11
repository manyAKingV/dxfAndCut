import ezdxf

# 读取 DXF 文件
doc = ezdxf.readfile('../paint_dxf/line.dxf')

# 获取模型空间
msp = doc.modelspace()

# 遍历模型空间中的所有实体
for entity in msp:
    # 检查实体是否为直线
    if entity.dxftype() == 'LINE':
        # 获取直线的起点和终点坐标
        start_point = entity.dxf.start
        end_point = entity.dxf.end
        print(f"直线起点坐标: {start_point}")
        print(f"直线终点坐标: {end_point}")

import ezdxf

# 创建一个新的 DXF 文档，指定版本为 R2010
doc = ezdxf.new('R2010')

# 获取块定义管理器
blocks = doc.blocks

# 定义一个名为 'CIRCLE_BLOCK' 的块
circle_block = blocks.new(name='CIRCLE_BLOCK')

# 在块中添加一个圆形，圆心为 (0, 0)，半径为 5，颜色为红色（颜色代码 1 代表红色）
circle = circle_block.add_circle(center=(0, 0), radius=5)
circle.dxf.color = 1

# 在圆心添加一个点，颜色为蓝色（颜色代码 5 代表蓝色）
center_point = circle_block.add_point((0, 0))
center_point.dxf.color = 5

# 获取模型空间
msp = doc.modelspace()

# 在模型空间中插入 'CIRCLE_BLOCK' 块，插入点为 (10, 10)
msp.add_blockref('CIRCLE_BLOCK', insert=(10, 10))

# 保存 DXF 文件
doc.saveas('circle_block.dxf')

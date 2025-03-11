import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt

# 读取 DXF 文件
# doc = ezdxf.readfile('test01.dxf')
doc = ezdxf.readfile('../paint_dxf/circle_block.dxf')

# 获取模型空间
msp = doc.modelspace()

# 创建渲染上下文
context = RenderContext(doc)

# 创建 matplotlib 图形和坐标轴
fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1])
ax.set_axis_off()

# 创建 matplotlib 后端
out = MatplotlibBackend(ax)

# 渲染模型空间
Frontend(context, out).draw_layout(msp)

# 保存为 PNG 文件
fig.savefig('circle_block.png', dpi=300)

# 关闭图形
plt.close(fig)

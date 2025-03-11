import ezdxf
import matplotlib.pyplot as plt
from ezdxf.addons.iterdxf import modelspace
from matplotlib.patches import Circle


# read dxf file
doc = ezdxf.readfile("test01.dxf")
# read model space
msp = doc.modelspace()

blocks = doc.blocks

# 遍历模型空间中的所有Insert实体
for entity in msp.query('INSERT'):
    if isinstance(entity, ezdxf.entities.Insert):
        print(f"块参照名称: {entity.dxf.name}")
        print(f"插入点: {entity.dxf.insert}")
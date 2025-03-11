import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt
import ezdxf.math


# 自定义处理厚度和拉伸方向的函数
def custom_transform_thickness_and_extrusion_without_ocs(entity, m):
    from ezdxf.math import Vec3
    if hasattr(entity.dxf, 'thickness'):
        thickness = Vec3.from_any(entity.dxf.thickness)
        if thickness.magnitude > 1e-12:  # 检查向量长度是否接近零
            thickness = thickness.normalize()
            entity.dxf.thickness = thickness
    if hasattr(entity.dxf, 'extrusion'):
        extrusion = Vec3.from_any(entity.dxf.extrusion)
        if extrusion.magnitude > 1e-12:  # 检查向量长度是否接近零
            extrusion = extrusion.normalize()
            entity.dxf.extrusion = extrusion
    return entity


# 替换原始的处理函数
ezdxf.math.transform_thickness_and_extrusion_without_ocs = custom_transform_thickness_and_extrusion_without_ocs


def convert_dxf_to_png(dxf_file_path, png_file_path, dpi=300):
    try:
        # 读取 DXF 文件
        doc = ezdxf.readfile(dxf_file_path)

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
        fig.savefig(png_file_path, dpi=dpi)

        # 关闭图形
        plt.close(fig)

        print(f"成功将 {dxf_file_path} 转换为 {png_file_path}")
    except Exception as e:
        print(f"转换过程中出现错误: {e}")


if __name__ == "__main__":
    # 替换为你的 DXF 文件路径
    dxf_file = "test02.dxf"
    # 替换为你想要保存的 PNG 文件路径
    png_file = "output.png"
    convert_dxf_to_png(dxf_file, png_file)

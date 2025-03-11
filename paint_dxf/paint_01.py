import ezdxf

doc = ezdxf.new('R2010')

msp = doc.modelspace()
msp.add_line((0, 0), (10, 10))
doc.saveas('line.dxf')

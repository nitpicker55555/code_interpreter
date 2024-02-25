import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

font = FontProperties(fname=r"C:\Windows\Fonts\msyh.ttc", size=14)  # 以微软雅黑为例

plt.plot([1, 2, 3], [4, 5, 6])
plt.title('示例图表', fontproperties=font)
plt.xlabel('X轴', fontproperties=font)
plt.ylabel('Y轴', fontproperties=font)
plt.show()

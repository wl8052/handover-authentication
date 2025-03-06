import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline

# 生成随机节点
num_nodes = 1000
x = np.random.uniform(0, 15, num_nodes)
y = np.random.uniform(0, 15, num_nodes)

# 定义起点、中间点和终点
points = [(2, 2), (5, 8), (8, 4), (10, 10), (13, 12)]

# 使用三次样条插值生成连续曲线路径
t = np.linspace(0, 1, num_nodes)
x_interp = CubicSpline([i/4 for i in range(len(points))], [point[0] for point in points], bc_type='clamped')(t)
y_interp = CubicSpline([i/4 for i in range(len(points))], [point[1] for point in points], bc_type='clamped')(t)

# 绘制节点和连续曲线路径
plt.scatter(x, y, color='b', marker='o', label='Nodes')
plt.plot(x_interp, y_interp, color='r', label='Continuous Path')

# 设置图像属性
plt.title('Continuous Path with Defined Points')
plt.xlabel('X')
plt.ylabel('Y')
plt.xlim(0, 15)
plt.ylim(0, 15)
plt.legend()
plt.grid(True)

# 模拟小车行驶
num_samples = 20
sample_indices = np.linspace(0, len(x_interp) - 1, num_samples, dtype=int)
for idx in sample_indices:
    plt.plot(x_interp[idx], y_interp[idx], 'go')

# 保存图像
plt.savefig('continuous_path_defined_points_with_MT.png')
plt.show()

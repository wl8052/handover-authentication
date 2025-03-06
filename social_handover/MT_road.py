import numpy as np
from scipy.interpolate import CubicSpline

# 定义路径的起点、中间点和终点
points = [(2, 2), (5, 8), (8, 4), (10, 10), (13, 12)]

# 使用三次样条插值生成连续曲线路径
t = np.linspace(0, 1, len(points))
x_interp = CubicSpline(t, [point[0] for point in points], bc_type='clamped')
y_interp = CubicSpline(t, [point[1] for point in points], bc_type='clamped')

# 计算路径的总长度（通过采样点之间的距离之和来近似）
total_length = 0
for i in range(1, len(points)):
    total_length += np.sqrt((points[i][0] - points[i - 1][0]) ** 2 + (points[i][1] - points[i - 1][1]) ** 2)

# 假设小车的速度是1单位长度每秒
MT_speed = 1  # 单位长度/秒


# 在特定时间 t_sec 下找到MT的位置
def car_position_at_time(t_sec):
    # 计算MT在路径上所经过的距离
    distance_covered = t_sec * MT_speed

    # 找到对应的路径上的位置
    cumulative_distance = 0
    for i in range(1, len(points)):
        segment_length = np.sqrt((points[i][0] - points[i - 1][0]) ** 2 + (points[i][1] - points[i - 1][1]) ** 2)
        cumulative_distance += segment_length
        if cumulative_distance >= distance_covered:
            t_segment = t[i - 1] + ((distance_covered - (cumulative_distance - segment_length)) / segment_length) * (
                        t[i] - t[i - 1])
            x_position = x_interp(t_segment)
            y_position = y_interp(t_segment)
            return x_position, y_position

    # 如果超出路径总长度，则返回终点位置
    return points[-1]


# # 在特定时间下找到MT的位置
# t_seconds = 10  # 秒
# MT_x, MT_y = car_position_at_time(t_seconds)
# print(f"At time {t_seconds} seconds, the car's position is ({MT_x}, {MT_y})")

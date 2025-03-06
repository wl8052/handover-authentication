# 运行该主文件前，需先运行blockchain.py和create_result.py

import math
import os
import openpyxl
import requests

from def_name import find_start_nodes, computing_trust, find_target_node, find_coordinates_by_node_name
from social_handover.MT_road import car_position_at_time
from social_handover.updata_relationship import update_interactions
# 认证时间（秒）一般情况下的认证时间
AUTHENTICATION_TIME = 0.5

handover_count = []         # 切换次数
authentication_count = []   # 认证次数


# 执行一次的切换次数和认证次数
def One_This_program(interactions):
    # (2,2)是路径的起点，以此找到第一个ES节点
    start_node = find_start_nodes(2, 2,interactions)
    t_seconds = 0.1
    # 初始连接ES的x和y
    start_x, start_y = find_coordinates_by_node_name(start_node)
    print(start_node, start_x, start_y)
    need_count = 0
    total_count = 0
    while True:
        # 移动终端的x和y
        MT_x, MT_y = car_position_at_time(t_seconds)
        # print(MT_x, MT_y)
        # 移动终端和当前连接点距离超0.7时执行找下一跳
        if math.sqrt((start_x - MT_x)**2 + (start_y - MT_y) ** 2) > 0.7:
            # 下一跳节点
            next_node, t_seconds = find_target_node(start_node, t_seconds,interactions)
            # 计算切换ES之间信任并输出切换总数和需切换次数
            need_count, total_count = computing_trust(start_node, next_node,need_count,total_count,interactions)
            print('认证次数:'+str(need_count), '切换次数:'+str(total_count))
            start_node = next_node
            next_x, next_y = find_coordinates_by_node_name(next_node)  # 下一个ES的x和y
            # 为下个循环的当前连接节点赋值
            start_x, start_y = next_x, next_y
            if math.sqrt((13 - next_x)**2 + (12 - next_y) ** 2) < 1:
                return total_count, need_count
        # 移动终端行驶的时间匀速递增
        t_seconds += 0.1
        print('时间推移:{:.2f}'.format(t_seconds))


# 记录切换和认证次数到数组中
def Record_count():
    for i in range(1, 31):
        interactions = requests.get(
            'http://localhost:5000/interactions').json()  # 节点社交关系[{"interaction_time":,"node1":,"node2":}]
        handover, authentication = One_This_program(interactions)
        update_interactions()
        # 将切换次数添加到列表中
        handover_count.append(handover)
        # 将认证次数添加到列表中
        authentication_count.append(authentication)
    return handover_count, authentication_count


def insert_data_into_XLSX(file_path, row_data):
    # 打开或创建 handover_times.xlsx 文件
    if os.path.exists(file_path):
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["user_num", "SREHA", "Tradition", "One_time", "Assist_program"])

    # 写入数据
    ws.append(row_data)

    # 保存 Excel 文件
    wb.save(file_path)

# 认证次数
handover_count, authentication_count = Record_count()
print(handover_count)
print(authentication_count)
total_count1 = 0  # 初始化总切换次数
need_count1 = 0  # 初始化总认证次数
for i in range(2,31,2):
    total_count1 += handover_count[i-2]+handover_count[i-1]
    need_count1 += authentication_count[i-2]+authentication_count[i-1]
    if i % 2 == 0:
        print(total_count1,need_count1)
        # 本文方案，认证次数+初次连接
        SREHA = need_count1 + i
        # 传统的切换方案，每次都要认证，切换次数+初次连接
        Tradition = total_count1 + i
        # 一次认证，后续就不需要认证了
        One_time = i
        # 辅助认证方案，每次都认证，但可以减少单次认证时间
        Assist_program = total_count1 + i
        # 插入到handover_times.xlsx表中
        data1 = [i, SREHA, Tradition, One_time,
                 Assist_program]  # 格式：[user_num, SREHA, Tradition, One_time, Assist_program]
        handover_times_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "handover_times.xlsx")
        insert_data_into_XLSX(handover_times_file, data1)

        # 认证时间
        # 本文方案，认证次数+初次连接
        SREHA_time = (need_count1 + i) * AUTHENTICATION_TIME
        # 传统的切换方案，每次都要认证，切换次数+初次连接
        Tradition_time = (total_count1 + i) * AUTHENTICATION_TIME
        # 一次认证，后续就不需要认证了
        One_time_time = i * AUTHENTICATION_TIME
        # 辅助认证方案，每次都认证，但可以减少单次认证时间比例为0.7,首次的不变
        Assist_program_time = total_count1 * AUTHENTICATION_TIME * 0.7 + i * AUTHENTICATION_TIME

        # Authentication_latency.xlsx表中
        data2 = [i, SREHA_time, Tradition_time, One_time_time,
                 Assist_program_time]  # 格式：[user_num, SREHA, Tradition, One_time, Assist_program]
        handover_times_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Authentication_latency.xlsx")
        insert_data_into_XLSX(handover_times_file, data2)



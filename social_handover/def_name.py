# 在这里写一各种调用的函数
import math
from datetime import datetime, timedelta
import random

from blockchain import Blockchain
import requests
from MT_road import car_position_at_time
blockchain = Blockchain()

nodes = requests.get('http://localhost:5000/nodes').json()  # 节点坐标的数据[{node_name: ,x: ,y: }]
# interactions = requests.get('http://localhost:5000/interactions').json()   # 节点社交关系[{"interaction_time":,"node1":,"node2":}]

def calculate_distance(node1, node2):
    return math.sqrt((node1['x'] - node2['x'])**2 + (node1['y'] - node2['y'])**2)


# 距离为1到2的两个节点，最后返回candidate
def node_candidate():

    candidate = []
    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            distance = calculate_distance(nodes[i], nodes[j])
            if 1 < distance < 2:
                mid_value = {'node1': nodes[i]['node_name'], 'node2': nodes[j]['node_name'], 'distance': distance}      # 中间部分
                candidate.append(mid_value)
    return candidate    # 返回距离为1到2的两个节点，以及他们之间的距离

# # 调用并打印
# candidate = node_candidate()
# print(candidate)


# 一个节点维护的社交关系，存着节点社交数量和3天内认证的社交数量
def relationship_times(interactions):
    # interactions = requests.get('http://localhost:5000/interactions').json()
    current_time = datetime.now()
    # 创建一个字典，用于存储每个节点对应的最近交互时间
    latest_interactions = {}

    # 遍历交互数据，更新每个节点对应的最近交互时间
    for interaction in interactions:
        node1 = interaction['node1']
        node2 = interaction['node2']
        interaction_time = datetime.strptime(interaction['interaction_time'], '%Y-%m-%d %H:%M:%S')

        # 如果该节点对之前没有记录，或者当前交互时间更近，则更新最近交互时间
        if (node1, node2) not in latest_interactions or interaction_time > latest_interactions[(node1, node2)]:
            latest_interactions[(node1, node2)] = interaction_time

    # 从交互数据中仅保留距离当前时间更近的记录
    filtered_interactions = [interaction for interaction in interactions if
                             datetime.strptime(interaction['interaction_time'], '%Y-%m-%d %H:%M:%S') ==
                             latest_interactions[
                                 (interaction['node1'], interaction['node2'])]]


# 保存关系
    node_interactions = {}

    for interaction in filtered_interactions:
        node1 = interaction['node1']
        node2 = interaction['node2']
        interaction_time = datetime.strptime(interaction['interaction_time'], '%Y-%m-%d %H:%M:%S')

        if node1 not in node_interactions:
            node_interactions[node1] = {'times': 0, 'times3': 0}
        node_interactions[node1]['times'] += 1

        if node2 not in node_interactions:
            node_interactions[node2] = {'times': 0, 'times3': 0}
        node_interactions[node2]['times'] += 1

        if current_time - interaction_time <= timedelta(days=3):
            node_interactions[node1]['times3'] += 1
            node_interactions[node2]['times3'] += 1

    nodes_data = [{'node_name': node, 'times': data['times'], 'times3': data['times3']} for node, data in node_interactions.items()]
    return nodes_data

# 调用函数并打印节点数据
# nodes_data = relationship_times()
# for node_data in nodes_data:
#     print(node_data)

# 获取两个节点的重合节点数量
def get_common_contacts(node1, node2,interactions):

    # 创建两个集合，分别存储与节点1和节点2交互的节点
    node1_interactions = set()
    node2_interactions = set()

    # 遍历所有交互记录
    for data in interactions:
        # 如果节点1参与了交互，则将另一个节点加入到节点1的交互集合中
        if data['node1'] == node1:
            node1_interactions.add(data['node2'])
        # 如果节点2参与了交互，则将另一个节点加入到节点2的交互集合中
        elif data['node1'] == node2:
            node2_interactions.add(data['node2'])
        elif data['node2'] == node1:
            node1_interactions.add(data['node1'])
        elif data['node2'] == node2:
            node2_interactions.add(data['node1'])

    # 计算两个交互集合的交集大小
    shared_interactions_count = len(node1_interactions.intersection(node2_interactions))
    return shared_interactions_count

# a = get_common_contacts(980,998)  # 测试
# print(a)


# 查询节点距现在服务时间和社交次数，要输入节点名，并计算节点本身的信誉度，返回自身信誉度
def node_trust(node_name,interactions):
    nodes_data = relationship_times(interactions)
    for node_data in nodes_data:
        if node_data['node_name'] == node_name:
            k = node_data['times3'] / node_data['times']
            node_history_trust = 2 * k
            if node_history_trust > 1:
                node_history_trust = 1
            return node_history_trust
        # 如果找不到对应的node_name，返回0
    return 0
# a = node_trust(795)     # 测试
# print(a)


# 计算信任，判断要不要认证，返回需要认证次数和切换次数
def computing_trust(node1, node2,need_count,total_count,interactions):
    try:
        # 重合节点的数量
        common_count = get_common_contacts(node1, node2,interactions)
        print('重合数量：{}'.format(common_count))
        k = 0.2 * common_count
        t1 = node_trust(node1,interactions)
        t2 = node_trust(node2,interactions)
        M1 = 0.7 * k + 0.3 * t1     # 2对1的信任
        M1 = round(M1, 2)
        M2 = 0.7 * k + 0.3 * t2     # 1对2的信任
        M2 = round(M2, 2)
        print('两ES之间信任:', '\n', str(M1), str(M2))
        total_count += 1
        if M1 > 0.7 and M2 > 0.7:
            # print("本次不需要认证")
            return need_count, total_count
        else:
            need_count += 1
            return need_count, total_count

    except Exception as e:
        print(f"获取通信重合节点时出现错误：{e}")

def computing_1_to_2(node1, node2,interactions):
    try:
        common_count = get_common_contacts(node1, node2,interactions)       # 重合节点的数量
        # print(common_count+1)
        k = 0.2 * common_count
        t2 = node_trust(node2,interactions)
        M2 = 0.7 * k + 0.3 * t2     # 1对2的信任
        # print(M1, M2)
        return round(M2, 2)

    except Exception as e:
        print(f"获取通信重合节点时出现错误：{e}")


# 找到起始节点
def find_start_nodes(x, y,interactions):
    distances = []  # 存储节点到目标点的距离

    # 计算每个节点到目标点的距离，并存储为元组 (距离, 节点名称, 信任度)
    for node in nodes:
        node_x = node['x']
        node_y = node['y']
        distance = math.sqrt((x - node_x) ** 2 + (y - node_y) ** 2)
        if distance > 1:
            continue
        trust = node_trust(node,interactions)
        distances.append((distance, node['node_name'], trust))

    # 根据距离对节点进行排序
    distances.sort()

    # 提取距离最近的三个节点名称
    nearest_nodes = [node[1] for node in distances[:3]]

    # # 从最近的三个节点中找到信任度最高的节点名称
    # selected_node = max(distances[:3], key=lambda x: x[2])[1]

    # 从最近的三个节点中随机选择一个节点
    selected_node = random.choice(nearest_nodes)

    return selected_node  # 输出信任度最高的节点名称


# 找到指定node_name的x和y
def find_coordinates_by_node_name(node_name):
    for item in nodes:
        if item['node_name'] == node_name:
            return item['x'], item['y']
    return None, None


# 找到下一跳节点
def find_target_node(node_name, t_seconds,interactions):
    # 如果车与当前连接的节点之间的距离超过0.7，则将下一个位置设置为当前位置加上1秒后的位置,将来的位置
    t_seconds += 1
    next_x, next_y = car_position_at_time(t_seconds + 1)
    print('移动终端位置:{:.2f}  {:.2f}'.format(next_x, next_y))

    # print('移动终端位置:{}',str(next_x), str(next_y))

    # 计算车子位置移动后与每个节点的距离，并计算信任度
    L_nodes = []
    distances_trust = []

    for node in nodes:
        node_x = node['x']
        node_y = node['y']
        start_x, start_y = find_coordinates_by_node_name(node_name)
        # 当前ES和下一跳ES的距离
        distance_L = math.sqrt((start_x - node_x) ** 2 + (start_y - node_y) ** 2)
        L = round(distance_L, 2)
        # 使得两个ES的距离区间在合理的范围内
        if L > 1.7 or L < 1:
            continue
        # 距离当前ES 1.7的候选下一跳ESs
        L_nodes.append({'node_name':node['node_name'], 'x':node_x, 'y':node_y,'L':L})
    print('待选ES阶段一：\n {}'.format(L_nodes))

    for node in L_nodes:
        node_x = node['x']
        node_y = node['y']
        # 寻找MT周围的ES，判断距离
        distance = math.sqrt((next_x - node_x) ** 2 + (next_y - node_y) ** 2)
        if distance > 1:
            continue
        trust = computing_1_to_2(node_name, node['node_name'], interactions)    # 当前ES对待选ES的信任
        distances_trust.append((round(distance, 2), trust, node['node_name']))
    if distances_trust == []:
        # 可能超过了距离，MT回退
        t_seconds -= 0.5
        next_x, next_y = car_position_at_time(t_seconds)
        for node in L_nodes:
            node_x = node['x']
            node_y = node['y']
            # 移动终端和下一跳ES的距离
            distance = math.sqrt((next_x - node_x) ** 2 + (next_y - node_y) ** 2)
            if distance > 1:
                continue
            trust = computing_1_to_2(node_name, node['node_name'], interactions)
            distances_trust.append((round(distance, 2), trust, node['node_name']))  # 距离，信任，名称

    print('下一个es和终端：\n {}'.format(distances_trust))

    # 找到上面筛选结果中距离最近的四个节点
    nearest_nodes = sorted(distances_trust)[:4]
    print('待选节点阶段二: \n {}'.format(nearest_nodes))
    # 对待选ES进行信任排序
    sorted_nodes = sorted(nearest_nodes, key=lambda x: x[1])
    if len(sorted_nodes) == 1:
        next_node = sorted_nodes[-1][2]
    else:
    # 考虑到性能，找最大的两个作为待选，三分之二的概率选信任最高的点，三分之一的概率选另一个
        if random.random() < 2 / 3:
            next_node = sorted_nodes[-1][2]
        else:
            next_node = sorted_nodes[-2][2]

    # max_value = [node[2] for node in sorted_nodes[-2:]]     # 考虑到性能，找最大的两个作为待选
    # next_node = random.choice(max_value)        # 对待选ES随机选择
    ### 从距离最近的四个节点中找到具有最大信任度的节点名称（放弃这种方式，可能对堵塞）
    # next_node = max(nearest_nodes, key=lambda x: x[1])[2]
    print('选中的下一跳ES: \n {}'.format(next_node))
    start_x, start_y = find_coordinates_by_node_name(node_name)
    nex_x, nex_y = find_coordinates_by_node_name(next_node)
    L = math.sqrt((start_x - nex_x) ** 2 + (start_y - nex_y) ** 2)
    # 取两位小数
    L_rounded = round(L, 2)
    print('两ES距离: \n {}'.format(L_rounded))

    # 输出下一跳名称
    return next_node, t_seconds


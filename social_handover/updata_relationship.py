import requests
from datetime import datetime, timedelta
import time


# def update_interactions():
#     interactions = requests.get('http://localhost:5000/interactions').json()
#     while True:
#
#         i = 0
#         for interaction in interactions:
#             interaction_date = datetime.strptime(interaction['interaction_time'], '%Y-%m-%d %H:%M:%S')
#             if datetime.now() - interaction_date > timedelta(days=5):
#                 i += 1
#                 interaction['interaction_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#                 requests.post('http://localhost:5000/new_transaction', json=interaction)
#                 print("更新第{}个".format(i))
#         time.sleep(60*60*24)  # 每天检查一次
#
#
# if __name__ == "__main__":
#     update_interactions()


def update_interactions():
    interactions = requests.get('http://localhost:5000/interactions').json()
    interactions_to_update = []

    for interaction in interactions:
        interaction_date = datetime.strptime(interaction['interaction_time'], '%Y-%m-%d %H:%M:%S')
        if datetime.now() - interaction_date > timedelta(days=5):
            interaction['interaction_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            interactions_to_update.append(interaction)

    if interactions_to_update:
        requests.post('http://localhost:5000/new_transaction', json=interactions_to_update)
        print("共更新{}个交互记录".format(len(interactions_to_update)))
    else:
        print("没有需要更新的交互记录")


# if __name__ == "__main__":
#     while True:
#         update_interactions()
#         time.sleep(60*60*24)  # 每天检查一次

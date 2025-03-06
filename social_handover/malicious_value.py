import random


# 计算出不同象限内有效时间内比例的差距，最后计算得出为24.89%左右
# 定义适应度函数
def fitness_function(threshold, data):
    malicious_nodes = sum(1 for d in data if d > threshold)
    fitness_value = malicious_nodes / len(data)
    return fitness_value


# 定义遗传算法函数
def genetic_algorithm(data, population_size=50, num_generations=100, mutation_rate=0.01):
    # 初始化种群
    population = [random.uniform(0, 0.8) for _ in range(population_size)]

    for generation in range(num_generations):
        # 计算适应度值
        fitness_values = [fitness_function(threshold, data) for threshold in population]

        # 选择优秀个体
        selected_population = []
        for _ in range(population_size):
            parent1 = random.choices(population, weights=fitness_values)[0]
            parent2 = random.choices(population, weights=fitness_values)[0]
            selected_population.append((parent1 + parent2) / 2)

        # 变异操作
        mutated_population = []
        for threshold in selected_population:
            if random.random() < mutation_rate:
                mutated_population.append(random.uniform(0, 0.8))
            else:
                mutated_population.append(threshold)

        population = mutated_population

    # 返回最佳阈值
    best_threshold = max(population, key=lambda threshold: fitness_function(threshold, data))
    return best_threshold


# 测试数据
data = [random.uniform(0, 0.8) for _ in range(100)]

# 使用遗传算法计算最佳阈值
best_threshold = genetic_algorithm(data)
print("最佳阈值：", best_threshold)

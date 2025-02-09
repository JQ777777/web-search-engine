import json
from collections import defaultdict, Counter
import numpy as np

# 加载数据
def load_data(file_path):
    print(f"正在从 {file_path} 加载数据...")
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    print("数据加载完成。")
    return data

# 保存数据
def save_data(file_path, data):
    print(f"正在将数据保存到 {file_path} ...")
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print("数据保存完成。")

# 构建图结构
def build_graph(data):
    print("正在构建图结构...")
    graph = defaultdict(list)
    url_to_index = {}
    index_to_url = {}
    
    for i, entry in enumerate(data):
        url = entry['url']
        url_to_index[url] = i
        index_to_url[i] = url
        for link in entry['links']:
            if link in url_to_index:
                graph[i].append(url_to_index[link])
    
    print("图结构构建完成。")
    return graph, url_to_index, index_to_url

# 初始化PageRank
def initialize_pagerank(data, initial_pr=0.3):
    print("正在初始化PageRank值...")
    N = len(data)
    pr = np.full(N, initial_pr)  # 初始化为给定的初始值
    if not np.all(np.isfinite(pr)):
        raise ValueError("初始PageRank值中包含无效数值 (NaN 或 Inf)")
    print("PageRank值初始化完成。")
    return pr

# 迭代计算PageRank
def compute_pagerank(graph, pr, d=0.85, epsilon=1e-6, max_iterations=100):
    print("开始PageRank计算...")
    N = len(pr)
    dangling_weights = np.full(N, 1/N)  # 悬空节点的权重分配
    out_degree = Counter()
    
    # 计算每个节点的出度
    for node, targets in graph.items():
        out_degree[node] = len(targets)
    
    # 获取所有悬空节点
    dangling_nodes = [node for node in range(N) if out_degree[node] == 0]
    
    for iteration in range(max_iterations):
        new_pr = (1 - d) / N * np.ones(N)  # 初始的随机跳转部分
        
        # 处理有出链的节点
        for node, targets in graph.items():
            if out_degree[node] > 0:
                new_pr[targets] += d * pr[node] / out_degree[node]
            else:  # 处理悬空节点
                new_pr += d * pr[node] * dangling_weights
        
        # 处理悬空节点的贡献
        if dangling_nodes:
            dangling_weight_sum = d * sum(pr[node] for node in dangling_nodes)
            new_pr += dangling_weight_sum * dangling_weights
        
        change = np.nan_to_num(np.abs(new_pr - pr).sum())
        pr = new_pr
        print(f"迭代 {iteration + 1}: 变化量 = {change}")
        
        if change < epsilon:
            print("已收敛。")
            break
    
    print("PageRank计算完成。")
    return pr

# 更新数据
def update_data_with_pagerank(data, pr, url_to_index):
    print("正在用新的PageRank值更新数据...")
    for entry in data:
        entry['pr'] = float(pr[url_to_index[entry['url']]])
    print("数据已用新的PageRank值更新。")
    return data

# 主函数
def main(input_file, output_file):
    try:
        # Step 1: Load the data
        data = load_data(input_file)
        
        # Step 2: Build the graph
        graph, url_to_index, index_to_url = build_graph(data)
        
        # Step 3: Initialize PageRank
        pr = initialize_pagerank(data)
        
        # Step 4: Compute PageRank
        pr = compute_pagerank(graph, pr)
        
        # Step 5: Update data with new PageRank values
        updated_data = update_data_with_pagerank(data, pr, url_to_index)
        
        # Save the updated data to a new file or overwrite the existing one
        save_data(output_file, updated_data)
        
        print("过程成功完成。")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == '__main__':
    input_file = 'nankai_data.json'  # 输入文件路径
    output_file = 'nankai_data_pagerank.json'  # 输出文件路径
    main(input_file, output_file)
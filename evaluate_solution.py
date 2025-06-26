import re
import os

def parse_solution_file(filepath):
    """解析solution文件，提取所有解"""
    solutions = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('obj:'):
            obj = float(line.split(':')[1])
            regret = float(lines[i+1].split(':')[1])
            sol_str = lines[i+2].split(':', 1)[1]
            # 解析边列表
            edges = eval(sol_str)
            solutions.append({
                'obj': obj,
                'regret': regret,
                'edges': edges
            })
            i += 3
        else:
            i += 1
    
    return solutions

def parse_sample_file(filepath):
    """解析sample文件，提取所有距离矩阵样本"""
    samples = []
    with open(filepath, 'r') as f:
        content = f.read()
    
    # 分割不同的样本
    sample_sections = content.split('--- Sample')
    
    for i, section in enumerate(sample_sections):
        if i == 0:  # 跳过第一个部分（min_dist和max_dist）
            continue
            
        # 查找距离矩阵
        dist_start = section.find('dist_matrix:')
        if dist_start == -1:
            continue
            
        dist_section = section[dist_start:]
        lines = dist_section.split('\n')[1:]  # 跳过'dist_matrix:'行
        
        matrix = []
        for line in lines:
            if line.strip() and not line.startswith('---'):
                try:
                    row = [float(x) for x in line.split()]
                    if len(row) > 0:  # 确保行不为空
                        matrix.append(row)
                except ValueError:
                    break  # 遇到非数字行，停止解析
        
        if matrix:
            samples.append(matrix)
    
    return samples

def calculate_path_cost(edges, distance_matrix):
    """根据边列表和距离矩阵计算路径成本"""
    total_cost = 0.0
    for edge in edges:
        i, j = edge
        total_cost += distance_matrix[i][j]
    return total_cost

def calculate_mean(values):
    """计算平均值"""
    if not values:
        return 0.0
    return sum(values) / len(values)

def main():
    # 读取solution文件
    solution_file = 'solution/R-50-1000.txt'
    solutions = parse_solution_file(solution_file)
    print(f"读取到 {len(solutions)} 个解")
    
    # 处理每个样本组
    sample_base_dir = 'sample-data/R-50-1000-sample'
    
    all_costs = []  # 存储所有实例的所有样本成本
    instance_averages = []  # 存储每个实例的平均成本
    
    for instance_idx in range(20):  # 20个实例
        sample_file = f'{sample_base_dir}/group_{instance_idx}.txt'
        
        if not os.path.exists(sample_file):
            print(f"文件不存在: {sample_file}")
            continue
            
        print(f"\n处理实例 {instance_idx}...")
        
        # 读取该实例的所有样本
        samples = parse_sample_file(sample_file)
        print(f"  读取到 {len(samples)} 个样本")
        
        if instance_idx >= len(solutions):
            print(f"  没有对应的解，跳过")
            continue
            
        # 获取对应的解
        solution = solutions[instance_idx]
        edges = solution['edges']
        
        # 计算每个样本的成本
        sample_costs = []
        for sample_idx, distance_matrix in enumerate(samples):
            cost = calculate_path_cost(edges, distance_matrix)
            sample_costs.append(cost)
            all_costs.append(cost)
            print(f"    样本 {sample_idx + 1}: {cost:.4f}")
        
        # 计算该实例的平均成本
        if sample_costs:
            instance_avg = calculate_mean(sample_costs)
            instance_averages.append(instance_avg)
            print(f"  实例 {instance_idx} 平均成本: {instance_avg:.4f}")
    
    # 计算总平均值
    if all_costs:
        total_average = calculate_mean(all_costs)
        print(f"\n=== 结果汇总 ===")
        print(f"总样本数: {len(all_costs)}")
        print(f"处理的实例数: {len(instance_averages)}")
        print(f"总平均成本: {total_average:.4f}")
        
        # 打印每个实例的平均成本
        print(f"\n各实例平均成本:")
        for i, avg in enumerate(instance_averages):
            print(f"实例 {i}: {avg:.4f}")
            
        # 计算实例平均成本的平均值（应该和总平均成本相同）
        instance_avg_of_avg = calculate_mean(instance_averages)
        print(f"\n实例平均成本的平均值: {instance_avg_of_avg:.4f}")
    else:
        print("没有成功计算任何成本")

if __name__ == "__main__":
    main() 
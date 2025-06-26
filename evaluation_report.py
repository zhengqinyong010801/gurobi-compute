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

def calculate_std(values):
    """计算标准差"""
    if len(values) <= 1:
        return 0.0
    mean = calculate_mean(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5

def main():
    # 读取solution文件
    solution_file = 'solution/R-50-1000.txt'
    solutions = parse_solution_file(solution_file)
    
    # 处理每个样本组
    sample_base_dir = 'sample-data/R-50-1000-sample'
    
    results = []
    all_costs = []
    
    for instance_idx in range(20):  # 20个实例
        sample_file = f'{sample_base_dir}/group_{instance_idx}.txt'
        
        if not os.path.exists(sample_file):
            continue
            
        # 读取该实例的所有样本
        samples = parse_sample_file(sample_file)
        
        if instance_idx >= len(solutions):
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
        
        # 计算统计信息
        instance_avg = calculate_mean(sample_costs)
        instance_std = calculate_std(sample_costs)
        instance_min = min(sample_costs) if sample_costs else 0
        instance_max = max(sample_costs) if sample_costs else 0
        
        results.append({
            'instance': instance_idx,
            'obj': solution['obj'],
            'regret': solution['regret'],
            'sample_costs': sample_costs,
            'mean': instance_avg,
            'std': instance_std,
            'min': instance_min,
            'max': instance_max,
            'num_samples': len(sample_costs)
        })
    
    # 生成报告
    with open('evaluation_report.txt', 'w') as f:
        f.write("=== 鲁棒车辆路径问题解的评估报告 ===\n\n")
        f.write(f"数据集: R-20-100\n")
        f.write(f"实例数量: {len(results)}\n")
        f.write(f"每个实例的样本数: 5\n")
        f.write(f"总样本数: {len(all_costs)}\n\n")
        
        # 总体统计
        total_mean = calculate_mean(all_costs)
        total_std = calculate_std(all_costs)
        total_min = min(all_costs) if all_costs else 0
        total_max = max(all_costs) if all_costs else 0
        
        f.write("=== 总体统计 ===\n")
        f.write(f"总平均成本: {total_mean:.4f}\n")
        f.write(f"总标准差: {total_std:.4f}\n")
        f.write(f"最小成本: {total_min:.4f}\n")
        f.write(f"最大成本: {total_max:.4f}\n\n")
        
        # 实例平均成本的统计
        instance_means = [r['mean'] for r in results]
        instance_mean_avg = calculate_mean(instance_means)
        instance_mean_std = calculate_std(instance_means)
        
        f.write("=== 实例平均成本统计 ===\n")
        f.write(f"实例平均成本的平均值: {instance_mean_avg:.4f}\n")
        f.write(f"实例平均成本的标准差: {instance_mean_std:.4f}\n")
        f.write(f"最佳实例平均成本: {min(instance_means):.4f}\n")
        f.write(f"最差实例平均成本: {max(instance_means):.4f}\n\n")
        
        # 详细的实例结果
        f.write("=== 详细结果 ===\n")
        f.write("实例\tobj值\tregret\t平均成本\t标准差\t最小成本\t最大成本\t样本成本列表\n")
        for r in results:
            costs_str = "\t".join([f"{c:.4f}" for c in r['sample_costs']])
            f.write(f"{r['instance']}\t{r['obj']:.4f}\t{r['regret']:.4f}\t{r['mean']:.4f}\t"
                   f"{r['std']:.4f}\t{r['min']:.4f}\t{r['max']:.4f}\t{costs_str}\n")
        
        # 性能分析
        f.write("\n=== 性能分析 ===\n")
        
        # 按平均成本排序
        sorted_results = sorted(results, key=lambda x: x['mean'])
        f.write("\n最佳5个实例（按平均成本）:\n")
        for i, r in enumerate(sorted_results[:5]):
            f.write(f"{i+1}. 实例{r['instance']}: 平均成本={r['mean']:.4f}, 标准差={r['std']:.4f}\n")
            
        f.write("\n最差5个实例（按平均成本）:\n")
        for i, r in enumerate(sorted_results[-5:]):
            f.write(f"{i+1}. 实例{r['instance']}: 平均成本={r['mean']:.4f}, 标准差={r['std']:.4f}\n")
        
        # 稳定性分析
        f.write("\n最稳定5个实例（按标准差）:\n")
        sorted_by_std = sorted(results, key=lambda x: x['std'])
        for i, r in enumerate(sorted_by_std[:5]):
            f.write(f"{i+1}. 实例{r['instance']}: 标准差={r['std']:.4f}, 平均成本={r['mean']:.4f}\n")
            
        f.write("\n最不稳定5个实例（按标准差）:\n")
        for i, r in enumerate(sorted_by_std[-5:]):
            f.write(f"{i+1}. 实例{r['instance']}: 标准差={r['std']:.4f}, 平均成本={r['mean']:.4f}\n")
    
    print("评估完成！详细报告已保存到 evaluation_report.txt")
    print(f"总平均成本: {total_mean:.4f}")
    print(f"处理了 {len(results)} 个实例，共 {len(all_costs)} 个样本")

if __name__ == "__main__":
    main() 
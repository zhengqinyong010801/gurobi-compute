import time
import random

# RCVRP 测试数据
def get_robust_rcvrp_instance(filename):
    with open(filename, 'r') as f:
        # Read all lines and remove surrounding whitespace and filter out empty lines
        lines = [line.strip() for line in f.readlines() if line.strip()]

    # Find the starting index of each data block
    min_dist_idx = lines.index('min_dist:')
    max_dist_idx = lines.index('max_dist:')
    # The file contains multiple samples, we'll use the demands from the first one
    node_demand_idx = lines.index('node_demand:')

    # Determine the number of nodes from the structure of the min_dist block
    # The number of lines between min_dist: and max_dist: is the number of nodes (depot + customers)
    num_nodes = max_dist_idx - (min_dist_idx + 1)
    n = num_nodes - 1  # Number of customers

    # Parse the lower bounds of distances (d_down)
    d_down = {}
    for i in range(num_nodes):
        row_vals = list(map(float, lines[min_dist_idx + 1 + i].split()))
        for j in range(num_nodes):
            d_down[i, j] = row_vals[j]

    # Parse the upper bounds of distances (d_up)
    d_up = {}
    for i in range(num_nodes):
        row_vals = list(map(float, lines[max_dist_idx + 1 + i].split()))
        for j in range(num_nodes):
            d_up[i, j] = row_vals[j]

    # Parse customer demands (q)
    q = [0.0] * (n + 1)
    for i in range(n):
        q[i + 1] = float(lines[node_demand_idx + 1 + i])

    return n, d_up, d_down, q

def clarke_wright(N, d, q, Q):
    """
    Clarke and Wright savings heuristic for CVRP.
    """
    # 1. Initial routes
    routes = {i: [0, i, 0] for i in N}
    route_demands = {i: q[i] for i in N}
    customer_to_route_id = {i: i for i in N}

    # 2. Calculate savings
    savings = []
    for i_idx, i in enumerate(N):
        for j in N[i_idx+1:]:
            # Use .get with a default for cases where an edge might not exist, though d should be complete.
            d_0i = d.get((0, i), d.get((i, 0), float('inf')))
            d_0j = d.get((0, j), d.get((j, 0), float('inf')))
            d_ij = d.get((i, j), d.get((j, i), float('inf')))
            s_ij = d_0i + d_0j - d_ij
            if s_ij > 0:
                savings.append((s_ij, i, j))
    
    # 3. Sort savings
    savings.sort(key=lambda x: x[0], reverse=True)

    # 4. Merge
    for _, i, j in savings:
        route_i_id = customer_to_route_id[i]
        route_j_id = customer_to_route_id[j]

        if route_i_id == route_j_id:
            continue

        route_i = routes[route_i_id]
        route_j = routes[route_j_id]
        
        if route_demands[route_i_id] + route_demands[route_j_id] > Q:
            continue
        
        merged = False
        # Case 1: i is end of route_i, j is start of route_j
        if route_i[-2] == i and route_j[1] == j:
            new_route = route_i[:-1] + route_j[1:]
            merged = True
        # Case 2: j is end of route_j, i is start of route_i
        elif route_j[-2] == j and route_i[1] == i:
            new_route = route_j[:-1] + route_i[1:]
            # swap roles to merge i's route into j's
            route_i_id, route_j_id = route_j_id, route_i_id
            route_i, route_j = route_j, route_i
            merged = True
        # Case 3: i is end, j is end
        elif route_i[-2] == i and route_j[-2] == j:
            new_route = route_i[:-1] + route_j[-2:0:-1] + [0]
            merged = True
        # Case 4: i is start, j is start
        elif route_i[1] == i and route_j[1] == j:
            new_route = route_j[:-1] + route_i[-2:0:-1] + [0]
            # swap roles to merge i's route into j's
            route_i_id, route_j_id = route_j_id, route_i_id
            route_i, route_j = route_j, route_i
            merged = True

        if merged:
            routes[route_i_id] = new_route
            route_demands[route_i_id] += route_demands[route_j_id]
            
            for customer in routes[route_j_id]:
                if customer != 0:
                    customer_to_route_id[customer] = route_i_id

            del routes[route_j_id]
            del route_demands[route_j_id]
            
    
    solution_edges = []
    final_routes = list(routes.values())
    for route in final_routes:
        for k in range(len(route) - 1):
            u, v = route[k], route[k+1]
            if u > v:
                u, v = v, u
            solution_edges.append((u,v))
            
    return solution_edges, final_routes

def generate_random_scenario(d_down, d_up):
    d_rand = {}
    for edge in d_down:
        d_rand[edge] = random.uniform(d_down[edge], d_up[edge])
        # ensure symmetry
        u, v = edge
        d_rand[(v,u)] = d_rand[edge]
    return d_rand

def calculate_path_cost(path_edges, distance_matrix):
    total_cost = 0
    for edge in path_edges:
        u, v = edge
        total_cost += distance_matrix.get((u, v), distance_matrix.get((v, u), 0))
    return total_cost


if __name__ == '__main__':
    n = 20
    int_max = 100
    Q = 1.0
    N = [i for i in range(1, n + 1)]

    all_instance_costs = []
    for idx in range(0,20): # Let's just run for one instance for demonstration
        ins_name = 'sample-data/R-{}-{}-sample/group_{}.txt'.format(n,int_max, idx)
        
        #########
        n, d_up, d_down, q = get_robust_rcvrp_instance(ins_name)

        # Use average distance for heuristic
        d_avg = {e: (d_up[e] + d_down[e]) / 2 for e in d_up}
        
        print(f"Solving instance: {ins_name}")
        best_path_edges, best_routes = clarke_wright(N, d_avg, q, Q)

        # print("\nBest path found with Clarke-Wright heuristic:")
        # for i, r in enumerate(best_routes):
        #     print(f"Route #{i+1}: {r}")
        
        # print("\nCalculating costs for 5 random scenarios...")
        scenario_costs = []
        for i in range(5):
            d_scenario = generate_random_scenario(d_down, d_up)
            cost = calculate_path_cost(best_path_edges, d_scenario)
            # print(f"Scenario {i+1}, Total cost: {cost:.4f}")
            scenario_costs.append(cost)

        if scenario_costs:
            average_cost = sum(scenario_costs) / len(scenario_costs)
            # print(f"\nAverage cost over {len(scenario_costs)} scenarios: {average_cost:.4f}")
            all_instance_costs.append(average_cost)

    if all_instance_costs:
        final_average = sum(all_instance_costs) / len(all_instance_costs)
        print(f"\nAverage cost over {len(all_instance_costs)} instances: {final_average:.4f}")



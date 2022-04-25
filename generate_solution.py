import pandas as pd
import pickle as pkl
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from typing import Dict, List


COUNT = 40
VEHICLE_CAPACITY = 6
VEHICLE_COUNT = 10
MAX_SOLVER_TIME_SECONDS = 600
USE_TIME_WINDOWS = False
LOCATION = "data"
DEPOT_ID = 9
SOLUTION_LOCATION = "data/solution.pkl"
KITCHEN_DATA_LOCATION = "data/kitchens-locations.csv"
TIME_GRAPH_LOCATION = "data/time.pkl"


def get_kitchen_data(location):
    kitchetns = pd.read_csv(location)
    kitchetns = kitchetns.fillna(0)
    return kitchetns


def get_seconds(data):
    if data == '0':
        return 0
    else:
        data = data.split(' - ')[1]
        data = data.split(':')
        return (int(data[0]) - 21) * 60 * 60 + int(data[1])*60


def collect_data(travel_times, delivery_windows, demands, depot_id, vehicle_counts):
    data = {}
    data['distance_matrix'] = [elem[:COUNT] for elem in travel_times[:COUNT]]
    data['num_vehicles'] = vehicle_counts
    data['demands'] = list(demands.astype(int))
    data['vehicle_capacities'] = [VEHICLE_CAPACITY] * vehicle_counts
    data['depot'] = depot_id
    data['time_windows'] = delivery_windows[:COUNT]
    return data


def load_time_graph(graph_location: str):
    with open(graph_location, 'rb') as graph_file:
        graph = pkl.load(graph_file)
    return graph

def load_data(kitchen_data_locations, time_data_locat):
    kitchens = pd.read_csv(kitchen_data_locations).dropna()
    kitchens = kitchens[kitchens.requirements != 0.0]
    kitchens.time = kitchens.time.astype(str).apply(get_seconds)
    delivery_windows = [(0, elem) for elem in kitchens.time]
    demands = kitchens.requirements
    graph = load_time_graph(time_data_locat)
    
    return collect_data(graph, delivery_windows, demands, DEPOT_ID, VEHICLE_COUNT)


def solve(data):
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)
    

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]
    
    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        data['vehicle_capacities'],
        True,
        'Capacity')
    
    if USE_TIME_WINDOWS:
        time = 'Time'
        routing.AddDimension(
            transit_callback_index,
            30,  
            30000,  
            False,
            time)
        time_dimension = routing.GetDimensionOrDie(time)
        for location_idx, time_window in enumerate(data['time_windows']):
            if location_idx == data['depot']:
                continue
            index = manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        depot_idx = data['depot']
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            time_dimension.CumulVar(index).SetRange(
                data['time_windows'][depot_idx][0],
                data['time_windows'][depot_idx][1])
    
        for i in range(data['num_vehicles']):
            routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(routing.Start(i)))
            routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(routing.End(i)))

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC)
    search_parameters.time_limit.FromSeconds(MAX_SOLVER_TIME_SECONDS)

    solution = routing.SolveWithParameters(search_parameters)
    return routing, solution, manager


def extract_solution(routing, solution, manager):
    paths = []
    for vehicle_id in range(VEHICLE_COUNT):
        paths.append([])
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            paths[vehicle_id].append(node_index)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
    return paths


def save_data(solution, solution_location):
    with open(solution_location, "wb") as data_file:
        pkl.dump(solution, data_file)


def main():
    data = load_data(KITCHEN_DATA_LOCATION, TIME_GRAPH_LOCATION)
    routing, solution, manager = solve(data)
    solution = extract_solution(routing, solution, manager)
    save_data(solution, SOLUTION_LOCATION)


if __name__ == '__main__':
    main()

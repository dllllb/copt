import pandas as pd
import osmnx as ox
import pandas as pd
import pickle as pkl
import folium

GRAPH_LOCATION = "data/full_graph.pkl"
PATHS_FILE_LOCATION = "data/paths.pkl"
SOLUTION_LOCATION = "data/solution.pkl"
KITCHEN_INFO = "data/kitchens-locations.csv"

def load_graph(graph_location):
    with open(graph_location, "rb") as data_file:
        graph = pkl.load(data_file)
    return graph


def read_solution(solution_location):
    with open(solution_location, 'rb') as data_file:
        solution = pkl.load(data_file)
    return solution


def load_routes(routes_locations):
    with open(routes_locations, 'rb') as data_file:
        routs = pkl.load(data_file)
    return routs


def plot_point(x, y, color, title, map):
    folium.CircleMarker(location=[y, x],
                        radius=5,
                        weight=5,
                        tooltip=title,
                        color=color).add_to(map)

def plot_solution(graph, all_routes, solution, titles, map_path):
    route = all_routes[(solution[0], solution[1])]
    start_point = graph.nodes[route[0]]
    map_ = ox.plot_route_folium(graph, route)
    folium.CircleMarker(location=[start_point['y'], start_point['x']],
                            radius=5,
                            weight=5,
                            tooltip=titles[solution[0]],
                            color='red').add_to(map_)
    point = graph.nodes[route[-1]]
    folium.CircleMarker(location=[point['y'], point['x']],
                            radius=5,
                            weight=5,
                            tooltip=titles[solution[1]],
                            color='blue').add_to(map_)
    for index in range(1, len(solution)):
        route = all_routes[(solution[index-1], solution[index])]
        map_ = ox.plot_route_folium(graph, route, route_map=map_)
        point = graph.nodes[route[-1]]
        folium.CircleMarker(location=[point['y'], point['x']],
                            radius=5,
                            weight=5,
                            tooltip=titles[solution[index]],
                            color='blue'
            ).add_to(map_)
    map_.save(map_path)


def main():
    graph = load_graph(GRAPH_LOCATION)
    all_routes = load_routes(PATHS_FILE_LOCATION)
    solution = read_solution(SOLUTION_LOCATION)
    names = pd.read_csv(KITCHEN_INFO).title.to_list()
    for index, elem in enumerate(solution):
        plot_solution(graph, all_routes, elem, names, f"data/route_{index}.html")


if __name__ == '__main__':
    main()

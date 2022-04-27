import pandas as pd
from generate_solution import TIME_GRAPH_LOCATION
import osmnx as ox
import pandas as pd
import pickle as pkl
import folium
import datetime

GRAPH_LOCATION = "data/full_graph.pkl"
PATHS_FILE_LOCATION = "data/paths.pkl"
SOLUTION_LOCATION = "data/solution.pkl"
KITCHEN_INFO = "data/kitchens-locations.csv"
TIME_GRAPH_LOCATION = "data/time.pkl"


def load_pickle_object(path):
    with open(path, 'rb') as data_file:
        return pkl.load(data_file)


def plot_point(x, y, color, title, map):
    folium.CircleMarker(location=[y, x],
                        radius=5,
                        weight=5,
                        tooltip=title,
                        color=color).add_to(map)

def plot_route(graph, all_routes, solution, titles, feature_group, color, times):
    current_time = datetime.datetime(year=2021, month=1, day=1, hour=21)
    route = all_routes[(solution[0], solution[1])]
    start_point = graph.nodes[route[0]]
    ox.plot_route_folium(graph, route, route_map=feature_group)
    folium.CircleMarker(location=[start_point['y'], start_point['x']],
                            radius=5,
                            weight=5,
                            tooltip=titles[solution[0]],
                            color='red').add_to(feature_group)
    point = graph.nodes[route[-1]]
    folium.CircleMarker(location=[point['y'], point['x']],
                            radius=5,
                            weight=5,
                            tooltip=titles[solution[1]],
                            color=color).add_to(feature_group)
    for index in range(1, len(solution)):
        route = all_routes[(solution[index-1], solution[index])]
        travel_time = times[solution[index-1]][solution[index]]
        current_time += datetime.timedelta(seconds=travel_time)
        if index != 1:
            current_time += datetime.timedelta(minutes=15)
        ox.plot_route_folium(graph, route, route_map=feature_group, color=color)
        point = graph.nodes[route[-1]]
        folium.CircleMarker(location=[point['y'], point['x']],
                            radius=5,
                            weight=5,
                            tooltip=f"{titles[solution[index]]} {current_time.strftime('%H:%M:%S')}",
                            color=color
            ).add_to(feature_group)
    return feature_group

def plot_solutions(graph, all_routes, solutions, titles, times):
    route_map = folium.Map(location=[55.751244, 37.618423])
    colors = ['blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray'] 
    for index, elem in enumerate(solutions):
        feature_group = folium.FeatureGroup(name=f'Track {index}',overlay=True)
        plot_route(graph, all_routes, elem, titles, feature_group, colors[index % len(colors)], times)
        feature_group.add_to(route_map)
        route_map.add_child(feature_group)
    folium.LayerControl().add_to(route_map)
    return route_map



def main():
    graph = load_pickle_object(GRAPH_LOCATION)
    all_routes = load_pickle_object(PATHS_FILE_LOCATION)
    solution = load_pickle_object(SOLUTION_LOCATION)
    time_graph = load_pickle_object(TIME_GRAPH_LOCATION)
    names = pd.read_csv(KITCHEN_INFO).title.to_list()
    route_map = plot_solutions(graph, all_routes, solution, names, time_graph)
    route_map.save("data/routes.html")


if __name__ == '__main__':
    main()

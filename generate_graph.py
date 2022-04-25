import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import osmnx  as ox
import networkx as nx
from tqdm import tqdm
import pandas as pd
import pickle as pkl


def get_data(data_file_location: str) -> pd.DataFrame:
    data = pd.read_csv(data_file_location)
    data.longitude = data.longitude.str.replace(',', '.').astype(float)
    data.latitude = data.latitude.str.replace(',', '.').astype(float)
    return data[['longitude', 'latitude']]


def transform_to_geopandas(locations: pd.DataFrame) -> gpd.GeoDataFrame:
    all_points = []
    for i in range(len(locations)):
        all_points.append(Point(locations.iloc[i, 0], locations.iloc[i, 1]))
    return gpd.GeoDataFrame(data=all_points, columns=['geometry'], crs=4326, geometry='geometry')


def get_graph(all_points: gpd.GeoDataFrame) -> nx.MultiDiGraph:
    all_points = all_points.reset_index()
    convex = all_points.unary_union.convex_hull
    graph_extent = convex.buffer(0.02)
    graph = ox.graph_from_polygon(graph_extent, network_type='drive')
    graph = ox.add_edge_speeds(graph)
    graph = ox.add_edge_travel_times(graph)
    return graph


def get_distances_and_time(all_points: gpd.GeoDataFrame, graph: nx.MultiDiGraph):
    location_times = []
    location_paths = {}
    for i in tqdm(range(len(all_points))):
        location_times.append([])
        for j in range(len(all_points)):
            origin = all_points.iloc[i]
            destination = all_points.iloc[j]
            closest_origin_node = ox.distance.nearest_nodes(graph, origin.geometry.x, origin.geometry.y)
            closest_target_node = ox.distance.nearest_nodes(graph, destination.geometry.x, destination.geometry.y)
            path = ox.shortest_path(graph, closest_origin_node, closest_target_node, weight="travel_time")
            location_paths[(i, j)] = path
            location_times[i].append(int(sum(ox.utils_graph.get_route_edge_attributes(graph, path, "travel_time"))))
    return location_times, location_paths


def save_data(data, location):
    with open(location, "wb") as data_file:
        pkl.dump(data, data_file)


def main():
    location = "data/kitchens-locations.csv"
    data = transform_to_geopandas(get_data(location))
    graph = get_graph(data)
    time, paths = get_distances_and_time(data, graph)
    save_data(time, "data/time.pkl")
    save_data(paths, "data/paths.pkl")
    save_data(graph, "data/full_graph.pkl")


if __name__ == '__main__':
    main()

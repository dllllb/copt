A small demo of the `ORTools`-based vehicle routing problem solution. Distance matrix is calculated using the road graph, loaded from the OpenStreetMap using `OSMnx`.

Execution steps:
```sh
uv run generate_graph.py
uv run generate_solution.py
uv run plot_solution.py
```

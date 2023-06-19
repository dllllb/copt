A small demo of the `ORTools`-based vehicle routing problem solution. Distance matrix is calculated using the road graph, loaded from the OpenStreetMap using `OSMnx`.

Execution steps:
```sh
pipenv install
pipenv shell

python generate_graph.py
python generate_solution.py
python plot_solution.py
```

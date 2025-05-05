# ai/lookup_table.py

import os
import pickle
from collections import deque

# ─── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.abspath(os.path.dirname(__file__))
DATA_DIR      = os.path.join(BASE_DIR, '..', 'data')
DEFAULT_FILE  = os.path.join(DATA_DIR, 'distance_lookup.pkl')


def compute_distance_lookup(graph):
    """
    Precompute shortest‐path distances between every pair of nodes via BFS.
    Returns a dict: { start_node: { dest_node: distance, … }, … }
    """
    lookup = {}
    for start in graph:
        distances = {start: 0}
        queue     = deque([start])

        while queue:
            current = queue.popleft()
            d = distances[current]
            for nbr in graph[current]:
                if nbr not in distances:
                    distances[nbr] = d + 1
                    queue.append(nbr)

        lookup[start] = distances

    return lookup


def save_lookup_table(lookup_table, filename=None):
    """
    Save the lookup_table to disk using pickle.
    Defaults to 'data/distance_lookup.pkl'.
    """
    # ensure data dir exists
    out = filename or DEFAULT_FILE
    os.makedirs(os.path.dirname(out), exist_ok=True)

    with open(out, 'wb') as f:
        pickle.dump(lookup_table, f)


def load_lookup_table(filename=None):
    """
    Load the lookup table from disk.
    Returns the dict, or None if the file doesn’t exist.
    """
    inp = filename or DEFAULT_FILE
    try:
        with open(inp, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    # If you run `python -m ai.lookup_table`, this will:
    # 1) Build the graph from level1
    # 2) Compute the BFS lookup
    # 3) Save it under data/distance_lookup.pkl
    # 4) Reload and print a sample entry
    from ai.search     import build_graph
    from maps.level1   import game_map

    graph, _, _    = build_graph(game_map)
    lookup_table   = compute_distance_lookup(graph)
    save_lookup_table(lookup_table)

    loaded = load_lookup_table()
    print("Lookup Table Loaded. Sample entry:")
    sample = next(iter(loaded))
    print(f"From node {sample}: {loaded[sample]}")

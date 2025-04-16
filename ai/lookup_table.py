# ai/lookup_table.py
import os
import sys

# Add the parent directory to sys.path so that maps and other directories are found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from collections import deque
import pickle

def compute_distance_lookup(graph):
    """
    Precomputes the shortest-path distances between every pair of valid nodes
    in the graph using BFS.
    
    Parameters:
      graph: An adjacency list where keys are nodes (tuples, e.g., (row, col))
             and values are lists of adjacent nodes.
             
    Returns:
      A nested dictionary in the form:
      {start_node: {destination_node: distance, ...}, ...}
    """
    lookup_table = {}
    
    for start_node in graph.keys():
        distances = {start_node: 0}  # Distance to self is 0
        queue = deque([start_node])
        
        while queue:
            current = queue.popleft()
            current_distance = distances[current]
            
            for neighbor in graph[current]:
                if neighbor not in distances:
                    distances[neighbor] = current_distance + 1
                    queue.append(neighbor)
                    
        lookup_table[start_node] = distances
        
    return lookup_table

def save_lookup_table(lookup_table, filename='distance_lookup.pkl'):
    """
    Saves the computed lookup table to disk using pickle.
    """
    with open(filename, 'wb') as f:
        pickle.dump(lookup_table, f)

def load_lookup_table(filename='distance_lookup.pkl'):
    """
    Loads the lookup table from disk.
    
    Returns:
      The lookup table dictionary if the file exists; otherwise, returns None.
    """
    try:
        with open(filename, 'rb') as f:
            lookup_table = pickle.load(f)
            return lookup_table
    except FileNotFoundError:
        return None

# Example usage (this block can be removed or commented out in production):
if __name__ == "__main__":
    from ai.search import build_graph
    from maps.level1 import game_map  # or level2 if you prefer
    
    # Build the graph from the static map.
    graph, _, _ = build_graph(game_map)
    
    # Compute and save the lookup table.
    lookup_table = compute_distance_lookup(graph)
    save_lookup_table(lookup_table)
    
    # For debugging, you can load and print the lookup table:
    loaded_table = load_lookup_table()
    print("Lookup Table Loaded. Sample entry:")
    sample_key = list(loaded_table.keys())[0]
    print(f"From node {sample_key}: {loaded_table[sample_key]}")

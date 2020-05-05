import pickle

def read_adjacencies():
    with open("ticket_to_ride/data/adjacent.obj", "rb") as f:
        adjacent_edges_int = pickle.load(f)
        adjacent_nodes_int = pickle.load(f)
        adjacent_edges_tuple = pickle.load(f)
        adjacent_nodes_str = pickle.load(f)
    return adjacent_edges_int, adjacent_nodes_int, adjacent_edges_tuple, adjacent_nodes_str


def read_masks():
    with open("ticket_to_ride/data/masks.obj", "rb") as f:
        M0 = pickle.load(f)
        M1 = pickle.load(f)
        M2 = pickle.load(f)
        M3 = pickle.load(f)
    return M0, M1, M2, M3


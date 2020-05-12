import pickle


def read_adjacencies():
    with open('ticket_to_ride/data/adjacent.obj', 'rb') as f:
        adjacent_edges_int = pickle.load(f)
        adjacent_nodes_int = pickle.load(f)
        adjacent_edges_tuple = pickle.load(f)
        adjacent_nodes_str = pickle.load(f)
    return adjacent_edges_int, adjacent_nodes_int, adjacent_edges_tuple, adjacent_nodes_str


def read_masks():
    with open('ticket_to_ride/data/masks.obj', 'rb') as f:
        M = pickle.load(f)
        number_of_cluster_reps = pickle.load(f)
    return M, number_of_cluster_reps


def extract_cluster_reps():
    _, number_of_cluster_reps = read_masks()
    print('Number of cluster repetitions:', number_of_cluster_reps)
    return number_of_cluster_reps

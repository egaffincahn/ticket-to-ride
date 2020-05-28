import networkx as nx
from ticket.population import Population
from ticket.game import Game
from ticket.board import Map
from matplotlib import pyplot as plt
import copy
import numpy as np


def play_single_game(players=3):
    pop = Population(individuals=players)
    game = Game(pop.cohort)
    game.play_game()
    return game

game = play_single_game()
player_dists = np.zeros(game.players, dtype=np.int16)

# for turn = 1:info.players
for turn in range(game.players):
#
#     H = rmedge(G.distance, find(G.taken.Edges.Weight ~= turn)); % remove all the edges where this player didn't go
    H = game.map.create_player_subgraph(turn, multi=True, incl_nodes=True)
#
#     fulladjmat = full(adjacency(H)); % create full adjacency matrix with 1s where two cities are connected by this player
    full_adj_mat = nx.adjacency_matrix(H).todense()

#     path = {}; % each cell is vector representing the route through each city index
    path = []
#     terminated = false(size(path)); % vector representing whether the path has been full searched
    terminated = []
#     trimadjmat = {}; % each cell is a full adjacency matrix but where the city connections looked at so far have been removed (trimmed) to disallow them from being used again
    trim_adj_mat = []
#     playerdists = 0; % vector for this player where each index is the number of points in a path, only updated once it's terminated
    path_dists = []
#     foundglobalbest = false; % tells us if there's a path that has used every connection - allows us to quit early
    found_global_best = False
#
#     for city = find(sum(fulladjmat, 1) > 0) % only look at the cities that have connections
    for n in np.flatnonzero(np.sum(full_adj_mat, axis=0)):
#         path{end+1} = city; % initialize a new path with the current city we start with
        path.append([n])
#         terminated(end+1) = false; % this new path has not been finished
        terminated.append(False)
#         currpath = length(path); % currpath indexes the current index of the path (and other) cell vector we are exploring
#         trimadjmat{currpath} = fulladjmat; % initialize the current trimmed adjacency matrix
        trim_adj_mat.append(copy.deepcopy(full_adj_mat))
#         while any(~terminated) && ~foundglobalbest % only stop when all paths are terminated or we found a path that uses all connections
        while any(np.logical_not(terminated)) and not found_global_best:
#             curr = path{currpath}(end); % current city index
            curr_path_index = np.flatnonzero(np.logical_not(terminated))[0]
            n_ = path[curr_path_index][-1]
#             numconn = sum(trimadjmat{currpath}(:,curr)); % number of connected cities to the current
            connected_nodes = np.flatnonzero(trim_adj_mat[curr_path_index][:, n_])
            num_connected = len(connected_nodes)
#             if numconn == 1 % only 1 - easy case
            if num_connected == 1:
#                 conn = find(trimadjmat{currpath}(:,curr), 1, 'first'); % find the connected city index
#                 path{currpath} = [path{currpath} conn]; % add the connected to the path vector
                n__ = connected_nodes
                path[curr_path_index] = np.concatenate((path[curr_path_index], n__))
#                 trimadjmat{currpath}(curr,conn) = 0; % remove it from the trimmed adjacency matrix
#                 trimadjmat{currpath}(conn,curr) = 0; % and the symmetric (row,column) pair
                trim_adj_mat[curr_path_index][n_, n__] = 0
                trim_adj_mat[curr_path_index][n__, n_] = 0
#             elseif numconn > 1 % more than 1 connected cities
            elif num_connected > 1:
#                 terminated(currpath) = []; % we remove a few of the current cells to be replaced by 2 or more (1 from each connected city)
                terminated = [t for i, t in enumerate(terminated) if i != curr_path_index]
#                 for next = find(trimadjmat{currpath}(:,curr))' % scroll through each connected city
                for n__ in connected_nodes:
#                     path{end+1} = [path{currpath} next]; % create a new path and add the connected city to it
                    path.append(np.concatenate((path[curr_path_index], [n__])))
#                     terminated(end+1) = false; % do the same as in the 1 connected city case
                    terminated.append(False)
#                     trimadjmat{end+1} = trimadjmat{currpath};
                    trim_adj_mat.append(trim_adj_mat[curr_path_index])
#                     trimadjmat{end}(curr,next) = 0;
#                     trimadjmat{end}(next,curr) = 0;
                    trim_adj_mat[curr_path_index][n_, n__] = 0
                    trim_adj_mat[curr_path_index][n__, n_] = 0
#                 end
#                 trimadjmat(currpath) = []; % remove some more of the current cells
                trim_adj_mat = [t for i, t in enumerate(trim_adj_mat) if i != curr_path_index]
#                 path(currpath) = [];
                path = [p for i, p in enumerate(path) if i != curr_path_index]
#                 currpath = length(path); % tell the algorithm which path to get started with after this fork
#             elseif numconn == 0 % when there are no more connected cities on this path
            elif num_connected == 0:
#                 ind = findedge(H, path{currpath}(1:end-1), path{currpath}(2:end)); % gets the edge indices for the cities in the path
                edges = []
                for i in range(len(path[curr_path_index]) - 1):
                    n0 = game.map.get_node_name(path[curr_path_index][i])
                    n1 = game.map.get_node_name(path[curr_path_index][i + 1])
                    edges.append(game.map.get_edge_index((n0, n1, 0)))
                n0 = game.map.get_node_name(path[curr_path_index][0])
                n1 = game.map.get_node_name(path[curr_path_index][-1])
                if len(path[curr_path_index]) > 2 and n0 in nx.neighbors(H, n1):
                    edges.append(game.map.get_edge_index((n0, n1, 0)))
#                 playerdists(currpath) = sum(H.Edges.Weight(ind)); % adds up the distances
                path_dists.append(sum(game.map.extract_feature(edges, feature='distance')))
#                 if all(~trimadjmat{currpath}(:)) % all cities have been connected on this path (exciting!)
                if np.all(np.logical_not(trim_adj_mat[curr_path_index])):
#                     foundglobalbest = true;
                    found_global_best = True
#                 else
                else:
#                     terminated(currpath) = true; % don't need to return to this path
                    terminated[curr_path_index] = True
#                     currpath = find(~terminated, 1, 'last'); % get started on the last unfinished path (could choose any of them)
#                 end
#             end
#         end
        if found_global_best:
            break
#         if foundglobalbest
#             break
#         end
#     end
#     bestdist(turn) = max(playerdists);
    player_dists[turn] = max(path_dists)
# end
#
# longest = max(bestdist); % find the value of the longest
# points = 10 * (longest == bestdist); % get player(s) with longest, give them all 10!
#
#

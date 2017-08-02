function plotgraph(turn, G, cards, info)
% return
%% plots player 1's goals and locations
while 0
    h = plot(G.distance, 'NodeColor', [.75 .75 .75], 'EdgeColor', [.75 .75 .75]);
    h.EdgeLabel = G.distance.Edges.Weight;
    
    player = 1;
    colors = jet(length(cards.playergoals{player}));
    for goal = 1:length(cards.playergoals{player})
        highlight(h, cards.playergoals{player}{goal}{1}, 'NodeColor', colors(goal,:), 'MarkerSize', 10)
        highlight(h, cards.playergoals{player}{goal}{2}, 'NodeColor', colors(goal,:), 'MarkerSize', 10)
    end
    for edge = 1:numedges(G.taken)
        player = G.taken.Edges.Weight(edge);
        if player == 1
            [s, t] = findedge(G.taken, edge);
            highlight(h, s, t, 'EdgeColor', 'k', 'LineWidth', 5)
        end
    end
end

%% plots all taken
h = plot(G.taken, 'NodeColor', [.75 .75 .75], 'EdgeColor', [.75 .75 .75]);
h.EdgeLabel = G.distance.Edges.Weight;

colors = jet(info.players);

for edge = 1:numedges(G.taken)
    player = G.taken.Edges.Weight(edge);
    if player ~= 0
        [s, t] = findedge(G.taken, edge);
        highlight(h, s, t, 'EdgeColor', colors(player,:), 'LineWidth', 5)
    end
end

% this is a slow, stupid way to code this
% it also doesn't say which goal cities go with which
% maybe do this based on turn
for node = 1:numnodes(G.taken)
    nodename = char(G.distance.Nodes.Name(node));
    needed = [];
    for player = 1:info.players
        for goal = 1:length(cards.playergoals{player})
            for city = 1:2
                if strcmp(nodename, cards.playergoals{player}{goal}{city})
                    needed(end+1) = player;
                end
            end
        end
    end
    if ~isempty(needed)
        if length(needed) > 1 && any(turn == needed)
            highlight(h, nodename, 'NodeColor', colors(turn,:), 'MarkerSize', 10)
        else
            highlight(h, nodename, 'NodeColor', colors(needed(1),:), 'MarkerSize', 10)
        end
    end
end


%%
drawnow
function plotgraph(turn, G, cards, info)

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


%%
drawnow
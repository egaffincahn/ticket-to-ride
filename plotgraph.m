function plotgraph(turn, G, cards, info)

% x,y positions of cities

clf
playercolors = jet(info.players);

playerspots = [... % subplot indices
    5 6; ...
    30 40; ...
    90 100; ...
    81 91; ...
    21 31];

%% individual player info
longestroadpoints = addlongestroad(G, info);
[goalpoints, completed] = addgoalcards(G, cards, info); % check if the goal was completed
for player = 1:info.players
    subplot(12,10,playerspots(player,:))
    yspread = .25; if player == 1; yspread = yspread * 2; end
    ypos = 1.5;            text(0, ypos, sprintf('Player %d', player), 'FontWeight', 'bold', 'Color', playercolors(player,:))
    ypos = ypos - yspread; text(0, 1.5-yspread*1, sprintf('%d train cars remaining', info.pieces(player)))
    ypos = ypos - yspread; text(0, 1.5-yspread*2, sprintf('%d cards in hand', length(cards.hand{player})))
    ypos = ypos - yspread;
    yspread = yspread / 1.5;
    for goal = 1:length(cards.playergoals{player})
        if completed{player}(goal)
            completion = '[COMPLETED]';
        else
            completion = '';
        end
        text(0, ypos, sprintf('%s - %s [%d] %s', cards.playergoals{player}{goal}{1}, cards.playergoals{player}{goal}{2}, cards.playergoals{player}{goal}{3}, completion))
        ypos = ypos - yspread;
    end
    if player == turn
        axis off
        text(-.5, 1.5-yspread*0, '*', 'FontWeight', 'bold', 'FontSize', 36)
    else
        axis off
    end
end

%% general text at bottom
subplot(12,10,101:120)
if turn == 0 % end of game
    text(0, 0, [sprintf('%d ', info.points) 'total points'], 'FontSize', 14)
    trackpoints = info.points - longestroadpoints - goalpoints;
    text(0, .25, [sprintf('%d ', goalpoints), 'goal points'])
else
    text(0, 0, [sprintf('%d ', info.points + longestroadpoints) 'total points'], 'FontSize', 14)
    trackpoints = info.points;
end
text(0, .5, [sprintf('%d ', longestroadpoints) 'longest points'])
text(0, .75, [sprintf('%d ', trackpoints) 'track points'])
text(0, 1, sprintf('%d cards in deck, %d cards in discard', length(cards.deck), length(cards.discards)), 'FontSize', 14)
axis off

%% plot graph
subplot(12,10,intersect(11:100, find(ismember(mod(1:120, 10), 2:9))))
h = plot(G.taken, 'NodeColor', [.75 .75 .75], 'EdgeColor', [.75 .75 .75]);
h.EdgeLabel = G.distance.Edges.Weight;
axis off

%% all taken edges
for edge = 1:numedges(G.taken)
    player = G.taken.Edges.Weight(edge);
    if player ~= 0
        [s, t] = findedge(G.taken, edge);
        highlight(h, s, t, 'EdgeColor', playercolors(player,:), 'LineWidth', 5)
    end
end

%% current player's goals
if turn == 0
    text(0, -1, 'GAME OVER', 'FontSize', 20)
else
    goalcolors = parula(length(cards.playergoals{turn}));
    for goal = 1:size(goalcolors, 1)
        for city = 1:2
            highlight(h, cards.playergoals{turn}{goal}{city}, 'NodeColor', goalcolors(goal,:), 'MarkerSize', 15)
        end
    end
end

%%
drawnow



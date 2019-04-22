function [points, winner] = playgame(G, s, cards, info, doplot)

if nargin < 5
    doplot = false;
end
    

t = tic;

players = length(s);

cards = movecards([], cards, 'deck', 'faceup', 1:5); % put first 5 face up
for turn = 1:players
    cards = movecards(turn, cards, 'deck', 'hand', 1:4); % give players their first cards
end

cards.playergoals = cellfun(@(x) {}, cell(1, players), 'UniformOutput', false);
for turn = 1:players
    cards = pickgoals(turn, cards);
end

turn = 1; % indicates player whose turn it is

while all(info.pieces > 2) % go until someone has 2 or fewer pieces
    if info.rounds > 100
        keyboard
    end
    [G, cards, info] = doturn(turn, G, cards, info, s, doplot);
    turn = turn + 1;
    if turn > players
        turn = 1;
        info.rounds = info.rounds + 1;
    end
end


for i = 1:players
    % they should lay down longest they have because it's almost over
    [G, cards, info] = doturn(turn, G, cards, info, s, doplot);
    turn = turn + 1;
    if turn > players % back around the table
        turn = 1;
        info.rounds = info.rounds + 1;
    end
end

% add up the points awarded for completing a goal card and longest road
info.points = info.points + addgoalcards(G, cards, info);
info.points = info.points + addlongestroad(G, info);

[~, winner] = max(info.points);

for turn = 1:players
    assert(45 - sum(G.distance.Edges.Weight(G.taken.Edges.Weight == turn)) == info.pieces(turn), 'Incorrect pieces remaining')
end

if doplot
    plotgraph(0, G, cards, info)
end


points = info.points;

% fprintf('winner: %d, points: %d, %d, %d\n\n', winner, points(1), points(2), points(3))
% fprintf('winner found - %.1f seconds to play game\n', toc(t))


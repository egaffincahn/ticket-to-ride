function winner = ticket(players)

% rng(1)

s = struct();

if nargin < 1 || isempty(players)
    players = 3;
end

G = initializemap;

pieces = 45 * ones([players, 1]);
points = zeros([players, 1]);
deck = Shuffle([zeros([1, 14]), repmat(1:8, [1, 12])]); deck(1:3) = 0;
[~, deck, faceup, discards] = movecards([], [], deck, [], [], 'deck', 'faceup', 1:5);
hand = cell(1, players);
for turn = 1:players
    [hand, deck, ~, discards] = movecards(turn, hand, deck, [], discards, 'deck', 'hand', 1:4);
end

goalcards = importgoals;
goalcards = goalcards(randperm(height(goalcards)),:);
goals = cellfun(@(x) {}, cell(1, players), 'UniformOutput', false);
for turn = 1:players
    [goals, goalcards] = pickgoals(turn, goals, goalcards, s);
end

turn = 1; % indicates player whose turn it is
while all(pieces > 2)
    [G, hand, deck, faceup, discards, goals, goalcards, pieces, points] = doturn(turn, G, hand, deck, faceup, discards, goals, goalcards, pieces, points, s);
    turn = turn + 1;
    if turn > players; turn = 1; end
end


for i = 1:players
    % they should lay down longest they have because it's almost over
    [G, hand, deck, faceup, discards, goals, goalcards, pieces, points] = doturn(turn, G, hand, deck, faceup, discards, goals, goalcards, pieces, points, s);
    turn = turn + 1;
    if turn > players; turn = 1; end
end

% add up goal cards
for turn = 1:3
    goalpoints = 0;
    H = G.taken;
    H = rmedge(H, find(H.Edges.Weight ~= turn));
    for i = 1:length(goals{turn})
        outcome = goals{turn}{i}{3};
        if isempty(shortestpath(H, goals{turn}{i}{1}, goals{turn}{i}{2}))
            outcome = -outcome;
        end
        goalpoints = goalpoints + outcome;
    end
    points(turn) = points(turn) + goalpoints;
end

% add up longest road

[~, winner] = max(points);

function addlongestroad_unittest

test = 0; % test number
info.players = 3; % number of players
G = initializemap;

figure(1), clf
h = plot(G.distance);
h.EdgeLabel = G.distance.Edges.Weight;
title('Track Distances')

% test: single track
turn = 1;
test = test + 1;
G.taken.Edges.Weight(findedge(G.taken, 'Vancouver', 'Calgary')) = turn; % 3
[points, bestdist] = addlongestroad(G, info);
if ~all(points == [10 0 0] & bestdist == [3 0 0])
    failed(G, turn, test)
end

% test: string of tracks, two players have tracks
turn = 2;
test = test + 1;
G.taken.Edges.Weight(findedge(G.taken, 'Seattle', 'Calgary')) = turn; % 4
G.taken.Edges.Weight(findedge(G.taken, 'Calgary', 'Winnipeg')) = turn; % 6
G.taken.Edges.Weight(findedge(G.taken, 'Winnipeg', 'Duluth')) = turn; % 4
[points, bestdist] = addlongestroad(G, info);
if ~all(points == [0 10 0] & bestdist == [3 14 0])
    failed(G, turn, test)
end

% test: loop
turn = 3;
test = test + 1;
G.taken.Edges.Weight(findedge(G.taken, 'Boston', 'Montreal')) = turn; % 2
G.taken.Edges.Weight(findedge(G.taken, 'Montreal', 'New York')) = turn; % 3
G.taken.Edges.Weight(findedge(G.taken, 'New York', 'Boston')) = turn; % 2
[points, bestdist] = addlongestroad(G, info);
if ~all(points == [0 10 0] & bestdist == [3 14 7])
    failed(G, turn, test)
end

% test: loop + tail
turn = 3;
test = test + 1;
G.taken.Edges.Weight(findedge(G.taken, 'Sault St. Marie', 'Montreal')) = turn; % 5
G.taken.Edges.Weight(findedge(G.taken, 'Sault St. Marie', 'Duluth')) = turn; % 3
[points, bestdist] = addlongestroad(G, info);
if ~all(points == [0 0 10] & bestdist == [3 14 15])
    failed(G, turn, test)
end

% test: tie
turn = 3;
G.taken.Edges.Weight(findedge(G.taken, 'Sault St. Marie', 'Duluth')) = 0; % -3
G.taken.Edges.Weight(findedge(G.taken, 'Sault St. Marie', 'Toronto')) = turn; % 2
[points, bestdist] = addlongestroad(G, info);
if ~all(points == [0 10 10] & bestdist == [3 14 14])
    failed(G, turn, test)
end

% test: 1-1 fork
turn = 1;
test = test + 1;
G.taken.Edges.Weight(findedge(G.taken, 'Calgary', 'Helena')) = turn; % 4
G.taken.Edges.Weight(findedge(G.taken, 'Helena', 'Duluth')) = turn; % 6
G.taken.Edges.Weight(findedge(G.taken, 'Helena', 'Denver')) = turn; % 4
[points, bestdist] = addlongestroad(G, info);
if ~all(points == [0 10 10] & bestdist == [13 14 14])
    failed(G, turn, test)
end

% test: 2-1 fork
turn = 1;
test = test + 1;
G.taken.Edges.Weight(findedge(G.taken, 'Duluth', 'Chicago')) = turn; % 3
[points, bestdist] = addlongestroad(G, info);
if ~all(points == [10 0 0] & bestdist == [16 14 14])
    failed(G, turn, test)
end

% test: long fork
turn = 1;
test = test + 1;
G.taken.Edges.Weight(findedge(G.taken, 'Chicago', 'Pittsburgh')) = turn; % 3
G.taken.Edges.Weight(findedge(G.taken, 'Denver', 'Oklahoma City')) = turn; % 4
G.taken.Edges.Weight(findedge(G.taken, 'Oklahoma City', 'Dallas')) = turn; % 2
G.taken.Edges.Weight(findedge(G.taken, 'Dallas', 'Houston')) = turn; % 1
G.taken.Edges.Weight(findedge(G.taken, 'New Orleans', 'Houston')) = turn; % 2
G.taken.Edges.Weight(findedge(G.taken, 'New Orleans', 'Miami')) = turn; % 6
[points, bestdist] = addlongestroad(G, info);
if ~all(points == [10 0 0] & bestdist == [31 14 14])
    failed(G, turn, test)
end

% test: third fork
turn = 1;
test = test + 1;
G.taken.Edges.Weight(findedge(G.taken, 'Oklahoma City', 'El Paso')) = turn; % 5
[points, bestdist] = addlongestroad(G, info);
if ~all(points == [10 0 0] & bestdist == [31 14 14])
    failed(G, turn, test)
end

% test: looping fork
turn = 1;
test = test + 1;
G.taken.Edges.Weight(findedge(G.taken, 'Oklahoma City', 'Santa Fe')) = turn; % 3
G.taken.Edges.Weight(findedge(G.taken, 'El Paso', 'Santa Fe')) = turn; % 2
[points, bestdist] = addlongestroad(G, info);
if ~all(points == [10 0 0] & bestdist == [41 14 14])
    failed(G, turn, test)
end

% test: non-included looping fork
turn = 1;
test = test + 1;
G.taken.Edges.Weight(findedge(G.taken, 'Oklahoma City', 'El Paso')) = 0; % -5
G.taken.Edges.Weight(findedge(G.taken, 'Dallas', 'El Paso')) = turn; % 4
[points, bestdist] = addlongestroad(G, info);
if ~all(points == [10 0 0] & bestdist == [38 14 14])
    failed(G, turn, test)
end

% test: long complicated track
% 
% 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
disp('passed all unit tests')
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


function failed(G, turn, testnum)

figure(2), clf
h = plot(G.taken);
h.EdgeLabel = G.taken.Edges.Weight;
title('Taken by Player Index')

figure(3), clf
j = plot(G.distance);
j.EdgeLabel = G.distance.Edges.Weight .* (G.taken.Edges.Weight == turn);
title(sprintf('Distances of Tracks Taken by Player %d', turn))

error(['Failed test ' num2str(testnum)])

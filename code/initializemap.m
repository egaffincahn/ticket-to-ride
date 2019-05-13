function G = initializemap()

map = importmap;
G.taken = graph(map.from, map.to, 0);
% G.turns = graph(map.from, map.to, 1);
G.distance = graph(map.from, map.to, map.distance);
G.color = graph(map.from, map.to, map.color);
% G.parallel = graph(map.from, map.to, map.parallel);
% G.points = graph(map.from, map.to, calcpoints(map.distance));
% G.weighted = graph(map.from, map.to, map.distance ./ calcpoints(map.distance));

% function points = calcpoints(distances)
% 
% points = nan(size(distances));
% points(distances == 6) = 15;
% points(distances == 5) = 10;
% points(distances == 4) = 7;
% points(distances == 3) = 4;
% points(distances == 2) = 2;
% points(distances == 1) = 1;

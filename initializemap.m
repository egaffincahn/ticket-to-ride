function G = initializemap()

map = importmap;
[G.taken, G.distance, G.points, G.color, G.parallel, G.weighted] = deal(graph(map.from, map.to, 0));
G.distance.Edges.Weight = map.distance;
G.color.Edges.Weight = map.color;
G.parallel.Edges.Weight = map.parallel;
G.points.Edges.Weight = calcpoints(map.distance);
G.weighted.Edges.Weight = map.distance ./ calcpoints(map.distance);


function points = calcpoints(distances)

points = nan(size(distances));
points(distances == 6) = 15;
points(distances == 5) = 10;
points(distances == 4) = 7;
points(distances == 3) = 4;
points(distances == 2) = 2;
points(distances == 1) = 1;

function s = strategy(G, cards)


edges = G.distance.Edges.EndNodes;
cities = G.distance.Nodes;

nnodes = G.distance.numnodes;
nedges = G.distance.numedges;
ngoals = height(cards.goalcards);
ncolors = 9; % 8 colors plus wild
nfeatures = 3;
npickgoal = 1;
npickface = 5;
npickrand = 1;

featureunits = 500; % per feature type (color, distance, owner)
fullunits = 1000;
compressionunits = 100;
decisionunits = npickgoal + npickface + npickrand + nedges;

% weights onto the feature layer
s.color = rande([2 * ncolors + nedges + 1, featureunits]); % colors in hand, in faceup, and track colors
s.distance = rande([nedges + 1, featureunits]);
s.taken = rande([nedges + 1, featureunits]);

% weights onto city layer
for i = 1:nnodes % number of units in this layer = number of cities = number of graph nodes
    nodeonedge = any(ismember(edges, cities.Name{i}), 2); % if this node (city) is on this edge
    nodeingoal = any(ismember([cards.goalcards.from, cards.goalcards.to], cities.Name{i}), 2); % if this node is in the goal card
    s.cities(:,i) = [rande(1); ...
        rande([nedges,1]) .* nodeonedge; ... % weights from edge units (color) to city units
        rande([nedges,1]) .* nodeonedge; ... % weights from edge units (length) to city units
        rande([nedges,1]) .* nodeonedge; ... % weights from edge units (player) to city units
        rande([ngoals,1]) .* nodeingoal; ... % weights from goal cards (points) to city units
        ];
end

% weights on the fully connected layers
s.full1 = rande([featureunits * nfeatures + nnodes + 1, fullunits]);
s.compression = rande([fullunits + 1, compressionunits]);
s.full2 = rande([compressionunits + 1, fullunits]);

% weights onto the output decision layer
s.decisions = rande([fullunits + 1, decisionunits]);

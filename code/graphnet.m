function actionvalues = graphnet(W, G, cards, info, turn)

% state (inputs)
nnodes = G.distance.numnodes;
nedges = G.distance.numedges;
ngoals = height(cards.goalcards);
nedgefeatures = 3; % edge features: distance, color, owner
nnodefeatures = ngoals;
X_in = zeros(nnodes, nnodefeatures);
for i = 1:nnodefeatures
    if cards.goalcards.player(i) == turn
        noderows = ismember(table2cell(G.distance.Nodes), table2cell(cards.goalcards(i,1:2)));
        X_in(noderows, i) = cards.goalcards.value(i);
    end
end

E = zeros(nnodes, nnodes, nedgefeatures);
E(:,:,1) = full(adjacency(G.distance, 'weighted'));
E(:,:,2) = full(adjacency(G.color, 'weighted'));
E(:,:,3) = E(:,:,3) + full(adjacency(G.taken, 'weighted')) == turn;
for i = find(1:info.players ~= turn)
    E(:,:,3) = E(:,:,3) - i * (full(adjacency(G.taken, 'weighted')) == i);
end
E = normalize(E);

% eq (7)
W(turn).features = rande([nnodefeatures, nnodefeatures]);
a = 0;
for p = 1:nedgefeatures
    
    out(:,:,p) = E(:,:,p) * X_in * W(turn).features;
    
%     %     a = alpha(X, E(:,:,p));
%     for i = 1:nnodes
%         for j = 1:nnodes
%             f = exp(relu(...
%                 [X(i,:) * W(turn).features, X(j,:) * W(turn).features], ...
%                 a));
%             a(i,j,p) = f(X(i,:), X(j,:)) * E(i,j,p);
%         end
%     end
%     a(:,:,p) = normalize(a(:,:,p));
end
keyboard


% % state (inputs)
% handcolors = sum(cards.hand{turn} == (0:8)', 2);
% facecolors = sum(cards.faceup == (0:8)', 2);
% input.cards = [handcolors; facecolors];
% 
% % feature layer
% % layer.features = tanh([ ...
% %     [1; zcards(input.cards); zcolor(input.color)]' * W(turn).color, ...
% %     [1; zdistance(input.distance)]' * W(turn).distance, ...
% %     [1; ztaken(input.taken)]' * W(turn).taken]);
% 
% % city layer
% layer.cities = tanh(...
%     [1; zcolor(input.color); zdistance(input.distance); ztaken(input.taken); zgoals(input.goals)]' * W(turn).cities);
% 
% % fully connected layers
% full1 = tanh(...
%     [1, layer.features, layer.cities] * W(turn).full1);
% 
% compression = tanh(...
%     [1, full1] * W(turn).compression);
% 
% full2 = relu(...
%     [1, compression] * W(turn).full2);
% 
% % figure out what options are allowed
% npickgoal = 1;
% npickface = 5;
% npickrand = 1;
% nheader = npickgoal + npickface + npickrand;
% nedges = length(input.distance);
% 
% available = [...
%     true(nheader, 1); ...
%     true(nedges, 1)]';
% 
% if sum(cards.goalcards.player == 0) < 3 % not allowed to take new goal cards
%     available(1) = false;
% end
% 
% for i = 1:nedges
%     if input.taken(i) > 0 % already taken
%         available(i + nheader) = false;
%         continue
%     end
%     if input.distance(i) > info.pieces(turn) % not enough pieces
%         available(i + nheader) = false;
%         continue
%     end
%     nneeded = input.distance(i);
%     solidcolors = handcolors(2:end) + handcolors(1);
%     if input.color(i) == 0 && all(nneeded > solidcolors) % don't have enough of any color (grey track)
%         available(i + nheader) = false;
%     end
%     if input.color(i) > 10 % don't have enough of the two options of color
%         if nneeded > solidcolors(rem(input.color(i), 10)) || ...
%                 nneeded > solidcolors(floor(input.color(i) / 10))
%             available(i + nheader) = false;
%         end
%     end
%     if input.color(i) < 10 && input.color(i) > 0 && ... % don't have enough of the color
%             nneeded > solidcolors(input.color(i))
%         available(i + nheader) = false;
%     end
% end
% 
% % output
% z = [1, full2] * W(turn).decisions;
% actionvalues = zeros(size(z));
% tic
% while ~any(actionvalues > 0)
%     z(~available) = -Inf;
%     probabilities = softmax(z - max(z));
%     actionvalues = probabilities .* available;
%     if toc > 5
%         keyboard
%     end
% end


function a = alpha(x, e, a)
if nargin < 3; a = 1; end
nnodes = size(x,1);
for i = 1:nnodes
    for j = 1:nnodes
        a(i,j) = f(x(i,:), x(j,:)) * e(i,j);
    end
end
a = normalize(a);


function g = relu(z, a)
if nargin < 2; a = 0; end
g = max(z, z * a);


function g = softmax(z)
g = exp(z) ./ sum(exp(z));

% function z = zcolor(x)
% z = (x - 4.5) / 4.5;
% 
% function g = zcards(z)
% g = (z - 5) / 5;
% 
% function z = zdistance(x)
% z = (x - 3.5) / 3.5;
% 
% function z = ztaken(x)
% z = x - 2;
% 
% function z = zgoals(x)
% z = (x - 11.5) / 11.5;


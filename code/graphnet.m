function actionvalues = graphnet(W, G, cards, info, turn)

% state (inputs)
nnodes = G.distance.numnodes;
nedges = G.distance.numedges;
ngoals = height(cards.goalcards);
nedgefeatures = 3; % edge features: distance, color, owner
nnodefeatures = ngoals;
X = zeros(nnodes, nnodefeatures);
for i = 1:nnodefeatures
    if cards.goalcards.player(i) == turn
        noderows = ismember(table2cell(G.distance.Nodes), table2cell(cards.goalcards(i,1:2)));
        X(noderows, i) = cards.goalcards.value(i);
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

adj = full(adjacency(G.distance));
for l = 1:4
    subplot(2,3,l), mesh(X)
    W(turn).features(:,:,l,1) = rande([nnodefeatures, nnodefeatures]); % Wi
    W(turn).features(:,:,l,2) = rande([nnodefeatures, nnodefeatures]); % Wj
    [X, E] = layer(X, E, W(turn).features(:,:,l,:), adj);
end
subplot(2,3,l+1), mesh(X)


% % state (inputs)
handcolors = sum(cards.hand{turn} == (0:8)', 2);
facecolors = sum(cards.faceup == (0:8)', 2);
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


function a = attention(xi, xj, Wi, Wj)
a = exp((xi * Wi) * (xj * Wj)');


function g = relu(z, a)
if nargin < 2; a = 0; end
g = max(z, z * a);


function [X_, E_] = layer(X, E, W, adj)

nnodes = size(X,1);
nnodefeatures = size(X,2);
nedgefeatures = size(E,3);

% from eq (3) of Gong & Cheng (2018) v1
% calculate alpha, the attention coefficient from X, E
alpha = nan(size(E));
for j = 1:nnodes
    C = zeros(nnodes,nedgefeatures) + sqrt(eps);
    for i = 1:nnodes
        for p = 1:nedgefeatures
            f = attention(X(i,:), X(j,:), W(:,:,:,1), W(:,:,:,2));
            if adj(i,j)%any(j == neighbors(G.distance, i))
                C(i,p) = C(i,p) + sum(f * E(i,j,p));
            end
            alpha(i,j,p) = f * E(i,j,p);
        end
    end
    alpha(:,j,:) = squeeze(alpha(:,j,:)) ./ C;
end

% from eq (1) of Gong & Cheng (2018) v1
% calculate X(l) from alpha and X(l-1)
X_ = nan(size(X));
for i = 1:nnodes
    a = zeros(1,nnodefeatures);
    for p = 1:nedgefeatures
        for j = find(adj(i,:))%neighbors(G.distance, i)'
            a = a + alpha(i,j,p) * X(j,:) * W(:,:,:,2);
        end
        ap(:,p) = a; % ... save these for concatenation function
    end
    X_(i,:) = relu(mean(ap,2)); % how can I concatenate these? dimensions don't make sense
end

E_ = alpha;

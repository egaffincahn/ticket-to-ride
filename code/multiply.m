function s = multiply(s, players)

parents = randperm(length(s));
nchildren = (players - 1) * 2;
fnames = fieldnames(s);

for i = 1:length(parents)/2
    p1 = s((i-1)*2+1);
    p2 = s(i*2);
    child = p1; % initialize child to parent 1's weights
    for c = 1:nchildren
        for f = 1:length(fnames)
            sz = size(p1.(fnames{f}));
            weights = child.(fnames{f});
            
            % randomly choose which weights will come from parent 2
            inherit = logical(round(rand(sz))); % which weights
            parentweights = p2.(fnames{f}); % all of parent 2's weights
            weights(inherit) = parentweights(inherit); % re-assign the randomly chosen weights
            
            % mutate some weights
            mutations = rand(sz) < .01;
            weights(mutations) = randn(sum(mutations(:)),1);
            
            child.(fnames{f}) = weights;
        end
        s(end+1) = child;
    end
end


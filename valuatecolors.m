function colorvals = valuatecolors(G, edgevals)

trackcolors = [floor(G.color.Edges.Weight / 10), mod(G.color.Edges.Weight, 10)]; % two columns to accommodate the parallel tracks
singles = ~trackcolors(:,1) & trackcolors(:,2); % tracks where there's only a single color
trackcolors(singles, 1) = trackcolors(singles, 2); % duplicate the track colors where there's only 1

colorvals = zeros([1, 8]);
for color = 1:length(colorvals)
    valsfromcolor = bsxfun(@times, trackcolors == color, edgevals); % take all the tracks of that color and multiply by 
    colorvals(color) = sum(valsfromcolor(:)); % taked weighted sum of the values of the color
end

% based on s, prefer hoarding a single color or not (the more you have, the more you value)

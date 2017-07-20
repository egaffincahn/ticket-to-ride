function edgevals = valuateedges(G, goals)

% decide:
    % minimizing distance?
    % maximizing points?
    % do we want a high ratio points:distance (hard) or low (easy)?


    edgevals = exprnd(2, [height(G.color.Edges), 1]);
    edgevals(G.taken.Edges.Weight > 0) = 0;
    
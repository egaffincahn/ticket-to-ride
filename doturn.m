function [G, cards, goals, goalcards, pieces, points] = doturn(turn, G, cards, goals, goalcards, pieces, points, s)

edgevals = valuateedges(G, goals);
turnover = false; % whether a track has been placed (when turn is over)
usewild = false; % pick is valued high enough to warrant using wildcards
anyhavevalue = false; % whether any track has high enough value to place

while ~turnover
    
    [value, pick] = max(edgevals); % find the highest valued track
    
    if value < 2 && ~anyhavevalue % pick new goal cards, exciting!
        [goals{turn}, goalcards] = pickgoals(goals{turn}, goalcards, s);
    elseif value > 10 || length(cards.hand{turn}) > (110-30)/length(cards.hand)
        track = G.color.Edges(pick,:); % the highest valued track
        trackcolor = track.Weight; % the color index of that track
        [colorcounts, colorindices] = hist(cards.hand{turn}, 0:8); % how many of each color does player have
        needed = G.distance.Edges.Weight(pick); % cards needed for the distance
        
        % figure out how many of the color(s) needed are in hand
        if trackcolor > 10 % two color options
            inhand = 0; % how many of that color player has
            for choicecolor_temp = [floor(trackcolor / 10), mod(trackcolor, 10)] % scroll between the two colors
                inhand_temp = colorcounts(choicecolor_temp == colorindices); % how many of the color the player has
                if inhand_temp > inhand % if it's more
                    inhand = inhand_temp; % save the number of the colors
                    choicecolor = choicecolor_temp; % and save the color to use
                end
            end
        elseif trackcolor > 0 % one regular color option
            inhand = colorcounts(trackcolor == colorindices);
            choicecolor = trackcolor;
        else % grey - any option
            % (1) currently choosing the first color with the minimum
            % requirements [NOT SURE THAT'S TRUE] (2) option for color with
            % most number (3) option for color with fewest that covers the
            % distance but with lowest value from valuatecolors()
            choicecolor = find(colorcounts(colorindices > 0) >= needed, 1, 'first');
            if isempty(choicecolor)
                inhand = 0;
            else
                inhand = colorcounts(choicecolor == colorindices);
            end
        end
        
        % check hand against how many are needed
        if inhand >= G.distance.Edges.Weight(pick) && pieces(turn) >= G.distance.Edges.Weight(pick) % yay, laying a track!
            ind = find(cards.hand{turn} == choicecolor, needed, 'first'); % indices of the first N cards of the color to use
            [G, cards, pieces, points] = laytrack(G, turn, pick, cards, ind, pieces, points);
            turnover = true;
        else % don't have enough with standard colors
            if value > 15 && sum(inhand | cards.hand{turn}==0) > needed && ~usewild % if have enough cards including the wilds and value is high and this is the max value (only do this once)
                wilds = find(cards.hand{turn} == 0);
                ind = [find(inhand), wilds(1:length(needed)-sum(inhand))];
                usewild = true; % only use wild on best
            end
            edgevals(pick) = 0; % set the pick's value to 0 so we don't choose it again
            anyhavevalue = true;
        end
    elseif usewild % value of must current choice is medium/low but there's another with high value worth using wilds on
        [G, cards, pieces, points] = laytrack(G, turn, pick, cards, ind, pieces, points);
        turnover = true;
    else % taking cards yay
        cards = pickcards(turn, cards, s);
        turnover = true;
    end
end




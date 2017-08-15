function [G, cards, info, memory] = doturn(turn, G, cards, info, memory, s)

% plotgraph(turn, G, cards, info)

if ~all(memory(turn).taken.Edges.Weight == G.taken.Edges.Weight) || info.rounds == 0 % only valuate edges if something changed
    memory(turn).edgevals = valuateedges(turn, G, cards, info, s);
end
edgevals_temp = memory(turn).edgevals; % create temporary duplicate to delete certain edges if player doesn't have the cards for them
turnover = false; % whether a track has been placed (when turn is over)
usewild = false; % pick is valued high enough to warrant using wildcards
anyhavevalue = false; % whether any track has high enough value to place
beta = [-1 .05 .001 .2];

while ~turnover
    
    [value, pick] = max(edgevals_temp); % find the highest valued track
    considerations = [1, length(cards.hand{turn}), value, info.players];
    
    if value < .1 && ~anyhavevalue && height(cards.goalcards) > 0 && all(info.pieces > 15) % pick new goal cards, exciting!
        cards = pickgoals(turn, cards, s);
        turnover = true;
    elseif (1 / (1 + exp(-beta * considerations'))) > rand
%     elseif value > 10 || length(cards.hand{turn}) > (110-30)/length(cards.hand) && value > 0
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
        if inhand >= G.distance.Edges.Weight(pick) && info.pieces(turn) >= G.distance.Edges.Weight(pick) % yay, laying a track!
            ind = find(cards.hand{turn} == choicecolor, needed, 'first'); % indices of the first N cards of the color to use
            [G, cards, info] = laytrack(G, turn, pick, cards, ind, info);
            turnover = true;
        else % don't have enough with standard colors
            if value > 15 && sum(inhand | cards.hand{turn}==0) > needed && ~usewild % if have enough cards including the wilds and value is high and this is the max value (only do this once)
                wilds = find(cards.hand{turn} == 0);
                ind = [find(inhand), wilds(1:length(needed)-sum(inhand))];
                usewild = true; % only use wild on best
            end
            edgevals_temp(pick) = -1; % set the pick's value to -1 so we don't choose it again
            anyhavevalue = true;
        end
    elseif usewild % value of must current choice is medium/low but there's another with high value worth using wilds on
        [G, cards, info] = laytrack(G, turn, pick, cards, ind, info);
        turnover = true;
    elseif length([cards.deck, cards.discards] > 1) %#ok<ISMT> % taking cards yay
        cards = pickcards(turn, G, memory, cards, s);
        turnover = true;
    else
        warning('Not enough cards')
    end
end




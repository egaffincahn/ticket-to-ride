function [G, cards, info] = doturn(turn, G, cards, info, s, doplot)

turnover = false;
cardcount = 0;
trycount = 0;
while ~turnover
    trycount = trycount + 1;
    if trycount > 5 % sorry buddy, skipping your turn
        break
    end
    
   actionvalues = graphnet(s, G, cards, info, turn);
    if cardcount > 0
        actionvalues([1, 8:end]) = 0; % have to take second card
        actionvalues(find(cards.faceup == 0) + 1) = 0; % cannot be a wild card
    end
    if isempty(cards.deck) || length(cards.faceup) < 5
        actionvalues(2:7) = 0; % not allowed to take cards if there aren't enough
        if cardcount > 0 % sorry, not enough cards to take a second one
            break
        end
    end
    if all(actionvalues <= 0)
        s(turn) = strategy(G, cards); % doturn doesn't return the strategy, so this change is only temporary
        continue
    end
    [~,action] = max(actionvalues);
    
    if action == 1 % new goal cards!
        cards = pickgoals(turn, cards);
        break
    end
    
    if 2 <= action && action <= 6 % 5 faceup
        if cards.faceup(action-1) == 0
            cardcount = cardcount + 2;
        else
            cardcount = cardcount + 1;
        end
        cards = movecards(turn, cards, 'faceup', 'hand', action-1);
    end
    
    if action == 7 % random card from deck
        cards = movecards(turn, cards, 'deck', 'hand', 1);
        cardcount = cardcount + 1;
    end
    
    if action >= 8 % laying a track!
        pick = action - 7;
        track = G.color.Edges(pick,:); % the highest valued track
        trackcolor = track.Weight; % the color index of that track
        colorcounts = sum(cards.hand{turn} == (0:8)', 2); % how many of each color does player have
        needed = G.distance.Edges.Weight(pick);
        
        if trackcolor > 10 % two color options
            % for now take color we have the most of
            colorvec = colorcounts;
            colorvec(~ismember(0:8, [floor(trackcolor / 10), rem(trackcolor, 10)])) = 0;
            [~,colorind] = max(colorvec);
        elseif trackcolor > 0 % one regular color option
            colorind = trackcolor + 1;
        else % grey - any option
            % for now take color that we have most of
            [~,colorind] = max([0; colorcounts(2:end)]);
        end
        if colorcounts(colorind) < needed % need to use wild
            ind = [find(cards.hand{turn} == colorind-1), find(cards.hand{turn} == 0, needed-colorcounts(colorind))];
        else
            ind = find(cards.hand{turn} == colorind-1, needed, 'first');
        end
        [G, cards, info] = laytrack(G, turn, pick, cards, ind, info);
        break
    end
    
    if cardcount == 2
        break
    end
end

if nargin == 6 && doplot
    plotgraph(turn, G, cards, info)
end


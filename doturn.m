function [G, hand, deck, faceup, discards, goals, goalcards, pieces, points] = doturn(turn, G, hand, deck, faceup, discards, goals, goalcards, pieces, points, s)

% parameters that could control a player's gameplay:
% -how many cards to stash
%   -use as soon as you have
%   -calculate some urgency and spend based on that
%       -if one of your highly valued spots just got taken
%       -if someone is collecting a lot of a color and you need that color
%   -gather gather gather until some point and then spend at some rate
% -how to valuate different edges
%   -minimize distance
%   -maximize points
%   -ratio points:distance (high=hard) or (low=easy)
%   -based on valuation of other players' moves
% -how aggressive to be when discarding goal cards
%   -keep all
%   -keep one easy, one hard
%   -calculate some overlap measurement
% -when to get new goal cards
%   -asap
%   -only when finished
% -estimating others' valuation
%   -none
%   -based on colors they pick up
%   -based on tracks they placed
% -longest track
%   -go for it from beginning
%   -never go for it
%   -be adaptive: go for it if it's reasonable
%   -be adaptive: go for it if it's reasonable and no one else is competing
% -willingness to spend wildcards
%   -always
%   -based on time in game (low -> high)
%   -urgency to lay a track
% -urgency
%   -time in game
%   -your pieces left
%   -others' pieces left
%   -color you need being taken
%   -your valued tracks are taken
% -endgame
%   -when to prepare for endgame
%   -calculate number of turns needed
%   -calculate whether your tracks are completable
%   -...
% -memory of others' cards
%   -none
%   -only most recent
%   -all
%   -some combination, but stochastic

edgevals = valuateedges(G, goals);
turnover = false; % whether a track has been placed (when turn is over)
usewild = false; % pick is valued high enough to warrant using wildcards
anyhavevalue = false; % whether any track has high enough value to place

while ~turnover
    
    [value, pick] = max(edgevals); % find the highest valued track
    
    if value < 2 && ~anyhavevalue % pick new goal cards, exciting!
        [goals{turn}, goalcards] = pickgoals(goals{turn}, goalcards, s);
    elseif value > 10 || length(hand{turn}) > (110-30)/length(hand)
        track = G.color.Edges(pick,:); % the highest valued track
        trackcolor = track.Weight; % the color index of that track
        [colorcounts, colorindices] = hist(hand{turn}, 0:8); % how many of each color does player have
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
            ind = find(hand{turn} == choicecolor, needed, 'first'); % indices of the first N cards of the color to use
            [G, hand, deck, faceup, discards, pieces, points] = laytrack(G, turn, pick, hand, deck, faceup, discards, ind, pieces, points);
            turnover = true;
        else % don't have enough with standard colors
            if value > 15 && sum(inhand | hand{turn}==0) > needed && ~usewild % if have enough cards including the wilds and value is high and this is the max value (only do this once)
                wilds = find(hand{turn} == 0);
                ind = [find(inhand), wilds(1:length(needed)-sum(inhand))];
                usewild = true; % only use wild on best
            end
            edgevals(pick) = 0; % set the pick's value to 0 so we don't choose it again
            anyhavevalue = true;
        end
    elseif usewild % value of must current choice is medium/low but there's another with high value worth using wilds on
        [G, hand, deck, faceup, discards, pieces, points] = laytrack(G, turn, pick, hand, deck, faceup, discards, ind, pieces, points);
        turnover = true;
    else % taking cards yay
        [hand, deck, faceup, discards] = pickcards(turn, hand, deck, faceup, discards, s);
        turnover = true;
    end
end




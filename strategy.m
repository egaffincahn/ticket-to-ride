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
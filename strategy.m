function S = strategy(individuals, fixed)

if nargin < 2 || ~fixed
    
    iterativevaluation = mat2cell(round(rand(individuals,1)), ones(individuals,1));
    attemptvaluationoverlap = mat2cell(round(rand(individuals,1)), ones(individuals,1));
    betalaytrack = mat2cell(bsxfun(@times, randn(individuals,8), 1./(1:8)), ones(1,individuals));
    betaedgeweights = mat2cell(rand(individuals,7), ones(1,individuals));
    
else
    
    iterativevaluation = mat2cell(true(individuals,1), ones(individuals,1));
    attemptvaluationoverlap = mat2cell(true(individuals,1), ones(individuals,1));
    betalaytrack = mat2cell(repmat([2.2908,-0.8744,0.8499,-32.2597,-2.1707,10.0435,15.3447,-0.3456], [individuals, 1]), ones(1,individuals));
    betaedgeweights = mat2cell(repmat([1,1,.5,0,0,0,0], [individuals, 1]), ones(1,individuals));
    
end

% w = who;
% features = w(~ismember(w, {'individuals', 'fixed'}));
% 
% S = struct;
% for i = 1:length(features)
%     S(1:individuals).(features{i}) = eval(features{i});
% %     S = setfield(S, features{i}, eval(features{i}));
% end
S = struct('iterativevaluation', iterativevaluation, 'attemptvaluationoverlap', attemptvaluationoverlap, 'betalaytrack', betalaytrack, 'betaedgeweights', betaedgeweights);

% parameters that could control a player's gameplay:
% -how many cards to stash
%   -use as soon as you have
%   -calculate some urgency and spend based on that
%       -if one of your highly valued spots just got taken
%       -if someone is collecting a lot of a color and you need that color
%   -gather gather gather until some point and then spend at some rate
% -how to valuate different edges
%   -criteria
%       -minimize distance
%       -maximize points
%       -ratio points:distance (high=hard) or (low=easy)
%       -based on valuation of other players' moves
%   -finding paths
%       -just based on goals alone
%       -
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
% -what to do when all goals are completed
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


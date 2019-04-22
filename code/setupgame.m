function [G, cards, info] = setupgame(players)

G = initializemap;

cards = struct();
cards.goalcards = importgoals; % read goal cards in from the txt file
cards.deck = Shuffle([zeros([1, 14]), repmat(1:8, [1, 12])]); % 14 wilds, 12 of the rest
cards.hand = cell(1, players); % initialize each players cards as empty cell
cards.faceup =  [];
cards.discards = [];

info.pieces = 45 * ones([players, 1]); % number of trains each player has
info.points = zeros([1, players]); % initialize everyone to 0 points
info.players = players;
info.rounds = 0;

function p = logisticvaluation(ncards, value, players)

X0 = 1;
X1 = ncards/10;
X2 = value/100;
X3 = players;
X = [X0, X1, X2, X3, X1.*X2, X1.*X3, X2.*X3, X1.*X2.*X3];
% beta = [-3.1640;-0.6646;-6.1244;1.6200;8.2131;-1.1659;-6.6327;6.5577];
beta = [2.2908;-0.8744;0.8499;-32.2597;-2.1707;10.0435;15.3447;-0.3456];
p = 1 ./ (1 + exp(-X * beta));

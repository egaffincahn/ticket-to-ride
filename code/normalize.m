% doubly stochastic normalization
function E = normalize(E_hat)

nnodes = size(E_hat,1);
E = zeros(size(E_hat));

% https://github.com/gongliyu/expr-tf-EGNN/blob/master/awesomeml/graph.py
E_hat(E_hat == 0) = sqrt(eps);

% equations from Gong & Cheng (2018)
E_tilde = E_hat ./ sum(E_hat,2); % eq (1)
for i = 1:nnodes
    E(i,:,:) = sum(E_tilde(i,:,:) .* E_tilde ./ sum(E_tilde, 1), 2); % eq(2)
end
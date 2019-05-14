function normalize_unittest

%%% TEST 1 %%%
E_orig(:,:,1) = [0 10 20 30; 10 0 2 0; 20 2 0 1; 30 0 1 0];
E_orig(:,:,2) = [0 2 2 1; 2 0 3 0; 2 3 0 4; 1 0 4 0];
E_orig(:,:,3) = 0;

% auto
E_hat = E_orig;
E = normalize(E_hat);
E_auto = E;
assert(all(E(:) > 0), 'Not all greater than 0')
assert(all(almost_equal(sum(E,1), 1)), 'Rows don''t sum to 1')
assert(all(almost_equal(sum(E,2), 1)), 'Columns don''t sum to 1')

% manual
E_hat = E_orig;
E = normalize_manual(E_hat);
E_manual = E;
assert(all(E(:) > 0), 'Not all greater than 0')
assert(all(almost_equal(sum(E,1), 1)), 'Rows don''t sum to 1')
assert(all(almost_equal(sum(E,2), 1)), 'Columns don''t sum to 1')

% test against each other
assert(all(E_manual(:) == E_auto(:)), 'Auto not same as manual')

%%% TEST 2 %%%
E_orig = rand(30,30,5);

% auto
E_hat = E_orig;
E = normalize(E_hat);
E_auto = E;
assert(all(E(:) > 0), 'Not all greater than 0')
assert(all(almost_equal(sum(E,1), 1)), 'Rows don''t sum to 1')
assert(all(almost_equal(sum(E,2), 1)), 'Columns don''t sum to 1')

% manual
E_hat = E_orig;
E = normalize_manual(E_hat);
E_manual = E;
assert(all(E(:) > 0), 'Not all greater than 0')
assert(all(almost_equal(sum(E,1), 1)), 'Rows don''t sum to 1')
assert(all(almost_equal(sum(E,2), 1)), 'Columns don''t sum to 1')

% test against each other
assert(all(E_manual(:) == E_auto(:)), 'Auto not same as manual')


disp('passed all tests')

function z = almost_equal(x, y)
z = abs(x(:) - y(:)) < sqrt(eps);

function E = normalize_manual(E_hat)
nnodes = size(E_hat,1);
nfeatures = size(E_hat,3);
E_hat(E_hat == 0) = sqrt(eps);
E_tilde = E_hat ./ sum(E_hat, 2);
E = zeros(size(E_hat));
for i = 1:nnodes
    for j = 1:nnodes
        for p = 1:nfeatures
            for k = 1:nnodes
                numerator = E_tilde(i,k,p) * E_tilde(j,k,p);
                denominator = 0;
                for v = 1:nnodes
                    denominator = denominator + E_tilde(v,k,p);
                end
                E(i,j,p) = E(i,j,p) + numerator / denominator;
            end
        end
    end
end
function y = rande(sz)

sigma = 1 / sz(1);
if size(sz, 2) > 1
    sigma = 1 / sz(2);
end

y = randn(sz) * sigma;

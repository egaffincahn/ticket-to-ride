function str = timeremaining(n, N, tochandle, makestring)

if nargin < 3 || isempty(tochandle)
    dt = toc; % elapsed time
else
    dt = toc(tochandle);
end
T = dt * N / n; % total time
rt = T - dt; % remaining time
str = [0 0 0]; % initialize output remaining time: [hours minutes seconds]

hr = 3600;
min = 60;

if rt > hr % hours remaining
    str(1) = floor(rt / hr);
    rt = rt - hr*str(1);
end
if rt > min % minutes remaining
    str(2) = floor(rt / min);
    rt = rt - min*str(2);
end
str(3) = round(rt); % seconds remaining
if nargin == 4 && makestring
    str = sprintf('%d hours, %d minutes, %d seconds estimated remaining', str(1), str(2), str(3));
end

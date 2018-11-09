function kids = multiply(parents, nkids)

kids = struct();
fields = fieldnames(parents);
for k = 1:nkids
    for f = 1:length(fields)
        for i = 1:length(parents(1).(fields{f}))
            alpha = rand;
            parentvalues = [parents(1).(fields{f})(i), parents(2).(fields{f})(i)];
            if rand < .1
                s = strategy(1);
                kids(k).(fields{f})(i) = s.(fields{f})(i);
            elseif sum(parentvalues(1) == [0 1]) == 1 && sum(parentvalues(2) == [0 1]) == 1 % the gene is binary
                kids(k).(fields{f})(i) = parentvalues(round(alpha)+1); % choose parent at random
            else % the gene is continuous
                kids(k).(fields{f})(i) = parentvalues * [alpha; 1-alpha]; % linear combination of parents
            end
        end
    end
end

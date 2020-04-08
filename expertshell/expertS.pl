test(F,R) :- expert([temperature(very_low), light(high)],F,R). 

expert(Facts, NewFacts, Actions) :-
    findall(r(Pre,Post), rule(Pre,Post), Rules), %very expensive
    expert(Rules, Facts, NewFacts, Actions).

expert(Rules, Facts, NewFacts, Actions) :-
    solve(Rules, Facts, NewFacts),
    include(check,NewFacts, Actions).

check(X) :- functor(X,do,1).

solve([], F, F). %changed GB

solve([r(Pre, Post)|Rs], Facts, NewFacts) :-
    \+subset(Post,Facts), 
    subset(Pre,Facts),
    append(Post, Facts, Merged), %changed GB
    solve(Rs, Merged, NewFacts). %changed GB

solve([r(_, _)|Rs], Facts, NewFacts) :- %added GB
    solve(Rs, Facts, NewFacts). %added GB
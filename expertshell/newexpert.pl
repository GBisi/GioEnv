:-consult('rules-es').

test(F,R) :- expert([temperature(very_low), light(high)],F,R). 

expert(Facts, NewFacts, Actions) :-
    findall(r(Pre,Post), rule(Pre,Post), Rules), %very expensive
    expert(Rules, Facts, NewFacts, Actions).

expert(Rules, Facts, NewFacts, Actions) :-
    solve(Rules, Facts, NewFacts),
    include(check,NewFacts, DoActions),
    dewrap(DoActions,[],Actions).

check(X) :- functor(X,do,1).

dewrap([],A,A).
dewrap([H|T],Actions, NewActions) :-
    arg(1,H,X),
    dewrap(T,[X|Actions],NewActions).

solve([], F, F). %changed GB

solve([r(Pre, Post)|Rs], Facts, NewFacts) :-
    \+member(Post,Facts), 
    subset(Pre,Facts),
    append([Post], Facts, Merged), %changed GB
    solve(Rs, Merged, NewFacts). %changed GB

solve([r(_, _)|Rs], Facts, NewFacts) :- %added GB
    solve(Rs, Facts, NewFacts). %added GB
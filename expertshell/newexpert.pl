test(F,R) :- start_loop([temperature(very_low), light(high)],F,R). 

start_loop(Facts,NewFacts,Actions) :-
    findall(r(Pre,Post), rule(Pre,Post), Rules), %very expensive
    start_loop(Rules,Facts,NewFacts,Actions).

start_loop(Rules,Facts,NewFacts,Actions) :-
    expert(Rules,Facts,NF,_),
    loop(Rules,Facts, NF, TotalFacts),
    write('Total Facts: '),write(TotalFacts),nl,
    expert(Rules,TotalFacts,NewFacts,DoActions),
    dewrap(DoActions,[],Actions).

loop(Rules, PrevFacts, CurrentFacts, TotalFacts) :-
    write('Loop: '),write(CurrentFacts),nl,
    length(PrevFacts, PF),
    length(CurrentFacts,CF),
    PF=\=CF,
    expert(Rules,CurrentFacts, NewFacts, _),
    loop(Rules,CurrentFacts,NewFacts,TotalFacts).

loop(_,PrevFacts,CurrentFacts, CurrentFacts) :-
    write('EndLoop: '),write(CurrentFacts),nl,
    length(PrevFacts, PF),
    length(CurrentFacts,CF),
    PF=:=CF.

expert(Rules, Facts, NewFacts, Actions) :-
    solve(Rules, Facts, NewFacts),
    include(check,NewFacts, Actions).

check(X) :- functor(X,do,1).

dewrap([],A,A).
dewrap([H|T],Actions, NewActions) :-
    arg(1,H,X),
    dewrap(T,[X|Actions],NewActions).

solve([], F, F). %changed GB

solve([r(Pre, Post)|Rs], Facts, NewFacts) :-
    \+subset(Post,Facts), 
    subset(Pre,Facts),
    append(Post, Facts, Merged), %changed GB
    solve(Rs, Merged, NewFacts). %changed GB

solve([r(_, _)|Rs], Facts, NewFacts) :- %added GB
    solve(Rs, Facts, NewFacts). %added GB
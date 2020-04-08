test(F,R) :- resolve([temperature(very_low), light(high)],F,R). 
testRules(N,R) :- resolve([ rule([ temperature(very_low) ] , [ do(set_temperature(high)) ]), rule([ temperature(low), outdoor_temperature(very_low) ] , [ do(set_temperature(high)) ]), rule([ temperature(high), outdoor_temperature(very_high) ] , [ do(set_temperature(low)) ]), rule([ temperature(very_high) ] , [ do(set_temperature(low)) ]), rule([ light(low), outdoor_light(medium) ] , [ do(set_light(medium)) ]), rule([ light(low), outdoor_light(low) ] , [ do(set_light(high)) ]), rule([ light(medium), outdoor_light(low) ] , [ do(set_light(high)) ]), rule([ light(medium), outdoor_light(high) ] , [ do(set_light(medium)) ]), rule([ light(high), outdoor_light(high) ] , [ do(set_light(medium)) ]), rule([ light(high), outdoor_light(medium) ] , [ do(set_light(medium)) ]) ],[temperature(very_low),light(high)],N,R).

resolve(F,N,A) :-
    start_loop(F,N,A).

resolve(R,F,N,A) :-
    start_loop(R,F,N,A).


start_loop(Facts,NewFacts,Actions) :-
    findall(rule(Pre,Post), rule(Pre,Post), Rules), %very expensive
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

solve([rule(Pre, Post)|Rs], Facts, NewFacts) :-
    \+subset(Post,Facts), 
    subset(Pre,Facts),
    append(Post, Facts, Merged), %changed GB
    solve(Rs, Merged, NewFacts). %changed GB

solve([rule(_, _)|Rs], Facts, NewFacts) :- %added GB
    solve(Rs, Facts, NewFacts). %added GB
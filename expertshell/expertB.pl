test(F,R) :- 
    expert([ rule([ news ] , [ do(google)]),rule([ temperature(very_low) ] , [ do(set_temperature(high)) ,news]), rule([ temperature(low), outdoor_temperature(very_low) ] , [ do(set_temperature(high)) ]), rule([ temperature(high), outdoor_temperature(very_high) ] , [ do(set_temperature(low)) ]), rule([ temperature(very_high) ] , [ do(set_temperature(low)) ]), rule([ light(low), outdoor_light(medium) ] , [ do(set_light(medium)) ]), rule([ light(low), outdoor_light(low) ] , [ do(set_light(high)) ]), rule([ light(medium), outdoor_light(low) ] , [ do(set_light(high)) ]), rule([ light(medium), outdoor_light(high) ] , [ do(set_light(medium)) ]), rule([ light(high), outdoor_light(high) ] , [ do(set_light(medium)) ]), rule([ light(high), outdoor_light(medium) ] , [ do(set_light(medium)) ]) ],
    [temperature(very_low), light(high)],F,R). 

expert(Rules, Facts, NewFacts, Actions) :-
    print('Rules',Rules),
    print('Facts',Facts),
    solve(Rules, Facts, NewFacts),
    include(check, NewFacts, DoActions),
    dewrap(DoActions,[],Actions).

check(X) :- functor(X,do,1).

solve(Rules, Facts, NewFacts) :-
    %print('Loop',Facts),
    solve(Rules, Facts, NotAppliedRules, AppliedRules, NewFacts2),
    continue(Rules, Facts, NotAppliedRules, AppliedRules, NewFacts2, NewFacts).

continue(_, _, [], _, NewFacts, NewFacts).

continue(_, Facts, _, _, NewFacts, NewFacts) :-
    same(Facts,NewFacts).

continue(_, _, NotAppliedRules, _, NewFacts2, NewFacts) :-
    solve(NotAppliedRules, NewFacts2, NewFacts).

solve([], Facts, [], [], Facts).

solve([rule(Pre, Post)|Rules], Facts, NotAppliedRules, [rule(Pre, Post)|AppliedRules], NewFacts) :-
    \+subset(Post,Facts), 
    subset(Pre,Facts),
    append(Post, Facts, NewFacts2), 
    solve(Rules, NewFacts2, NotAppliedRules, AppliedRules, NewFacts). 

solve([rule(Pre, Post)|Rules], Facts, [rule(Pre, Post)|NotAppliedRules], AppliedRules, NewFacts) :-
    (subset(Post,Facts); 
    \+subset(Pre,Facts)),
    solve(Rules, Facts, NotAppliedRules, AppliedRules, NewFacts).


same([], []).
same([H1|R1], [H2|R2]):-
    H1 = H2,
    same(R1, R2).

dewrap([],A,A).
dewrap([H|T],Actions, NewActions) :-
    arg(1,H,X),
    dewrap(T,[X|Actions],NewActions).

print(X) :- write(X),nl,nl.
print(X,Y) :- write(X),write(': '),write(Y),nl,nl.


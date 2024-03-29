test(F,R) :- 
    expert([ 
    rule([ beautiful_day ] , [ suggest(open_windows) ]),
    rule([ outdoor_temperature(high) , outdoor_light(high) ] , [ beautiful_day , suggest(turn_off_light) ]),
        rule([ outdoor_temperature(high) , outdoor_light(medium) ] , [ beautiful_day ]),
        rule([ temperature(very_low) ] , [ do(set_temperature(high)) ]), 
        rule([ temperature(low), outdoor_temperature(very_low) ] , [ do(set_temperature(high)) ]), 
        rule([ temperature(high), outdoor_temperature(very_high) ] , [ do(set_temperature(low)) ]), 
        rule([ temperature(very_high) ] , [ do(set_temperature(low)) ]), 
        rule([ light(low), outdoor_light(medium) ] , [ do(set_light(medium)) ]), 
        rule([ light(low), outdoor_light(low) ] , [ do(set_light(high)) ]), 
        rule([ light(medium), outdoor_light(low) ] , [ do(set_light(high)) ]), 
        rule([ light(medium), outdoor_light(high) ] , [ do(set_light(medium)) ]), 
        rule([ light(high), outdoor_light(high) ] , [ do(set_light(medium)) ]), 
        rule([ light(high), outdoor_light(medium) ] , [ do(set_light(medium)) ])
    ],
    [temperature(high), light(high), outdoor_temperature(high),outdoor_light(high)],F,R
    ). 

expert(Rules, Facts, NewFacts, Actions) :-
    print('Rules',Rules),
    print('Facts',Facts),
    solve(Rules, Facts, NewFacts),
    include(check, NewFacts, DoActions),
    dewrap(DoActions,[],Actions).

solve(Rules, Facts, NewFacts) :-
    print('Loop',Facts),
    solve(Rules, Facts, NotAppliedRules, AppliedRules, NewFacts2),
    continue(Rules, Facts, NotAppliedRules, AppliedRules, NewFacts2, NewFacts).

continue(_, _, [], _, NewFacts, NewFacts).

continue(_, Facts, _, _, Facts, Facts).

continue(_, Facts, [N|Ns], _, NewFacts2, NewFacts) :-
    Facts \== NewFacts2,
    solve([N|Ns], NewFacts2, NewFacts).

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


check(X) :- functor(X,do,1).

dewrap([],A,A).
dewrap([H|T],Actions, NewActions) :-
    arg(1,H,X),
    dewrap(T,[X|Actions],NewActions).

print(X) :- write(X),nl,nl.
print(X,Y) :- write(X),write(': '),write(Y),nl,nl.


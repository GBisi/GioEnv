% START with test(R).

% test(R) :- solve([temperature(very_low)],R). doesn't work!

test(L) :- compute([temperature(very_low)],L).

compute(F,L) :-
    %retractall(do(_)), 
    solve(F,_), 
    do(L).

solve(Facts, Results) :-
    solve(Facts, [], Results).

solve(A,L,R) :-
    (
    rule(P,C),
    not_in(C,A),
    verify(P,A),  % cut here? Yes!
    conclude(A,L,C)
    );
    is_list(R),
    assertz(do(R)).

not_in(do(C),A) :-
    not(member(C,A)).

not_in(fact(C),A) :-
    not(member(C,A)).

conclude(A,L,do(C)) :-
    solve([C|A],[C|L],[C|L]).

conclude(A,L,fact(C)) :-
    solve([C|A],L,L).

verify([],_).

verify([H|T],A) :- 
    member(H,A),
    verify(T,A).
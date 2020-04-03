:- consult('rulebook.pl').

% START with test(R).

test(R) :- solve([temperature(very_low)],R).

solve(Facts, Results) :-
    solve(Facts, [], Results).

solve(_,_,R) :- 
    is_list(R),
    write(R),nl,nl.

solve(A,L,_) :-
    rule(P,C),
    not_in(C,A),
    verify(P,A),  % cut here? 
    conclude(A,L,C).

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
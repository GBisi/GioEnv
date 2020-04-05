:- consult('expert.pl').

mediate(Es, Superio, X) :-
    parse_es(Es,[], EsL),
    parse_su(Superio,[], SuL),
    merge_list(EsL,SuL,Me),
    compute(Me, X).


parse_es([],L,L).

parse_es([H|T],L,[es(H)|M]) :-
    parse_es(T,L,M).


parse_su([],L,L).

parse_su([H|T],L,[su(H)|M]) :-
    parse_su(T,L,M).


merge_list([],L,L ).

merge_list([H|T],L,[H|M]):-
    merge_list(T,L,M).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%% MEDIATOR.PL - MEDIAATE DIFFERENT EXPERT SYSTEMS %%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

/* Mediate conclusion from two different expert system.
It wrap an expert system allowing it to manage the conclusion
of different systems. 
It recives two lists of conclusion, remap the elements wrapping each into a particular predicate.
Then call the expert system with a list that merge the two initial list re-mapped.
*/

:- consult('expert.pl').

% mediate(Es, Superio, Conclusion): Es and Superio are the two lists in input.
% re-map each element of each list with a specific predicate: es(_) for the elements of the first list
% and su(_) for the second.
% Then call an expert system and return it's conclusion.
% Like expert.pl needs a list of rules.
mediate(Es, Superio, Conclusion) :-
    parse_es(Es,[], EsL), %re-map all the elements wrapping them into es(_)
    parse_su(Superio,[], SuL), %re-map all the elements wrapping them into su(_)
    merge_list(EsL,SuL,Me),
    compute(Me, Conclusion).

% parse_*(InputL, Support, OutputL): remap all the elements of the initial list wrapping them into a specific predicate.
% TO DO(?): only one parse function with the predicate in input
parse_es([],L,L).

parse_es([H|T],L,[es(H)|M]) :-
    parse_es(T,L,M).

parse_su([],L,L).

parse_su([H|T],L,[su(H)|M]) :-
    parse_su(T,L,M).

% merge_list(First,Second,Output): merge two lists.
merge_list([],L,L).

merge_list([H|T],L,[H|M]):-
    merge_list(T,L,M).
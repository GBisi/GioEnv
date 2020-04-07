%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%% EXPERT.PL - SIMPLE EXPERT SYSTEM %%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

/* Implements the business logic of an expert system.
It needs a list of rules.
The rules must have this form:
rule(Precondition,Conclusion).
Where Conclusion can be:
do(Something) or fact(Something).
If Conclusion has the first form means 
that the conclusion is an action that the system
suggest to do. 
Else the conclusion is only a fact that the system
assumes true.
*/
% TEST: Start with test(R).
test(R) :- solve([temperature(very_low)],R). 

query(solve(Facts, [], NewResults)). %very first time ever.

expert(Rules, Facts, NewFacts, Actions) :-
    solve(Rules, Facts, NewFacts),
    include(do(X), Facts, Actions).

solve([], _, _).
solve([r(Pre, Post)|Rs], Facts, NewFacts) :-
    \+member(Post,Facts), 
    subset(Pre,Facts), 
    merge(Post, Facts, NewFacts).

merge([],L,L).
merge([H|T],L,[H|M]):-
    merge(T,L,M).

/* % solve(Facts,Results): receives a list of Fact in input, 
% then applies the rules and return it's Results
solve(Facts, NewFacts) :-
    findall(r(Pre,Post), rule(Pre,Post), Rules), %very expensive
    solve(Rules, Facts, NewFacts).
 */
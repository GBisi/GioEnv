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
:- consult('rules-es').
test(R) :- solve([temperature(very_low)],R).

solve(Facts, NewResults) :-
    solve(Facts, [], NewResults).

solve(Facts, Results, NewResults) :-
    rule(Preconditions,Conclusion), %get a rule
    not_in(Conclusion,Facts), %if not inferred this conclusion
    subset(Preconditions,Facts), %verify if the preconditions are true  % cut here? Yes!
    append(Conclusion,Facts,NewFacts),
    conclude(NewFacts, Results, Conclusion, NewResults).

solve(_, _, _).

conclude(NewFacts, Results, do(Conclusion), NewResults) :-
    solve(NewFacts, [Conclusion|Results], NewResults).

conclude(NewFacts, Results, fact(Conclusion), NewResults) :-
    solve(NewFacts, Results, NewResults).

not_in(fact(Conclusion),Facts) :-
    \+member(Conclusion,Facts).

not_in(do(Conclusion),Facts) :-
    \+member(Conclusion,Facts).
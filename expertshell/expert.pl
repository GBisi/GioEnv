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

% test(R) :- solve([temperature(very_low)],R). doesn't work! doesn't return R.

test(L) :- compute([temperature(very_low)],L).

% compute(Facts,Results): receives a list of Fact in input, 
% then apllies the rules and return it's Results
compute(Facts,Results) :-
    %retractall(do(_)), % remove previous conclusion but doesn't work in problog.
    solve(Facts,_), 
    do(Results).

% solve(Facts,Results): receives a list of Fact in input, 
% then apllies the rules and return it's Results
solve(Facts, Results) :-
    solve(Facts, [], Results).

% solve(Facts,Context,Results): receives a list of Fact in input, 
% then apllies the rules and return it's Results. 
% Context saves temporary results
solve(Facts, Context, Results) :-
    (
    rule(Preconditions,Conclusion), %get a rule
    not_in(Conclusion,Facts), %if not inferred this conclusion
    verify(Preconditions,Facts), %verify if the preconditions are true  % cut here? Yes!
    conclude(Facts,Context,Conclusion) %infer that conclusion is true
    );
    is_list(Results), %maybe not useful
    assertz(do(Results)). %needs for compute

% not_in(Conclusion, Facts): Verify that the conclusion is not in the Facts already inferred
% it is necessary to decapsulate the conclusion because the facts in input are 
not_in(do(Conclusion),Facts) :-
    not(member(Conclusion,Facts)).

not_in(fact(Conclusion),Facts) :-
    not(member(Conclusion,Facts)).

% verify(Preconditions, Facts): verify that all the precondition in Preconditions are in Facts.
verify([],_).

verify([H|T],Facts) :- 
    member(H,Facts),
    verify(T,Facts).

% conclude(Facts, Context, Conclusion): add Conclusion in Facts, if Conclusion is in the do(_) form, 
% add Conclusion in Results and 
% call solve with the new info.
conclude(Facts,Context,do(Conclusion)) :-
    solve([Conclusion|Facts],[Conclusion|Context],[Conclusion|Context]).

conclude(Facts,Context,fact(Conclusion)) :-
    solve([Conclusion|Facts],Context,Context).
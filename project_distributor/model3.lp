
% SETTINGS
courses_per_student(1).
max_per_course(30).
min_per_course(10).
%hard_enforced_preference(false).
student(S) :- preference(S,_,_).
course(C) :- preference(_,C,_).

% Generate assignments only from valid domain
% Generate
%{ assignnew(S,C) } = 1 :- preference(S,C,_).


%#show assignnew/2.


{ assign(S,C,1) } :- preference(S,C,1).
{ assign(S,C,R) } :- preference(S,C,R), preference(S,C2,R + 1),
                     not assign(S,C2,R + 1 ).


:- { assign(S,C,_) } > K ,student(S) , courses_per_student(K).

% Minimize
%#minimize { R-1,S,C : assign(S,C,R) }.
#show assign/3.

:- student(S), not assign(S,_,_).


quality(rank(R),amount(N)) :- 
    assign(_,_,R),
    N = #count { S : assign(S,_,R) }.

#show quality/2.

#minimize { R*A : quality(rank(R), amount(A)) }.

:- not quality(rank(1),amount(_)).

count(C, Count) :- course(C), Count = #count { S : assign(S,C,_) }.

:- count(C, Count), Count < Min, min_per_course(Min), Count != 0.
:- count(C, Count), Count > Max, max_per_course(Max).
#show count/2.
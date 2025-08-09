% SETTINGS
courses_per_student(1).
max_student_per_course(30).
min_student_per_course(10).
hard_enforced_preference(false).
student(S) :- preference(S,_,_).
course(C) :- preference(_,C,_).

% Generate assignments only from valid domain
{ assign(S,C) } :- preference(S,C,1).
{ assign(S,C) } :- preference(S,C,R), preference(S,C2,R + 1), not assign(S,C2).


:- { assign(S,C) } > K ,student(S) , courses_per_student(K).

res(S,C,R) :- assign(S,C), preference(S,C,R).
% Minimize
#minimize { R-1,S,C : res(S,C,R) }.
#show res/3.

% Hard constraint %TODO: find soft constraint without major complexity
:- student(S), not assign(S,_).
% #minimize { 20,S,C : assign(S,C), not preference(S,C,_) }.


quality(rank(R),amount(N)) :- 
    res(_,_,R),
    N = #count { S : res(S,C,R) }.

#show quality/2.

:- count(C, Count), Count < MinStudents, min_student_per_course(MinStudents), Count != 0.
:- count(C, Count), Count > MaxStudents, max_student_per_course(MaxStudents).
count(C, Count) :- course(C), Count = #count { S : assign(S,C) }.
#show count/2.
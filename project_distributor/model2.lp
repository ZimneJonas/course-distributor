% SETTINGS
courses_per_student(1).
max_student_per_course(30).
min_student_per_course(10).
% hard_enforced_preference(false).
student(S) :- preference(S,_,_).
course(C) :- preference(_,C,_).

% Generate assignments only from valid domain
% old: { assign(S,C) } :- preference(S,C,R).
% optimized (but only works for 1 course per student)
{ assign(S,C,1) } :- preference(S,C,1).
{ assign(S,C,R) } :- preference(S,C,R), preference(S,C2,R + 1), not assign(S,C2).
% { assign(S,C,R) } :- preference(S,C,R).

:- { assign(S,C,R) } > K ,student(S) , courses_per_student(K).

% assign(S,C,R) :- assign(S,C,R), preference(S,C,R).
% Minimize
#minimize { R-1,S,C : assign(S,C,R) }.
#show assign/3.

% Hard constraint %TODO: find soft constraint without major complexity
:- student(S), not assign(S,_,_).
% #minimize { 20,S,C : assign(S,C), not preference(S,C,_) }.


quality(rank(R),amount(N)) :- 
    assign(_,_,R),
    N = #count { S : assign(S,C,R) }.

#show quality/2.

course_cancelt(C) :- { assign(S,C,R) : course(C) } = 0, course(C).
:- MinStudents > { assign(S,C,R) : course(C) } , min_student_per_course(MinStudents), course(C), not course_cancelt(C).
:- MaxStudents < { assign(S,C,R) : course(C) } , max_student_per_course(MaxStudents), course(C), not course_cancelt(C).

% :- count(C, Count), Count < MinStudents, min_student_per_course(MinStudents), Count != 0.
% :- count(C, Count), Count > MaxStudents, max_student_per_course(MaxStudents).
% count(C, Count) :- course(C), Count = #count { S : assign(S,C,R) }.
#show count/2.
% SETTINGS
courses_per_student(1).
max_student_per_course(30).
min_student_per_course(10).

% CHECKS
% enforce preferences are set correctly
:- preference(S,C,R), not student(S).
:- preference(S,C,R), not course(C).
:- preference(S,C,R), preference(S,C2,R2), C!=C2, R=R2.

% RULES
% generate possible assignments restricted to allowed pairs
{ assign(S,C) : course(C) } = K :- student(S), courses_per_student(K).

% count the number of students for each course
count(N, C):- #count { S : assign(S,C), course(C) } = N, course(C).

% check the max and min number of students per course
:- max_student_per_course(K), count(N, C), N > K.
:- min_student_per_course(K), count(N, C), N < K, N!=0.


% -20 penalty for out of preference assignments
preference(S,C,20) :- assign(S,C), not preference(S,C,_).

#minimize { R : assign(S,C), preference(S,C,R) }.

% #show assign/2.
#show count/2.


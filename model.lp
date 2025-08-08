% SETTINGS
courses_per_student(1).
max_student_per_course(30).
min_student_per_course(10).
hard_enforced_preference(false).
show_stats(true).

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
penalty(20) :- assign(S,C), not preference(S,C,_).
:- assign(S,C), not preference(S,C,_), hard_enforced_preference(true).


penalty(X) :- assign(S,C), preference(S,C,X).
#minimize { X : penalty(X) }.

% also show penalty for each assignment
res(S,C,R) :- assign(S,C), preference(S,C,R).
#show res/3.
#show count/2.

% Statistics
quality(rank(R2),amount(N)) :- #count { S : assign(S,C), preference(S,C,R), R2 = R } = N, preference(_,_,R2), show_stats(true).

#show quality/2.
#show count/2.


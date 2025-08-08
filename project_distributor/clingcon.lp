% CLINGCON VERSION - Much more efficient for numeric constraints

% SETTINGS  
courses_per_student(1).
max_student_per_course(30).
min_student_per_course(10).

% DOMAIN - Only generate where preferences exist
{ assign(S,C) } :- student(S), course(C), preference(S,C,_).

% CARDINALITY CONSTRAINTS (more efficient in clingcon)
&sum { assign(S,C) : course(C); preference(S,C,_) } = K :- student(S), courses_per_student(K).

% CAPACITY CONSTRAINTS (much more efficient than ASP aggregates)
&sum { assign(S,C) : student(S); preference(S,C,_) } >= Min :- 
    course(C), min_student_per_course(Min).

&sum { assign(S,C) : student(S); preference(S,C,_) } <= Max :- 
    course(C), max_student_per_course(Max).

% OPTIMIZATION - Direct minimize sum of preferences
&minimize { R*assign(S,C) : student(S), course(C); preference(S,C,R) }.

% OUTPUT
res(S,C,R) :- assign(S,C), preference(S,C,R).
count(C, Count) :- course(C), Count = #count { S : assign(S,C) }.

quality(rank(R),amount(N)) :- 
    preference(_,_,R),
    N = #count { S,C : res(S,C,R) }.

#show res/3.
#show count/2.
#show quality/2.

% OUTPUT
res(S,C,R) :- assign(S,C), preference(S,C,R).
count(C, Count) :- course(C), Count = #sum { assign(S,C) : student(S), preference(S,C,_) }.

quality(rank(R),amount(N)) :- 
    preference(_,_,R),
    N = #count { S,C : res(S,C,R) }.

#show res/3.
#show count/2.
#show quality/2.
% CLINGCON VERSION - Much more efficient for numeric constraints

% SETTINGS
courses_per_student(1).
max_student_per_course(30).
min_student_per_course(10).

% DOMAIN - Only generate where preferences exist
{ assign(S,C) } :- student(S), course(C), preference(S,C,_).

% CONSTRAINT VARIABLES
% Each assignment has a penalty variable
&dom { 1..20 } = penalty(S,C) :- student(S), course(C), preference(S,C,_).

% LINKING ASP WITH CONSTRAINT VARIABLES
% If assigned, penalty equals preference value; otherwise 0
penalty(S,C) = R :- assign(S,C), preference(S,C,R).
penalty(S,C) = 0 :- not assign(S,C), student(S), course(C), preference(S,C,_).

% CARDINALITY CONSTRAINTS (more efficient in clingcon)
&sum { assign(S,C) : course(C), preference(S,C,_) } = K :- student(S), courses_per_student(K).

% CAPACITY CONSTRAINTS (much more efficient)
&sum { assign(S,C) : student(S), preference(S,C,_) } >= Min :- 
    course(C), min_student_per_course(Min),
    #count { S : student(S), preference(S,C,_) } >= Min.

&sum { assign(S,C) : student(S), preference(S,C,_) } <= Max :- 
    course(C), max_student_per_course(Max).

% OPTIMIZATION (constraint programming optimization)
total_penalty = #sum { penalty(S,C) : student(S), course(C), preference(S,C,_) }.
&minimize { total_penalty }.

% OUTPUT
res(S,C,R) :- assign(S,C), preference(S,C,R).
count(C, Count) :- course(C), Count = #sum { assign(S,C) : student(S), preference(S,C,_) }.

quality(rank(R),amount(N)) :- 
    preference(_,_,R),
    N = #count { S,C : res(S,C,R) }.

#show res/3.
#show count/2.
#show quality/2.
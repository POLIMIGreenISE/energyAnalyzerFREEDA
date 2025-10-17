:- dynamic highConsumptionService/4.
:- dynamic highConsumptionConnection/5.

save_to_file([Facts, Path]) :-
    consult(Facts),
    allSuggested(Constraints),
    open(Path, write, Stream),
    write_results(Constraints, Stream),
    close(Stream).

allSuggested(Constraints) :-
    bagof(Constraint, suggested(Constraint), Constraints).

suggested(affinity(d(C,FC),d(S,FS),W)) :-
    deployedTo(C,FC,_), deployedTo(S,FS,_), dif(C,S),
    highConsumptionConnection(C,FC,S,FS,W).

suggested(avoid(d(C,FC),N,W)) :-
    highConsumptionService(C,FC,N,W).

suggested(delay(d(C,FC),H,W)) :-
    canbedelayed(C,FC,H,W).

write_results([], _).
write_results([Constraint | Tail], Stream) :-
    format(Stream, '~q.~n', [Constraint]),
    write_results(Tail, Stream).
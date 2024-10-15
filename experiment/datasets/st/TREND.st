FUNCTION_BLOCK TREND
VAR_INPUT
    X : REAL;
END_VAR_INPUT

VAR_OUTPUT
    Q : BOOL;
    TU : BOOL;
    TD : BOOL;
    D : REAL;
END_VAR_OUTPUT

VAR
    last_X : REAL;
END_VAR
TU := X > last_X;
TD := X < last_X;
Q := TU OR TD;
D := X - LAST_X;

last_X := X;



(* revision history
hm	21. aug. 2009	rev 1.0
	original version

*)
END_FUNCTION_BLOCK

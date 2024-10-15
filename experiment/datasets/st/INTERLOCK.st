FUNCTION_BLOCK INTERLOCK
VAR_INPUT
    I1 : BOOL;
    I2 : BOOL;
    TL : TIME;
END_VAR

VAR_OUTPUT
    Q1 : BOOL;
    Q2 : BOOL;
END_VAR

VAR
    T1 : TOF; // Timer Off Delay
    T2 : TOF; // Timer Off Delay
END_VAR
(* the input signal have a run delay to lockout the other input *)
T1(IN := I1, PT := TL);
T2(IN := I2, PT := TL);

Q1 := I1 AND NOT t2.Q;
Q2 := I2 AND NOT t1.Q;


(* revision history

hm	28 sep 2007		rev 1.0
	original version

*)
END_FUNCTION_BLOCK

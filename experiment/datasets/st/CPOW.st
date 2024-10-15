FUNCTION CPOW : derived
VAR_INPUT
    X: complex;
    Y: Complex;
END_VAR
CPOW := CEXP(CMUL(Y,CLOG(X)));


(* revision history
hm	21. feb 2008	rev 1.0
	original version

*)
END_FUNCTION

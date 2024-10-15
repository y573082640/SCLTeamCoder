FUNCTION CCOS : derived
VAR_INPUT
    X: complex;
END_VAR
CCOS := CCOSH(CSET(-X.im, X.re));


(* revision history
hm	21. feb 2008	rev 1.0
	original version

*)
END_FUNCTION

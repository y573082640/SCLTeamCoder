FUNCTION CSINH : derived
VAR_INPUT
    X: complex;
END_VAR
CSINH.re := sinH(X.re) * COS(X.im);
CSINH.im := cosH(X.re) * SIN(X.im);


(* revision history
hm	21. feb 2008	rev 1.0
	original version

*)
END_FUNCTION

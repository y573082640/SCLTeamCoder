FUNCTION CSIN : derived
VAR_INPUT
    X : COMPLEX;
END_VAR
CSIN.re := cosH(X.im) * SIN(X.re);
CSIN.im := sinH(X.im) * COS(X.re);


(* revision history
hm	21. feb 2008	rev 1.0
	original version

*)
END_FUNCTION

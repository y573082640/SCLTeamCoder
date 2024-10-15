FUNCTION CSQRT : derived
VAR_INPUT
    X : COMPLEX; // Input variable of type complex
END_VAR

VAR
    temp : REAL; // Local variable of type REAL
END_VAR
temp := HYPOT(x.re, x.im);
CSQRT.re :=  SQRT(0.5 * (temp + x.re));
CSQRT.im :=  sgn(x.im) * SQRT(0.5 * (temp - x.re));


(* revision history
hm	21. feb 2008	rev 1.0
	original version

*)
END_FUNCTION

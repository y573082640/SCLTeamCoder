FUNCTION CASINH : derived
VAR_INPUT
    X : Complex;
END_VAR

VAR
    Y : Complex;
END_VAR
y.re := (X.re - X.im)*(X.re + X.im) + 1.0;
y.im := 2.0 * X.re * X.im;
y    := CSQRT(y);
y.re := y.re + x.re;
y.im := y.im + x.im;
CASINH  := CLOG(y);



(* revision history
hm	21. feb 2008	rev 1.0
	original version


*)
END_FUNCTION

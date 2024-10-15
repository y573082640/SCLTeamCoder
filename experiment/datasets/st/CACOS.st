FUNCTION CACOS : derived
VAR_INPUT
    X : ARRAY[1..2] OF REAL; // Assuming 'complex' is represented as an array of two REAL numbers
END_VAR

VAR
    Y : ARRAY[1..2] OF REAL; // Assuming 'complex' is represented as an array of two REAL numbers
END_VAR
y := CACOSH(x);
CACOS.re := y.im;
CACOS.im := -y.re;



(* revision history
hm	21. feb 2008	rev 1.0
	original version


*)
END_FUNCTION

FUNCTION V3_SMUL : derived
VAR_INPUT
    A : Vector_3;
    M : REAL;
END_VAR
V3_SMUL.X := A.X * M;
V3_SMUL.Y := A.Y * M;
V3_SMUL.Z := A.Z * M;



(* revision history
hm		11 dec 2007	rev 1.0
	original version

*)
END_FUNCTION

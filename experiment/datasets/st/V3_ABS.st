FUNCTION V3_ABS : REAL
VAR_INPUT
    A : Vector_3;
END_VAR
V3_ABS := SQRT(A.X * A.X + A.Y * A.Y + A.Z * A.Z);


(* revision history
hm		11 dec 2007	rev 1.0
	original version

*)
END_FUNCTION

FUNCTION V3_ADD : derived
VAR_INPUT
    A : VECTOR_3; // Derived type Vector_3
    B : VECTOR_3; // Derived type Vector_3
END_VAR
V3_ADD.X := A.X + B.X;
V3_ADD.Y := A.Y + B.Y;
V3_ADD.Z := A.Z + B.Z;



(* revision history
hm		11 dec 2007	rev 1.0
	original version

*)
END_FUNCTION

FUNCTION_BLOCK B_TRIG
VAR_INPUT
    CLK : BOOL;
END_VAR

VAR_OUTPUT
    Q : BOOL;
END_VAR

VAR
    edge : BOOL;
END_VAR
Q := clk XOR edge;
edge := CLK;


(* revision history
hm		4. aug. 2006	rev 1.0
	original version

*)
END_FUNCTION_BLOCK

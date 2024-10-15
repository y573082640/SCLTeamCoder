FUNCTION_BLOCK SH
VAR_INPUT
    in : REAL;
    CLK : BOOL;
END_VAR

VAR_OUTPUT
    out : REAL;
    trig : BOOL;
END_VAR

VAR
    edge : BOOL;
END_VAR
IF clk AND NOT edge THEN
	out := in;
	trig := TRUE;
ELSE;
	trig := FALSE;
END_IF;
edge := clk;

(* revision history

hm 16.1.2007	rev 1.1
	added trig output

*)
END_FUNCTION_BLOCK

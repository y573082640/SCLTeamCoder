FUNCTION_BLOCK TUNE
// Input Variables
VAR_INPUT
    SET : BOOL;
    SU : BOOL;
    SD : BOOL;
    RST : BOOL;
    SS : REAL := 0.1; // initial value
    Limit_L : REAL; // no initial value
    LIMIT_H : REAL := 100.0; // initial value
    RST_val : REAL; // no initial value
    SET_val : REAL := 100.0; // initial value
    T1 : TIME := TIME#500ms; // initial value
    T2 : TIME := TIME#2s0ms; // initial value
    S1 : REAL := 2.0; // initial value
    S2 : REAL := 10.0; // initial value
END_VAR

// Output Variables
VAR_OUTPUT
    Y : REAL; // no initial value
END_VAR

// Local Variables
VAR
    tx : DWORD;
    start : DWORD;
    start2 : DWORD;
    state : INT;
    in : BOOL;
    step : REAL;
    SPEED : REAL;
    Y_start : REAL;
    Y_start2 : REAL;
END_VAR
(* read system time *)
tx := T_PLC_MS();

IF rst THEN
	Y := RST_val;
	state := 0;
ELSIF set THEN
	Y := SET_val;
	state := 0;
ELSIF state > 0 THEN
	(* key has been pushed state machine operating *)
	(* first read the correct input *)
	IF state = 1 THEN
		(* step up *)
		in := su;
	ELSE
		(* step down *)
		in := sd;
	END_IF;
	(* check for single step operation *)
	IF NOT in AND tx - start <= TIME_TO_DWORD(T1) THEN
		Y := Y_start + step;
		state := 0;
	(* check if fast ramp needs to be generated *)
	ELSIF in AND tx - start >= TIME_TO_DWORD(T2) THEN
		Y := Y_start2 + DWORD_TO_REAL(tx - start2) * s2 / speed;
	(* check if slow ramp needs to be generated *)
	ELSIF in AND tx - start >= TIME_TO_DWORD(T1) THEN
		Y := Y_start + DWORD_TO_REAL(tx - start - TIME_TO_DWORD(T1)) * S1 / speed;
		start2 := tx;
		Y_start2 := Y;
	ELSIF NOT in THEN
		state := 0;
	END_IF;
ELSIF su THEN
	(* slow step up *)
	state := 1;
	start := tx;
	step := ss;
	speed := 1000.0;
	Y_start := Y;
ELSIF sd THEN
	(* slow step down *)
	state := 2;
	start := tx;
	step := -ss;
	speed := -1000.0;
	Y_start := Y;
END_IF;

(* make sure output does not exceed limits *)
Y := LIMIT(LIMIT_L, Y, LIMIT_H);

(* revision history
hm	3.11.2007		rev 1.0
	original version

hm	16. mar. 2008	rev 1.1
	added type conversions to avoid warnings under codesys 3.0

hm	11. mar. 2009	rev 1.2
	real constants updated to new systax using dot																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																											

*)
END_FUNCTION_BLOCK

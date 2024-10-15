FUNCTION_BLOCK CLK_PULSE
VAR_INPUT
    PT : TIME;          (* Input for time *)
    N : INT;            (* Input for integer *)
    RST : BOOL;         (* Input for reset *)
END_VAR

VAR_OUTPUT
    Q : BOOL;           (* Output for status *)
    CNT : INT;         (* Output for count *)
    RUN : BOOL;         (* Output for running status *)
END_VAR

VAR
    tx : DWORD;         (* Local variable for DWORD *)
    tn : DWORD;         (* Local variable for DWORD *)
    init : BOOL;        (* Local variable for initialization flag *)
END_VAR
tx := T_PLC_MS();		(* read system *)
Q := FALSE;				(* reset Q we generate pulses only for one cycle *)
RUN := CNT < N;

IF NOT init OR RST THEN
	init := TRUE;
	CNT := 0;
	tn := tx - TIME_TO_DWORD(PT);
	RUN := FALSE;
ELSIF (cnt < N OR N = 0) AND tx - tn >= TIME_TO_DWORD(PT) THEN		(* generate a pulse *)
	CNT := CNT + 1;
	Q := TRUE;
	tn := tn + TIME_TO_DWORD(PT);
END_IF;



(* revision history
hm		4. aug 2006		rev 1.0
	original version

hm		17. sep 2007	rev 1.1
	replaced time() with T_PLC_S() for compatblity reasons

hm		16. feb. 2011	rev 1.2
	fixed an error when timer overflows 
*)
END_FUNCTION_BLOCK

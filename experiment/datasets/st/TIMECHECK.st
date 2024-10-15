FUNCTION TIMECHECK : BOOL
VAR_INPUT
    TD : TIME_OF_DAY;
    START : TIME_OF_DAY;
    STOP : TIME_OF_DAY;
END_VAR
IF stop < start THEN
	TIMECHECK := start <= TD OR TD < stop;
ELSE
	TIMECHECK := start <= TD AND TD < stop;
END_IF;



(* revision history
hm 19. jul. 2009	rev 1.0
	original release

*)
END_FUNCTION

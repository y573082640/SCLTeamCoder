FUNCTION LIST_GET : string
VAR_INPUT
    SEP : BYTE;
    POS : INT;
END_VAR

VAR_IN_OUT
    LIST : STRING(LIST_LENGTH);
END_VAR

VAR
    i : INT := 1;
    o : INT := 1;
    pt : POINTER TO ARRAY[1..LIST_LENGTH] OF BYTE;
    po : POINTER TO ARRAY[1..LIST_LENGTH] OF BYTE;
    cnt : INT := 0;
    c : BYTE;
END_VAR
pt := ADR(LIST);							(* load pointers *)
po := ADR(LIST_GET);

REPEAT
	c := pt^[i];
	IF cnt = pos THEN						(* copy element to output string *)
		IF c = SEP  THEN EXIT; END_IF;		(* next element stop copy and finish *)
		po^[o] := c;
		o := o + 1;
	ELSIF c = SEP THEN
		cnt := cnt + 1;
	END_IF;
	i := i + 1;
UNTIL
	(i = LIST_LENGTH) OR (c = 0)
END_REPEAT;
po^[o] := 0;						(* close the output string *)



(* revision histroy
hm	20. jun. 2008	rev 1.0
	original release

hm	19. jan. 2011	rev 1.1
	changed string(255) to strring(LIST_LENGTH)

hm	21. mar. 2011	rev 2.0
	all list elements start with SEP
*)
END_FUNCTION

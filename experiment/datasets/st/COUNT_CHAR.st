FUNCTION COUNT_CHAR : INT
VAR_INPUT
    str : STRING; // STRING_LENGTH can be predefined as per requirement
    chr : BYTE;
END_VAR

VAR
    l : INT;
    pt : POINTER TO BYTE;
    pos : INT;
END_VAR
PT := ADR(str);
l := LEN(str);
COUNT_CHAR := 0;
FOR pos := 1 TO l DO
	IF pt^ = CHR THEN COUNT_CHAR := COUNT_CHAR + 1; END_IF;
    PT := PT + 1;
END_FOR;


(* revision history
hm	29. feb 2008	rev 1.0
	original version

hm	29. mar. 2008	rev 1.1
	changed STRING to STRING(STRING_LENGTH)
*)
END_FUNCTION

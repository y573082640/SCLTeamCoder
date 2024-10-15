FUNCTION_BLOCK DRIVER_4
VAR_INPUT
    Toggle_Mode: BOOL;        // Input for toggle mode
    Timeout: TIME;           // Input for timeout duration
    SET: BOOL;               // Input for set command
    IN0: BOOL;               // Input for boolean signal 0
    IN1: BOOL;               // Input for boolean signal 1
    IN2: BOOL;               // Input for boolean signal 2
    IN3: BOOL;               // Input for boolean signal 3
    RST: BOOL;               // Input for reset command
END_VAR

VAR_OUTPUT
    Q0: BOOL;                // Output for boolean signal 0
    Q1: BOOL;                // Output for boolean signal 1
    Q2: BOOL;                // Output for boolean signal 2
    Q3: BOOL;                // Output for boolean signal 3
END_VAR

VAR
    d0: DRIVER_1;           // Local variable for driver 1 instance 0
    d1: DRIVER_1;           // Local variable for driver 1 instance 1
    d2: DRIVER_1;           // Local variable for driver 1 instance 2
    d3: DRIVER_1;           // Local variable for driver 1 instance 3
END_VAR
D0(Set:=set, in:=in0, rst:=rst, toggle_mode:=toggle_mode, timeout:=timeout);
D1(Set:=set, in:=in1, rst:=rst, toggle_mode:=toggle_mode, timeout:=timeout);
D2(Set:=set, in:=in2, rst:=rst, toggle_mode:=toggle_mode, timeout:=timeout);
D3(Set:=set, in:=in3, rst:=rst, toggle_mode:=toggle_mode, timeout:=timeout);
Q0 := D0.Q;
Q1 := D1.Q;
Q2 := D2.Q;
Q3 := D3.Q;


(* revision history
hm	2. jan 2008		rev 1.0
	original version

*)
END_FUNCTION_BLOCK

//      // verilator_coverage annotation
        // A signed 32x32 Multiplier utilizing SPM
        //
        // Copyright 2016, mshalan@aucegypt.edu
        
        `timescale    1ns/1ps
        `default_nettype    none
        
        module pm32 (
 000158     input wire          clk,
%000002     input wire          rst,
%000002     input wire          start,
%000000     input wire  [31:0]  mc,
%000000     input wire  [31:0]  mp,
%000001     output reg  [63:0]  p,
%000001     output wire         done,
%000000     input wire          op // not use for in design, but added for compatibility with tb
        );
%000002     wire        pw;
%000000     reg [31:0]  Y;
%000000     reg [7:0]   cnt, ncnt;
%000001     reg [1:0]   state, nstate;
        
            localparam  IDLE=0, RUNNING=1, DONE=2;
        
 000080     always @(posedge clk or posedge rst)
%000002         if(rst)
%000002             state  <= IDLE;
                else
 000078             state <= nstate;
        
%000001     always_comb
%000001         case(state)
%000001             IDLE    :   if(start) nstate = RUNNING; else nstate = IDLE;
%000005             RUNNING :   if(cnt == 64) nstate = DONE; else nstate = RUNNING;
 000059             DONE    :   if(start) nstate = RUNNING; else nstate = DONE;
%000000             default :   nstate = IDLE;
                endcase
        
 000079     always @(posedge clk)
 000079         cnt <= ncnt;
        
%000001     always_comb
%000001         case(state)
 000016             IDLE    :   ncnt = 0;
 000325             RUNNING :   ncnt = cnt + 1;
 000059             DONE    :   ncnt = 0;
%000000             default :   ncnt = 0;
                endcase
        
 000080     always @(posedge clk or posedge rst)
%000002         if(rst)
%000002             Y <= 32'b0;
%000001         else if((start == 1'b1))
%000001             Y <= mp;
 000012         else if(state==RUNNING)
 000065             Y <= (Y >> 1);
        
 000080     always @(posedge clk or posedge rst)
%000002         if(rst)
%000002             p <= 64'b0;
%000001         else if(start)
%000001             p <= 64'b0;
 000012         else if(state==RUNNING)
 000065             p <= {pw, p[63:1]};
        
%000002     wire y = (state==RUNNING) ? Y[0] : 1'b0;
        
            spm #(.SIZE(32)) spm32(
                .clk(clk),
                .rst(rst),
                .x(mc),
                .y(y),
                .p(pw)
            );
        
            assign done = (state == DONE);
        
        endmodule
        

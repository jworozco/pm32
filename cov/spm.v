//      // verilator_coverage annotation
        /*
            A Serial-Parallel Multiplier (SPM)
            Modeled after the design outlined by ATML for their
            AT6000 FPGA in application notes DOC0716 and DOC0529:
                - https://ww1.microchip.com/downloads/en/AppNotes/DOC0529.PDF
                - https://ww1.microchip.com/downloads/en/AppNotes/DOC0716.PDF
        
            Implemented by mshalan@aucegypt.edu, 2016
        */
        
        `timescale    1ns/1ps
        `default_nettype    none
        
        module spm #(parameter SIZE = 32)(
 000158     input wire              clk,
%000002     input wire              rst,
%000002     input wire              y,
%000000     input wire [SIZE-1:0]   x,
%000002     output wire             p
        );
%000000     wire [SIZE-1:1]     pp;
%000000     wire [SIZE-1:0]     xy;
        
            genvar i;
        
            CSADD csa0 (.clk(clk), .rst(rst), .x(x[0]&y), .y(pp[1]), .sum(p));
        
            generate
                for(i=1; i<SIZE-1; i=i+1) begin : gen_csa
                    CSADD csa (.clk(clk), .rst(rst), .x(x[i]&y), .y(pp[i+1]), .sum(pp[i]));
                end
            endgenerate
        
            TCMP tcmp (.clk(clk), .rst(rst), .a(x[SIZE-1]&y), .s(pp[SIZE-1]));
        
        endmodule
        
        
        // Carry Save Adder
        module CSADD(
 004898     input wire  clk,
 000062     input wire  rst,
%000002     input wire  x,
%000008     input wire  y,
 000010     output reg  sum
        );
        
%000000     reg sc;
        
            // Half Adders logic
%000000     wire hsum1, hco1;
            assign hsum1 = y ^ sc;
            assign hco1 = y & sc;
        
%000000     wire hsum2, hco2;
            assign hsum2 = x ^ hsum1;
            assign hco2 = x & hsum1;
        
 002480     always @(posedge clk or posedge rst) begin
 000062         if (rst) begin
 000062             sum <= 1'b0;
 000062             sc <= 1'b0;
                end
 002418         else begin
 002418             sum <= hsum2;
 002418             sc <= hco1 ^ hco2;
                end
            end
        endmodule
        
        // 2's Complement
        module TCMP (
 000158     input wire  clk,
%000002     input wire  rst,
%000000     input wire  a,
%000000     output reg  s
        );
        
%000000     reg z;
        
 000080     always @(posedge clk or posedge rst) begin
%000002         if (rst) begin
%000002             s <= 1'b0;
%000002             z <= 1'b0;
                end
 000078         else begin
 000078             z <= a | z;
 000078             s <= a ^ z;
                end
            end
        
        endmodule
        

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
    input  logic              clk,
    input  logic              rst,
    input  logic              y,
    input  logic [SIZE-1:0]   x,
    output logic              p
);
    logic [SIZE-1:1]     pp;
    logic [SIZE-1:0]     xy;

    genvar i;

    CSADD csa0 (.clk(clk), .rst(rst), .x(x[0]&y), .y(pp[1]), .sum(p));

    generate
        for(i=1; i<SIZE-1; i++) begin : gen_csa
            CSADD csa (.clk(clk), .rst(rst), .x(x[i]&y), .y(pp[i+1]), .sum(pp[i]));
        end
    endgenerate

    TCMP tcmp (.clk(clk), .rst(rst), .a(x[SIZE-1]&y), .s(pp[SIZE-1]));

endmodule


// Carry Save Adder
module CSADD(
    input  logic  clk,
    input  logic  rst,
    input  logic  x,
    input  logic  y,
    output logic  sum
);

    logic sc;

    // Half Adders logic
    logic hsum1, hco1;
    assign hsum1 = y ^ sc;
    assign hco1 = y & sc;

    logic hsum2, hco2;
    assign hsum2 = x ^ hsum1;
    assign hco2 = x & hsum1;

    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            sum <= 1'b0;
            sc <= 1'b0;
        end
        else begin
            sum <= hsum2;
            sc <= hco1 ^ hco2;
        end
    end
endmodule

// 2's Complement
module TCMP (
    input  logic  clk,
    input  logic  rst,
    input  logic  a,
    output logic  s
);

    logic z;

    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            s <= 1'b0;
            z <= 1'b0;
        end
        else begin
            z <= a | z;
            s <= a & ~z;  // Pulse only on first occurrence of a=1
        end
    end
endmodule

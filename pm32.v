// A signed 32x32 Multiplier utilizing SPM
//
// Copyright 2016, mshalan@aucegypt.edu

`timescale    1ns/1ps
`default_nettype    none
// verilator lint_off TIMESCALEMOD

module pm32 (
    input  logic          clk,
    input  logic          rst,
    input  logic          start,
    input  logic [31:0]   mc,
    input  logic [31:0]   mp,
    output logic [63:0]   p,
    output logic          done,
    input  logic          op // not use for in design, but added for compatibility with tb
);
    logic        pw;
    logic [31:0] Y;
    logic [7:0]  cnt, ncnt;
    logic [1:0]  state, nstate;

    typedef enum logic [1:0] {
        IDLE    = 2'b00,
        RUNNING = 2'b01,
        DONE    = 2'b10
    } state_t;

    always_ff @(posedge clk or posedge rst) begin
        if(rst)
            state <= IDLE;
        else
            state <= nstate;
    end

    always_comb begin
        case(state)
            IDLE    : nstate = start ? RUNNING : IDLE;
            RUNNING : nstate = (cnt == 64) ? DONE : RUNNING;
            DONE    : nstate = start ? RUNNING : DONE;
            default : nstate = IDLE;
        endcase
    end

    always_ff @(posedge clk or posedge rst) begin
        if(rst)
            cnt <= '0;
        else
            cnt <= ncnt;
    end

    always_comb begin
        case(state)
            IDLE    : ncnt = '0;
            RUNNING : ncnt = cnt + 1'b1;
            DONE    : ncnt = '0;
            default : ncnt = '0;
        endcase
    end

    always_ff @(posedge clk or posedge rst) begin
        if(rst)
            Y <= '0;
        else if(start)
            Y <= mp;
        else if(state == RUNNING)
            Y <= Y >> 1;
    end

    always_ff @(posedge clk or posedge rst) begin
        if(rst)
            p <= '0;
        else if(start)
            p <= '0;
        else if(state == RUNNING)
            p <= {pw, p[63:1]};
    end

    logic y;
    assign y = (state == RUNNING) ? Y[0] : 1'b0;

    spm #(.SIZE(32)) spm32(
        .clk(clk),
        .rst(rst),
        .x(mc),
        .y(y),
        .p(pw)
    );

    assign done = (state == DONE);

endmodule

// synthesis translate_off
// synthesis translate_on

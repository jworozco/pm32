CWD=$(shell pwd)
COCOTB_REDUCED_LOG_FMT=True
SIM ?= verilator
VERILOG_SOURCES = $(CWD)/spm.v $(CWD)/pm32.v
MODULE := test_my_dut
TOPLEVEL := pm32
TOPLEVEL_LANG := verilog
COCOTB_HDL_TIMEUNIT=1us
COCOTB_HDL_TIMEPRECISION=1us
EXTRA_ARGS += --coverage
include $(shell cocotb-config --makefiles)/Makefile.sim
include cleanall.mk

# test_my_design.py (extended)

import cocotb
from cocotb.triggers import FallingEdge, Timer
from cocotb.types import Bit,Logic, LogicArray


async def generate_clock(dut):
    """Generate clock pulses."""

    for cycle in range(300):
        dut.clk.value = 0
        await Timer(1, units="ns")
        dut.clk.value = 1
        await Timer(1, units="ns")

async def reset_dut(dut, duration_ns):
    """Start with reset asserted and then de-assert it"""
    dut.rst.value = 1
    await Timer(duration_ns, units="ns")
    dut.rst.value = 0
    dut.rst._log.debug("Reset complete")


@cocotb.test()
async def my_first_test(dut):

    await cocotb.start(generate_clock(dut))  # run the clock "in the background"
    await cocotb.start(reset_dut(dut, 3))    # run reset in the background after 3 cycles get out of reset

    dut.start.value = 0
    dut.mc.value = 0
    dut.mp.value = 0
    await Timer(5, units="ns")  # wr 10
    dut.start.value = 1
    dut.mp.value = 16
    dut.mc.value = 16

    await Timer(2, units="ns")  # wr 10
    dut.start.value = 0

    await Timer(150, units="ns")  # wait for multiplication to complete
    await FallingEdge(dut.clk)  # wait for falling edge/"negedge"

    assert int(dut.p.value) == 16*16, "p is not 16*16!"

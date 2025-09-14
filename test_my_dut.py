"""Test module for PM32 DUT using cocotb framework."""

import cocotb
from cocotb.triggers import FallingEdge, Timer


async def generate_clock(dut):
    """Generate clock pulses.

    Args:
        dut: Device under test instance
    """
    for cycle in range(300):
        dut.clk.value = 0
        await Timer(1, units="ns")
        dut.clk.value = 1
        await Timer(1, units="ns")


async def reset_dut(dut, duration_ns):
    """Start with reset asserted and then de-assert it.

    Args:
        dut: Device under test instance
        duration_ns: Duration of reset in nanoseconds
    """
    dut.rst.value = 1
    await Timer(duration_ns, units="ns")
    dut.rst.value = 0
    dut.rst._log.debug("Reset complete")


@cocotb.test()
async def my_first_test(dut):
    """First basic test for PM32 multiplier.

    Args:
        dut: Device under test instance
    """
    # run the clock "in the background"
    await cocotb.start(generate_clock(dut))
    # run reset in the background after 3 cycles get out of reset
    await cocotb.start(reset_dut(dut, 3))

    # Initialize inputs
    dut.start.value = 0
    dut.mc.value = 0
    dut.mp.value = 0
    await Timer(5, units="ns")

    # Start multiplication: 16 * 16 = 256
    dut.start.value = 1
    dut.mp.value = 16
    dut.mc.value = 16

    await Timer(2, units="ns")
    dut.start.value = 0

    # Wait for multiplication to complete (64 cycles + margin)
    await Timer(150, units="ns")
    await FallingEdge(dut.clk)  # wait for falling edge/"negedge"

    # Check result
    expected_result = 16 * 16
    actual_result = int(dut.p.value)
    assert actual_result == expected_result, (
        f"p is not 16*16! Expected: {expected_result}, "
        f"Got: {actual_result}")

"""Testbench utilities for PM32 multiplier verification."""

import enum
import logging

import cocotb
import pyuvm
from cocotb.clock import Clock
from cocotb.queue import Queue, QueueEmpty
from cocotb.triggers import ClockCycles, RisingEdge


@enum.unique
class Ops(enum.IntEnum):
    """Legal operations for the Design."""

    MUL = 1


def DutPrediction(A, B, op):
    """Python model of the Design.

    Args:
        A (int): First operand (32-bit)
        B (int): Second operand (32-bit)
        op (Ops): Operation to perform

    Returns:
        int: Result of the operation
    """
    assert isinstance(op, Ops), "The Design op must be of type Ops"

    def to_signed(val):
        """Convert unsigned to signed 32-bit value."""
        return val if val < 0x80000000 else val - 0x100000000

    A_s = to_signed(A)
    B_s = to_signed(B)
    if op == Ops.MUL:
        result = A_s * B_s
    return result


# Edit: Setting up logging using the logger variable, default on DEBUG mode
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def get_int(signal):
    """Convert a bus to an integer, turning a value of x or z to 0.

    Args:
        signal: Cocotb signal to convert

    Returns:
        int: Integer value of the signal
    """
    try:
        int_val = int(signal.value)
    except ValueError:
        int_val = 0
    return int_val


class DutBfm(metaclass=pyuvm.Singleton):
    """Bus Functional Model for PM32 DUT communication."""

    def __init__(self):
        """Initialize the BFM with DUT reference and queues."""
        self.dut = cocotb.top
        self.cmd_driver_queue = Queue(maxsize=1)
        self.cmd_mon_queue = Queue(maxsize=0)
        self.result_mon_queue = Queue(maxsize=0)

    async def reset(self):
        """Reset the DUT and initialize signals."""
        cocotb.start_soon(Clock(self.dut.clk, 1, units="ns").start())
        self.dut.rst.value = 1  # active high reset
        self.dut.mc.value = 0
        self.dut.mp.value = 0
        self.dut.op.value = 0
        self.dut.start.value = 0
        await ClockCycles(self.dut.clk, 2)
        self.dut.rst.value = 0
        await RisingEdge(self.dut.clk)

    async def result_mon(self):
        """Monitor the result bus for completed operations."""
        prev_done = 0
        while True:
            await RisingEdge(self.dut.clk)
            done = get_int(self.dut.done)
            if prev_done == 0 and done == 1:
                result = get_int(self.dut.p)
                self.result_mon_queue.put_nowait(result)
            prev_done = done

    async def cmd_mon(self):
        """Monitor the command signals for new operations."""
        prev_start = 0
        while True:
            await RisingEdge(self.dut.clk)
            start = get_int(self.dut.start)
            if start == 1 and prev_start == 0:
                cmd_tuple = (get_int(self.dut.mc),
                             get_int(self.dut.mp),
                             get_int(self.dut.op))
                self.cmd_mon_queue.put_nowait(cmd_tuple)
            prev_start = start

    async def cmd_driver(self):
        """Drive commands to the DUT when ready."""
        self.dut.start.value = 0
        self.dut.mc.value = 0
        self.dut.mp.value = 0
        self.dut.op.value = 0
        while True:
            await RisingEdge(self.dut.clk)
            st = get_int(self.dut.start)
            dn = get_int(self.dut.done)
            # Drive commands to the Design when start and done are 0
            if st == 0 and dn == 0:
                try:
                    (aa, bb, op) = self.cmd_driver_queue.get_nowait()
                    self.dut.mc.value = aa
                    self.dut.mp.value = bb
                    self.dut.op.value = op
                    self.dut.start.value = 1
                except QueueEmpty:
                    continue
            # If start is 1 check done
            elif st == 1 and dn == 0:
                self.dut.start.value = 0  # testing

    def start_tasks(self):
        """Start the BFM coroutines."""
        cocotb.start_soon(self.cmd_driver())
        cocotb.start_soon(self.cmd_mon())
        cocotb.start_soon(self.result_mon())

    async def get_cmd(self):
        """Get the next command from the monitor queue.

        Returns:
            tuple: Command tuple (mc, mp, op)
        """
        cmd = await self.cmd_mon_queue.get()
        return cmd

    async def get_result(self):
        """Get the next result from the monitor queue.

        Returns:
            int: Result value
        """
        result = await self.result_mon_queue.get()
        return result

    async def send_op(self, aa, bb, op):
        """Send an operation to the DUT.

        Args:
            aa (int): First operand
            bb (int): Second operand
            op (int): Operation code
        """
        command_tuple = (aa, bb, op)
        await self.cmd_driver_queue.put(command_tuple)

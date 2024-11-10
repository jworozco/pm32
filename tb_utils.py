import cocotb
from cocotb.triggers import ClockCycles, FallingEdge
from cocotb.queue import QueueEmpty, Queue
from cocotb.clock import Clock
import enum
import logging
import pyuvm


# Edit: Update the operation enumeration
@enum.unique
class Ops(enum.IntEnum):
    """Legal ops for the Design"""
    #ADD = 1
    #AND = 2
    #XOR = 3
    MUL = 1


# #### The design_prediction function

# Edit: The prediction function for the scoreboard
def DutPrediction(A, B, op):
    """Python model of the Design"""
    assert isinstance(op, Ops), "The Design op must be of type Ops"
    # if op == Ops.ADD:
    #     result = A + B
    # elif op == Ops.AND:
    #     result = A & B
    # elif op == Ops.XOR:
    #     result = A ^ B
    if op == Ops.MUL:
        result = A * B
    return result


# #### The logger

# Edit: Setting up logging using the logger variable, defut on DEBUG mode
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# ### Reading a signal value
# Edit: get_int() converts a bus to an integer
# turning a value of x or z to 0
def get_int(signal):
    try:
        int_val = int(signal.value)
    except ValueError:
        int_val = 0
    return int_val


# ## The DutBfm singleton
# ### Initializing the DutBfm object


# Edit: Initializing the DutBfm singleton
class DutBfm(metaclass=pyuvm.Singleton):
    def __init__(self):
        self.dut = cocotb.top
        self.cmd_driver_queue = Queue(maxsize=1)
        self.cmd_mon_queue = Queue(maxsize=0)
        self.result_mon_queue = Queue(maxsize=0)

# ### The reset coroutine

# Edit: Centralizing the reset function, check names of clk and rst
    async def reset(self):
        cocotb.start_soon(Clock(self.dut.clk, 1, units="ns").start())
        self.dut.rst.value = 1 # active high reset
        self.dut.mc.value = 0
        self.dut.mp.value = 0
        self.dut.op.value = 0
        self.dut.start.value = 0
        await ClockCycles(self.dut.clk, 2)
        self.dut.rst.value = 0
        await FallingEdge(self.dut.clk)

# ## The communication coroutines
# #### result_mon()

# Edit: Monitoring the result bus
    async def result_mon(self):
        prev_done = 0
        while True:
            await FallingEdge(self.dut.clk)
            done = get_int(self.dut.done)
            if prev_done == 0 and done == 1:
                result = get_int(self.dut.p)
                self.result_mon_queue.put_nowait(result)
            prev_done = done

# #### cmd_mon()
# Edit: Monitoring the command signals
    async def cmd_mon(self):
        prev_start = 0
        while True:
            await FallingEdge(self.dut.clk)
            start = get_int(self.dut.start)
            if start == 1 and prev_start == 0:
                cmd_tuple = (get_int(self.dut.mc),
                             get_int(self.dut.mp),
                             get_int(self.dut.op))
                self.cmd_mon_queue.put_nowait(cmd_tuple)
            prev_start = start

# #### driver()
# Edit: Driving commands on the falling edge of clk
    async def cmd_driver(self):
        self.dut.start.value = 0
        self.dut.mc.value = 0
        self.dut.mp.value = 0
        self.dut.op.value = 0
        while True:
            await FallingEdge(self.dut.clk)
            st = get_int(self.dut.start)
            dn = get_int(self.dut.done)
# Edit: Driving commands to the Design when
# start and done are 0
            if st == 0 and dn == 0:
                try:
                    (aa, bb, op) = self.cmd_driver_queue.get_nowait()
                    self.dut.mc.value = aa
                    self.dut.mp.value = bb
                    self.dut.op.value = op
                    self.dut.start.value = 1
                except QueueEmpty:
                    continue
# Edit: If start is 1 check done
            elif st == 1:
                self.dut.start.value = 0 # testing
                #if dn == 1:
                #    self.dut.start.value = 0

# ### Launching the coroutines using start_soon
# Edit: Start the BFM coroutines
    def start_tasks(self):
        cocotb.start_soon(self.cmd_driver())
        cocotb.start_soon(self.cmd_mon())
        cocotb.start_soon(self.result_mon())

# Edit: The get_cmd() coroutine returns the next command
    async def get_cmd(self):
        cmd = await self.cmd_mon_queue.get()
        return cmd

# Edit: The get_result() coroutine returns the next result
    async def get_result(self):
        result = await self.result_mon_queue.get()
        return result

# Edit: send_op puts the command into the command Queue
    async def send_op(self, aa, bb, op):
        command_tuple = (aa, bb, op)
        await self.cmd_driver_queue.put(command_tuple)

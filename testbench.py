"""PM32 testbench using pyUVM framework."""

import random

import cocotb
import pyuvm
from cocotb.triggers import ClockCycles
from pyuvm import *

# All testbenches use tb_utils, so store it in a central
# place and add its path to the sys path so we can import it
from tb_utils import DutBfm, Ops, DutPrediction  # noqa: E402


# # UVM sequences
# ## Driver

# Edit: The Driver refactored to work with sequences
class Driver(uvm_driver):
    """Driver class for sending operations to DUT."""

    def start_of_simulation_phase(self):
        """Initialize BFM during simulation start."""
        self.bfm = DutBfm()

    async def run_phase(self):
        """Main driver run phase."""
        await self.bfm.reset()
        self.bfm.start_tasks()
        while True:
            cmd = await self.seq_item_port.get_next_item()
            await self.bfm.send_op(cmd.mc, cmd.mp, cmd.op)
            self.seq_item_port.item_done()


# ## Connecting the driver to the sequencer
class DutEnv(uvm_env):
    """DUT environment containing all verification components."""

    # Edit: Instantiating the sequencer in the environment
    def build_phase(self):
        """Build all verification components."""
        self.seqr = uvm_sequencer("seqr", self)
        ConfigDB().set(None, "*", "SEQR", self.seqr)
        self.driver = Driver("driver", self)
        self.cmd_mon = Monitor("cmd_mon", self, "get_cmd")
        self.result_mon = Monitor("result_mon", self, "get_result")
        self.scoreboard = Scoreboard("scoreboard", self)
        self.coverage = Coverage("coverage", self)

    # Edit: Connecting the sequencer to the driver
    def connect_phase(self):
        """Connect all verification components."""
        self.driver.seq_item_port.connect(self.seqr.seq_item_export)
        self.cmd_mon.ap.connect(self.scoreboard.cmd_export)
        self.cmd_mon.ap.connect(self.coverage.analysis_export)
        self.result_mon.ap.connect(self.scoreboard.result_export)


# ## AluSeqItem
# Edit: Defining an ALU command as a sequence item
class AluSeqItem(uvm_sequence_item):
    """Sequence item for ALU operations."""

    def __init__(self, name, aa, bb, op):
        """Initialize sequence item with operands and operation."""
        super().__init__(name)
        self.mc = aa
        self.mp = bb
        self.op = Ops(op)

    # Edit: The __eq__ and __str__ methods in a sequence item
    def __eq__(self, other):
        """Check equality of sequence items."""
        same = (self.mc == other.mc and self.mp == other.mp and
                self.op == other.op)
        return same

    def __str__(self):
        """String representation of sequence item."""
        return (f"{self.get_name()} : mc: 0x{self.mc:02x} "
                f"OP: {self.op.name} ({self.op.value}) mp: 0x{self.mp:02x}")


# ## Creating sequences
# ### BaseSeq

# Edit: The BaseSeq contains the common body() method
class BaseSeq(uvm_sequence):
    """Base sequence class with common functionality."""

    async def body(self):
        """Execute sequence body with all operations."""
        for op in list(Ops):
            cmd_tr = AluSeqItem(
                "cmd_tr",
                16,
                16,
                op
            )
            await self.start_item(cmd_tr)
            self.set_operands(cmd_tr)
            await self.finish_item(cmd_tr)

    def set_operands(self, tr):
        """Set operands for the transaction. Override in subclasses."""
        pass


# ### RandomSeq and MaxSeq
# Edit: Extending BaseSeq to create the random and maximum stimulus
class RandomSeq(BaseSeq):
    """Sequence with random operands."""

    def set_operands(self, tr):
        """Set random operands."""
        tr.mc = random.randint(0, (2**16 - 1))
        tr.mp = random.randint(0, (2**16 - 1))


class MaxSeq(BaseSeq):
    """Sequence with maximum positive operands."""

    def set_operands(self, tr):
        """Set maximum positive operands."""
        tr.mc = 0x7fff_ffff
        tr.mp = 0x7fff_ffff


class MinSeq(BaseSeq):
    """Sequence with maximum negative operands."""

    def set_operands(self, tr):
        """Set maximum negative operands."""
        tr.mc = 0x8000_0000
        tr.mp = 0x8000_0000


# ## Starting a sequence in a test
# ### BaseTest

# Edit: All tests use the same environment and need a sequence
@pyuvm.test()
class BaseTest(uvm_test):
    """Base test class with common functionality."""

    def build_phase(self):
        """Build the test environment."""
        self.env = DutEnv("env", self)

    def end_of_elaboration_phase(self):
        """Get sequencer reference after elaboration."""
        self.seqr = ConfigDB().get(self, "", "SEQR")

    # Edit: All tests start the sequence
    async def run_phase(self):
        """Run the test sequence."""
        self.raise_objection()
        seq = BaseSeq.create("seq")
        await seq.start(self.seqr)
        await ClockCycles(cocotb.top.clk, 200)  # to do last transaction
        self.drop_objection()


# ### RandomTest and MaxTest
# Edit: Overriding BaseSeq to get random stimulus and all ones
@pyuvm.test()
class RandomTest(BaseTest):
    """Test with random operands."""

    def start_of_simulation_phase(self):
        """Override sequence type for random testing."""
        uvm_factory().set_type_override_by_type(BaseSeq, RandomSeq)


@pyuvm.test()
class MaxTest(BaseTest):
    """Test with maximum positive operands."""

    def start_of_simulation_phase(self):
        """Override sequence type for maximum testing."""
        uvm_factory().set_type_override_by_type(BaseSeq, MaxSeq)


@pyuvm.test()
class MinTest(BaseTest):
    """Test with maximum negative operands."""

    def start_of_simulation_phase(self):
        """Override sequence type for minimum testing."""
        uvm_factory().set_type_override_by_type(BaseSeq, MinSeq)


class Coverage(uvm_subscriber):
    """Coverage collector for functional coverage."""

    def end_of_elaboration_phase(self):
        """Initialize coverage set."""
        self.cvg = set()

    def write(self, cmd):
        """Collect coverage data from commands."""
        (_, _, op) = cmd
        self.cvg.add(op)

    def report_phase(self):
        """Report coverage results."""
        if len(set(Ops) - self.cvg) > 0:
            self.logger.error(
                f"Functional coverage error. Missed: {set(Ops) - self.cvg}")
            assert False
        else:
            self.logger.info("Covered all operations")
            assert True


class Scoreboard(uvm_component):
    """Scoreboard for checking DUT results."""

    def build_phase(self):
        """Build scoreboard FIFOs and ports."""
        self.cmd_fifo = uvm_tlm_analysis_fifo("cmd_fifo", self)
        self.result_fifo = uvm_tlm_analysis_fifo("result_fifo", self)
        self.cmd_get_port = uvm_get_port("cmd_get_port", self)
        self.result_get_port = uvm_get_port("result_get_port", self)
        self.cmd_export = self.cmd_fifo.analysis_export
        self.result_export = self.result_fifo.analysis_export

    def connect_phase(self):
        """Connect ports to FIFOs."""
        self.cmd_get_port.connect(self.cmd_fifo.get_export)
        self.result_get_port.connect(self.result_fifo.get_export)

    def check_phase(self):
        """Check results against predictions."""
        while self.result_get_port.can_get():
            _, actual_result = self.result_get_port.try_get()
            cmd_success, cmd = self.cmd_get_port.try_get()
            if not cmd_success:
                self.logger.critical(f"result {actual_result} had no command")
            else:
                (A, B, op_numb) = cmd
                op = Ops(op_numb)
                predicted_result = DutPrediction(A, B, op)
                if predicted_result == actual_result:
                    self.logger.info(
                        f"PASSED: 0x{A:02x} {op.name} 0x{B:02x} = "
                        f"0x{actual_result:04x}")
                else:
                    self.logger.error(
                        f"FAILED: 0x{A:02x} {op.name} 0x{B:02x} = "
                        f"0x{actual_result:04x} "
                        f"expected 0x{predicted_result:04x}")


class Monitor(uvm_component):
    """Monitor for observing interface signals."""

    def __init__(self, name, parent, method_name):
        """Initialize monitor with method name."""
        super().__init__(name, parent)
        self.bfm = DutBfm()
        self.get_method = getattr(self.bfm, method_name)

    def build_phase(self):
        """Build analysis port."""
        self.ap = uvm_analysis_port("ap", self)

    async def run_phase(self):
        """Monitor interface and write to analysis port."""
        while True:
            datum = await self.get_method()
            self.logger.debug(f"MONITORED {datum}")
            self.ap.write(datum)

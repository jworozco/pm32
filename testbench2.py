"""Testbench for PM32 multiplier using cocotb framework."""

import random

import cocotb

from tb_utils import DutBfm, DutPrediction, Ops, logger


class BaseTester():
    """Base class for all testers with common behavior."""

    async def execute(self):
        """Execute the test with different operations."""
        self.bfm = DutBfm()
        ops = list(Ops)
        for op in ops:
            aa, bb = self.get_operands()
            await self.bfm.send_op(aa, bb, op)
        # send two dummy operations to allow
        # last real operation to complete
        await self.bfm.send_op(0, 0, 1)
        await self.bfm.send_op(0, 0, 1)

    def get_operands(self):
        """Get operands for testing. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement get_operands()")


class RandomTester(BaseTester):
    """Tester that uses random operands."""

    def get_operands(self):
        """Generate random operands."""
        return random.randint(0, 255), random.randint(0, 255)


class MaxTester(BaseTester):
    """Tester that uses maximum operands."""

    def get_operands(self):
        """Generate maximum operands."""
        return 0xFF, 0xFF


class Scoreboard():
    """Scoreboard for collecting and checking test results."""

    def __init__(self):
        """Initialize the scoreboard."""
        self.bfm = DutBfm()
        self.cmds = []
        self.results = []
        self.cvg = set()

    async def get_cmds(self):
        """Collect commands from BFM."""
        while True:
            cmd = await self.bfm.get_cmd()
            self.cmds.append(cmd)

    async def get_results(self):
        """Collect results from BFM."""
        while True:
            result = await self.bfm.get_result()
            self.results.append(result)

    def start_tasks(self):
        """Launch data-gathering tasks."""
        cocotb.start_soon(self.get_cmds())
        cocotb.start_soon(self.get_results())

    def check_results(self):
        """Check results against predictions and coverage."""
        passed = True
        for cmd in self.cmds:
            aa, bb, op_int = cmd
            op = Ops(op_int)
            self.cvg.add(op)
            actual = self.results.pop(0)
            prediction = DutPrediction(aa, bb, op)
            if actual == prediction:
                logger.info(
                    f"PASSED: {aa:02x} {op.name} {bb:02x} = {actual:04x}")
            else:
                passed = False
                logger.error(
                    f"FAILED: {aa:02x} {op.name} {bb:02x} = {actual:04x}"
                    f" - predicted {prediction:04x}")

        # Check functional coverage
        if len(set(Ops) - self.cvg) > 0:
            logger.error(
                f"Functional coverage error. Missed: {set(Ops) - self.cvg}")
            passed = False
        else:
            logger.info("Covered all operations")
        return passed


async def execute_test(tester_class):
    """Execute a test with given tester class.

    Args:
        tester_class: Class of tester to instantiate and run

    Returns:
        bool: True if test passed, False otherwise
    """
    bfm = DutBfm()
    scoreboard = Scoreboard()
    await bfm.reset()
    bfm.start_tasks()
    scoreboard.start_tasks()

    # Execute the tester
    tester = tester_class()
    await tester.execute()
    passed = scoreboard.check_results()
    return passed


@cocotb.test()
async def random_test(_):
    """Test with random operands."""
    passed = await execute_test(RandomTester)
    assert passed


@cocotb.test()
async def max_test(_):
    """Test with maximum operands."""
    passed = await execute_test(MaxTester)
    assert passed

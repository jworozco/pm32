# PM32 Project - Design Specification

## Overview
The PM32 project implements a **32-bit signed serial multiplier** using the Serial Parallel Multiplier (SPM) algorithm. This design performs signed multiplication of two 32-bit operands over multiple clock cycles, producing a 64-bit result. The repository contains RTL design files, verification testbenches, and toolchain support for both simulation and physical implementation.

## Design Architecture

### Top-Level Module: pm32
The `pm32` module implements a finite state machine-controlled serial multiplier with the following interface:

#### Port Description
| Port | Direction | Width | Type | Description |
|------|-----------|-------|------|-------------|
| `clk` | Input | 1 | Wire | System clock |
| `rst` | Input | 1 | Wire | Active-high asynchronous reset |
| `start` | Input | 1 | Wire | Start multiplication operation |
| `mc` | Input | 32 | Wire (signed) | Multiplicand (32-bit signed) |
| `mp` | Input | 32 | Wire (signed) | Multiplier (32-bit signed) |
| `p` | Output | 64 | Reg (signed) | Product result (64-bit signed) |
| `done` | Output | 1 | Wire | Operation complete flag |
| `op` | Input | 1 | Wire | Operation select (unused, for TB compatibility) |

#### Operating Ranges
- **Input Range (mc, mp):** -2,147,483,648 to 2,147,483,647 (0x80000000 to 0x7FFFFFFF)
- **Output Range (p):** -4,611,686,018,427,387,904 to 4,611,686,018,427,387,903 (64-bit signed)

### State Machine
The multiplier operates using a 3-state FSM:

| State | Value | Description |
|-------|-------|-------------|
| `IDLE` | 0 | Waiting for start signal |
| `RUNNING` | 1 | Performing serial multiplication (64 cycles) |
| `DONE` | 2 | Operation complete, result available |

#### State Transitions
- `IDLE → RUNNING`: When `start` is asserted
- `RUNNING → DONE`: After 64 clock cycles (when `cnt == 64`)
- `DONE → RUNNING`: When `start` is asserted again
- `DONE → DONE`: When `start` is not asserted

### Serial Parallel Multiplier (SPM) Algorithm
The design uses a bit-serial approach where:
1. The multiplier (`mp`) is loaded into register `Y`
2. Each cycle, the LSB of `Y` is used to control partial product generation
3. The multiplicand (`mc`) is processed by the SPM module with the current multiplier bit
4. Results are accumulated by shifting the product register `p` right and inserting new partial products at the MSB
5. The process continues for 64 cycles to handle signed arithmetic properly

### Sub-Module: SPM
The SPM (Serial Parallel Multiplier) module performs the core partial product calculation:
- **Size Parameter:** Configurable width (32 bits for pm32)
- **Inputs:** `x` (multiplicand slice), `y` (multiplier bit), `clk`, `rst`
- **Output:** `p` (partial product bit)

## Timing Specifications

### Performance Characteristics
- **Latency:** 64 clock cycles per multiplication
- **Throughput:** 1 multiplication every 65+ cycles (including setup time)
- **Clock Frequency:** Design-dependent (limited by critical path in SPM module)

### Operation Sequence
1. **Setup Phase:** Assert `start` with valid `mc` and `mp` inputs
2. **Execution Phase:** 64 clock cycles of serial processing
3. **Completion Phase:** `done` asserted, result available on `p` output
4. **Next Operation:** New `start` pulse initiates next multiplication

### Timing Diagram
The following timing diagram illustrates the operation of the PM32 multiplier:

![PM32 Timing Diagram](timing_diagram.png)

The diagram shows:
- **Reset Phase:** System reset clears all registers
- **Setup Phase:** Input operands `mc` and `mp` are applied with `start` signal
- **Execution Phase:** 64 clock cycles of serial multiplication processing
- **Completion Phase:** `done` signal asserted with valid result on `p` output
- **Example:** `0x12345678 × 0x1BCDEF01 = 0x01F721C28B9C1A98`

## Verification Environment

### Testbench Architecture
The project includes comprehensive verification using:
- **cocotb:** Python-based RTL simulation framework
- **pyUVM:** SystemVerilog UVM methodology ported to Python
- **Verilator:** High-performance RTL simulator

### Test Scenarios
1. **RandomSeq:** Random 16-bit operands for basic functionality
2. **MaxSeq:** Maximum positive values (0x7FFFFFFF × 0x7FFFFFFF)
3. **MinSeq:** Maximum negative values (0x80000000 × 0x80000000)
4. **Directed Tests:** Specific corner cases and edge conditions

### Expected Results Validation
The testbench includes a Python reference model that:
- Converts unsigned inputs to signed 32-bit values using two's complement
- Performs reference multiplication: `result = A_signed × B_signed`
- Compares against DUT output for functional verification

## Implementation Details

### Resource Utilization
- **Registers:** Approximately 100+ flip-flops (state, counters, data path)
- **Logic:** Combinational logic for FSM, SPM core, and data path
- **Memory:** No external memory required

### Tool Support
- **Simulation:** Verilator with cocotb/pyUVM testbenches
- **Synthesis:** OpenLane2 RTL-to-GDS flow support
- **Configuration:** `config.json` for physical implementation

## Getting Started
To get started with this project, follow the steps below:

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/pm32.git
    ```
2. Navigate to the project directory:
    ```bash
    cd pm32
    ```
3. Run simulation:
    ```bash
    make
    ```

## Files Structure
- `pm32.v` - Top-level multiplier module
- `spm.v` - Serial Parallel Multiplier core
- `testbench.py` - pyUVM-based verification environment
- `test_my_dut.py` - Simple directed test
- `tb_utils.py` - Testbench utilities and reference model
- `timing_diagram.puml` - PlantUML timing diagram source
- `timing_diagram.png` - Generated timing diagram image
- `Makefile` - Simulation build configuration
- `config.json` - OpenLane2 synthesis configuration

## Contributing
Contributions are welcome! Please follow the steps below to contribute:

1. Fork the repository.
2. Create a new branch:
    ```bash
    git checkout -b feature-name
    ```
3. Commit your changes:
    ```bash
    git commit -m "Description of changes"
    ```
4. Push to the branch:
    ```bash
    git push origin feature-name
    ```
5. Open a pull request.

## License
This project is licensed under the MIT license. See the `LICENSE` file for details.


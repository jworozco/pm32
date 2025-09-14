# PM32 Project Commands Reference

This document provides a comprehensive list of commands for simulation, synthesis, and physical design implementation of the PM32 project.

## Simulation Commands

### Clean Build
```bash
make clean
```

### Run Simulation
```bash
make sim
```

### Run Simulation with Waveforms
```bash
make sim WAVES=1
```

> **Note:** Check the Makefile to change or update simulation parameters.

## Synthesis Commands

### Basic Synthesis
```bash
librelane config.json --to yosys.synthesis --run-tag synth_only
```

### Synthesis Exploration
```bash
librelane config.json --flow SynthesisExploration --run-tag synth_explore
```

## Static Timing Analysis (STA)

### Pre Place & Route STA
```bash
librelane config.json --to openroad.staprepnr --run-tag staprepnr
```

### Post Place & Route STA
```bash
librelane config.json --to openroad.stapostpnr --run-tag stapostpnr
```

## Physical Design Flow

### Floorplan
```bash
librelane config.json --to openroad.floorplan --run-tag floorplan
```

### View Floorplan
```bash
librelane --last-run --flow openinklayout config.json
```

### Power Distribution Network (PDN)
```bash
librelane config.json --to openroad.generatepdn --run-tag generatepdn
```

### I/O Placement
```bash
librelane config.json --to openroad.ioplacement --run-tag ioplacement
```

### Global Placement
```bash
librelane config.json --to openroad.globalplacement --run-tag globalplacement
```

### Detailed Placement
```bash
librelane config.json --to openroad.detailedplacement --run-tag detailedplacement
```

### Clock Tree Synthesis (CTS)
```bash
librelane config.json --to openroad.cts --run-tag cts
```

### Global Routing
```bash
librelane config.json --to openroad.globalrouting --run-tag globalrouting
```

### Detailed Routing
```bash
librelane config.json --to openroad.detailedrouting --run-tag detailedrouting
```

## Verification & Analysis

### Technology Design Rule Check (TDRC)
```bash
librelane config.json --to checker.trdrc --run-tag trdrc
```

### IR Drop Analysis
```bash
librelane config.json --to openroad.irdropreport --run-tag irdropreport
```

### Design Rule Check (DRC)
```bash
librelane config.json --to klayout.drc --run-tag drc
```

### SPICE Extraction
```bash
librelane config.json --to magic.spiceextraction --run-tag extraction
```

### Layout vs. Schematic (LVS)
```bash
librelane config.json --to checker.lvs --run-tag lvs
```

## Complete Flow

### Full RTL-to-GDS Flow
```bash
librelane config.json --run-tag full
```

## GUI Visualization

To run the GUI, execute the flow up to the desired state, then use one of the following commands:

### OpenROAD GUI
```bash
librelane --last-run --flow OpenInOpenROAD config.json
```

### KLayout GUI
```bash
librelane --last-run --flow OpenInKLayout config.json
```

## Command Flow Overview

The typical design flow follows this sequence:

1. **Synthesis** → **STA Pre-PnR** → **Floorplan** → **PDN** → **I/O Placement**
2. **Global Placement** → **Detailed Placement** → **CTS** → **Global Routing**
3. **Detailed Routing** → **TDRC** → **STA Post-PnR** → **IR Drop**
4. **DRC** → **Extraction** → **LVS**

Use the GUI commands at any stage to visualize the current design state.
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
openlane config.json --to yosys.synthesis --run-tag synth_only
```

### Synthesis Exploration
```bash
openlane config.json --flow SynthesisExploration --run-tag synth_explore
```

## Static Timing Analysis (STA)

### Pre Place & Route STA
```bash
openlane config.json --to openroad.staprepnr --run-tag staprepnr
```

### Post Place & Route STA
```bash
openlane config.json --to openroad.stapostpnr --run-tag stapostpnr
```

## Physical Design Flow

### Floorplan
```bash
openlane config.json --to openroad.floorplan --run-tag floorplan
```

### View Floorplan
```bash
openlane --last-run --flow openinklayout config.json
```

### Power Distribution Network (PDN)
```bash
openlane config.json --to openroad.generatepdn --run-tag generatepdn
```

### I/O Placement
```bash
openlane config.json --to openroad.ioplacement --run-tag ioplacement
```

### Global Placement
```bash
openlane config.json --to openroad.globalplacement --run-tag globalplacement
```

### Detailed Placement
```bash
openlane config.json --to openroad.detailedplacement --run-tag detailedplacement
```

### Clock Tree Synthesis (CTS)
```bash
openlane config.json --to openroad.cts --run-tag cts
```

### Global Routing
```bash
openlane config.json --to openroad.globalrouting --run-tag globalrouting
```

### Detailed Routing
```bash
openlane config.json --to openroad.detailedrouting --run-tag detailedrouting
```

## Verification & Analysis

### Technology Design Rule Check (TDRC)
```bash
openlane config.json --to checker.trdrc --run-tag trdrc
```

### IR Drop Analysis
```bash
openlane config.json --to openroad.irdropreport --run-tag irdropreport
```

### Design Rule Check (DRC)
```bash
openlane config.json --to klayout.drc --run-tag drc
```

### SPICE Extraction
```bash
openlane config.json --to magic.spiceextraction --run-tag extraction
```

### Layout vs. Schematic (LVS)
```bash
openlane config.json --to checker.lvs --run-tag lvs
```

## Complete Flow

### Full RTL-to-GDS Flow
```bash
openlane config.json --run-tag full
```

## GUI Visualization

To run the GUI, execute the flow up to the desired state, then use one of the following commands:

### OpenROAD GUI
```bash
openlane --last-run --flow OpenInOpenROAD config.json
```

### KLayout GUI
```bash
openlane --last-run --flow OpenInKLayout config.json
```

## Command Flow Overview

The typical design flow follows this sequence:

1. **Synthesis** → **STA Pre-PnR** → **Floorplan** → **PDN** → **I/O Placement**
2. **Global Placement** → **Detailed Placement** → **CTS** → **Global Routing**
3. **Detailed Routing** → **TDRC** → **STA Post-PnR** → **IR Drop**
4. **DRC** → **Extraction** → **LVS**

Use the GUI commands at any stage to visualize the current design state.
# PM32 Project

## Overview
The PM32 project corresponds to a logic circuit that does binary multiplication (32 bits). This repository contains all the necessary files, designs, and documentation related to the project. The code of the multiplier is coming from the openlane repo. The testbenches use cocotb, test_my_dut is simple directed test while testbench(2) use pyUVM to test the design.

## Features
- Binary Multiplier of 2 32 inputs mp, mc
- Multi cicle multiplication calculation
- Uses Start and Done to initiate operation and indicate completion.
- This repo uses verilator for simulation (Makefile) and openlane2 for RTL2GDS (config.json)
- Testbench uses cocotb and pyuvm

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


# Create clock constraints
create_clock -name clk -period 25.000 [get_ports {clk}]

# Create virtual clocks for input and output delay constraints
# set input and output delays
set_input_delay -clock clk -max 3 [get_ports {mc}]
set_input_delay -clock clk -min 0 [get_ports {mc}]

set_input_delay -clock clk -max 3 [get_ports {mp}]
set_input_delay -clock clk -min 0 [get_ports {mp}]

set_input_delay -clock clk -max 3 [get_ports {start}]
set_input_delay -clock clk -min 0 [get_ports {start}]


set_output_delay -clock clk -max 3 [get_ports {p}]
set_output_delay -clock clk -min 0 [get_ports {p}]

set_output_delay -clock clk -max 3 [get_ports {done}]
set_output_delay -clock clk -min 0 [get_ports {done}]
# Using an RC Controller

We can the original RC controller that came with the base car kit to control the car. 

# Pins on the Raspberry Pi

By default we connect the RC controller to the Raspberry Pi as follows:

- RC controller Steering PWM to GPIO 37 (Low Duty Cycle % turns right, High Duty Cycle % turns left)
- RC controller Throttle to GPIO 38 (Low Duty Cycle % goes backward, High Duty Cycle % goes forward)

## Custom RC controller class

controllers.wl_cars_rc_controller.py is a custom class that we can use to control the car using the RC controller. 

In the config refer to it as `wl_cars_rc_controller`
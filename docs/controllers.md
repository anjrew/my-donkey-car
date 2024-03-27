# Controllers

For the main documentation on using the controllers with Donkey Car, see [this](http://docs.donkeycar.com/parts/controllers/

# Custom Controllers

For custom controllers not natively supported by Donkey Car, you may need to create a custom controller class. See [this](http://docs.donkeycar.com/utility/donkey/#joystick-wizard) page for more information on creating a custom controller class via the joystick setup wizard.

## Ali Express controller
 
A cheap controller from Ali Express can be found [here](https://www.aliexpress.us/item/32824692489.html?gatewayAdapt=4itemAdapt).
The custom controller class for this controller can be found [here](../controllers/ali_express_controller.py)

## Xbox 1

See [this](http://docs.donkeycar.com/parts/controllers/) link and the section of XBox One Controller Pairing

##  Logitech F710

This controller is a good choice for the Donkey Car. It is wireless and has a good range. It also has a switch to change between XInput and DirectInput modes. The DirectInput mode is the one that works with the Donkey Car and is generally more compatible with Linux. The switch is on the top of the controller. Switch to toggle to "D"

The mode button toggles between two modes that switches between the left joystick and the D-pad. The mode button is the small button in the center of the controller. The mode button should be toggled until the green LED is not lit so the left analog stick works properly.

You may need to add an additional custom joystick configuration found [here](../controllers/custom_F710.py)

## Troubleshooting

- https://forums.raspberrypi.com/viewtopic.php?t=213367
- https://forums.raspberrypi.com/viewtopic.php?t=284149
- https://atar-axis.github.io/xpadneo/
# Control Calibration 

When using the PCA9685 PWM driver, you may need to calibrate the steering and throttle controls. This document outlines the process for calibrating the steering and throttle controls using the PCA9685 PWM driver.

## Throttle

```bash
donkey calibrate --channel 0 --bus=1
```

### Reverse

There is a built in safety to the esc, following being driven in the forward mode, go into reverse, then neutral then into reverse.


## Steering
```bash
donkey calibrate --channel 1 --bus=1
```

Should output

________             ______                   _________              
___  __ \_______________  /___________  __    __  ____/_____ ________
__  / / /  __ \_  __ \_  //_/  _ \_  / / /    _  /    _  __ `/_  ___/
_  /_/ // /_/ /  / / /  ,<  /  __/  /_/ /     / /___  / /_/ /_  /    
/_____/ \____//_/ /_//_/|_| \___/_\__, /      \____/  \__,_/ /_/     
                                 /____/                              

using donkey v5.0.0 ...

sombrero enabled
sombrero disabled
init PCA9685 on channel 1 address 0x40 bus 1
Using PWM freq: 60
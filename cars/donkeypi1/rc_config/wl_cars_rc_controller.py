import logging

LOGGER = logging.getLogger(__name__)


# this class is a helper for the RCReceiver class
class Channel:
    def __init__(self, pin):
        self.pin = pin
        self.tick = None
        self.high_tick = None


class WlCarsRCReceiver:
    MIN_OUT = -1
    MAX_OUT = 1

    def __init__(self, cfg, debug=False):
        import pigpio

        self.pi = pigpio.pi()

        # standard variables
        self.channels = [
            Channel(cfg.STEERING_RC_GPIO),
            Channel(cfg.THROTTLE_RC_GPIO),
            Channel(cfg.DATA_WIPER_RC_GPIO),
        ]
        self.min_pwm = 1160
        self.max_pwm = 1915
        self.oldtime = 0
        self.STEERING_MID = cfg.PIGPIO_STEERING_MID
        self.MAX_FORWARD = cfg.PIGPIO_MAX_FORWARD
        self.STOPPED_PWM = cfg.PIGPIO_STOPPED_PWM
        self.MAX_REVERSE = cfg.PIGPIO_MAX_REVERSE
        self.RECORD = cfg.AUTO_RECORD_ON_THROTTLE
        self.debug = debug
        self.mode = 'user'
        self.is_action = False
        self.invert = cfg.PIGPIO_INVERT
        self.jitter = cfg.PIGPIO_JITTER
        self.factor = (self.MAX_OUT - self.MIN_OUT) / (self.max_pwm - self.min_pwm)
        self.cbs = []
        self.signals = [0, 0, 0]
        for channel in self.channels:
            self.pi.set_mode(channel.pin, pigpio.INPUT)
            self.cbs.append(self.pi.callback(channel.pin, pigpio.EITHER_EDGE, self.cbf))
            if self.debug:
                LOGGER.info(f'RCReceiver gpio {channel.pin} created')

    def cbf(self, gpio, level, tick):
        import pigpio

        """ Callback function for pigpio interrupt gpio. Signature is determined
            by pigpiod library. This function is called every time the gpio
            changes state as we specified EITHER_EDGE.  The pigpio callback library
            sends the user-defined callback function three parameters, which it may or may not use
        :param gpio: gpio to listen for state changes
        :param level: rising/falling edge
        :param tick: # of mu s since boot, 32 bit int
        """
        for channel in self.channels:
            if gpio == channel.pin:
                if level == 1:
                    channel.high_tick = tick
                elif level == 0:
                    if channel.high_tick is not None:
                        channel.tick = pigpio.tickDiff(channel.high_tick, tick)

    def pulse_width(self, high):
        """
        :return: the PWM pulse width in microseconds.
        """
        if high is not None:

            return high
        else:
            return 0.0

    def run(self, mode=None, recording=None):
        """
        :param mode: default user/mode
        :param recording: default recording mode
        """

        i = 0
        for channel in self.channels:
            # signal is a value in [0, (MAX_OUT-MIN_OUT)]
            self.signals[i] = (
                self.pulse_width(channel.tick) - self.min_pwm
            ) * self.factor
            # convert into min max interval
            if self.invert:
                self.signals[i] = -self.signals[i] + self.MAX_OUT
            else:
                self.signals[i] += self.MIN_OUT
            i += 1
        if self.debug:
            LOGGER.info(
                f'RC CH1 signal:{round(self.signals[0], 3)}, RC CH2 signal:{round(self.signals[1], 3)}, RC CH3 signal:{round(self.signals[2], 3)}'
            )

        # check mode channel if present
        if (self.signals[2] - self.jitter) > 0:
            self.mode = 'local'
        else:
            # pass though value if provided
            self.mode = mode if mode is not None else 'user'

        # check throttle channel
        if (
            (self.signals[1] - self.jitter) > 0
        ) and self.RECORD:  # is throttle above jitter level? If so, turn on auto-record
            is_action = True
        else:
            # pass through default value
            is_action = recording if recording is not None else False
        print(f"Returning {round(self.signals[0],2)} {round(self.signals[1],2)}")
        return self.signals[0], self.signals[1], self.mode, is_action

    def shutdown(self):
        """
        Cancel all the callbacks on shutdown
        """
        for channel in self.channels:
            self.cbs[channel].cancel()

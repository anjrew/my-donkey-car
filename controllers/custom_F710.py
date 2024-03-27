import logging
from donkeycar.parts.controller import Joystick, JoystickController

class MyLogitechJoystick(Joystick):
    '''
    An interface to a physical Logitech joystick available at /dev/input/js0
    Contains mapping that work for Raspian Stretch drivers
    Tested with Logitech Gamepad F710
    https://www.amazon.com/Logitech-940-000117-Gamepad-F710/dp/B0041RR0TW
    credit:
    https://github.com/kevkruemp/donkeypart_logitech_controller/blob/master/donkeypart_logitech_controller/part.py
    '''
    def __init__(self, *args, **kwargs):
        super(MyLogitechJoystick, self).__init__(*args, **kwargs)

        self.axis_names = {
            0x00: 'left_stick_horz',
            0x01: 'left_stick_vert',

            # Changed these two
            0x02: 'right_stick_horz',
            0x05: 'right_stick_vert',

            0x10: 'dpad_leftright', # 1 is right, -1 is left
            0x11: 'dpad_up_down', # 1 is down, -1 is up
        }

        self.button_names = {
            0x13a: 'back',  # 8 314
            0x13b: 'start',  # 9 315
            0x13c: 'Logitech',  # a  316

            0x130: 'A',
            0x131: 'B',
            0x133: 'X',
            0x134: 'Y',

            0x136: 'L1',
            0x137: 'R1',

            0x13d: 'left_stick_press',
            0x13e: 'right_stick_press',
        }

class MyJoystickController(JoystickController):
    '''
    A Controller object that maps inputs to actions
    credit:
    https://github.com/kevkruemp/donkeypart_logitech_controller/blob/master/donkeypart_logitech_controller/part.py
    '''
    def __init__(self, *args, **kwargs):
        super(MyJoystickController, self).__init__(*args, **kwargs)


    def init_js(self):
        '''
        attempt to init joystick
        '''
        try:
            self.js = MyLogitechJoystick(self.dev_fn)
            self.js.init()
        except FileNotFoundError:
            logging.error(f"{self.dev_fn} not found.")
            self.js = None
        return self.js is not None


    def init_trigger_maps(self):
        '''
        init set of mapping from buttons to function calls
        '''

        self.button_down_trigger_map = {
            'start': self.toggle_mode,
            'B': self.toggle_manual_recording,
            'Y': self.erase_last_N_records,
            'A': self.emergency_stop,
            'back': self.toggle_constant_throttle,
            "R1" : self.chaos_monkey_on_right,
            "L1" : self.chaos_monkey_on_left,
        }

        self.button_up_trigger_map = {
            "R1" : self.chaos_monkey_off,
            "L1" : self.chaos_monkey_off,
        }

        self.axis_trigger_map = {
            'left_stick_horz': self.set_steering,
            'right_stick_vert': self.set_throttle,
            'dpad_leftright' : self.on_axis_dpad_LR,
            'dpad_up_down' : self.on_axis_dpad_UD,
        }

    def on_axis_dpad_LR(self, val):
        if val == -1.0:
            self.on_dpad_left()
        elif val == 1.0:
            self.on_dpad_right()

    def on_axis_dpad_UD(self, val):
        if val == -1.0:
            self.on_dpad_up()
        elif val == 1.0:
            self.on_dpad_down()

    def on_dpad_up(self):
        self.increase_max_throttle()

    def on_dpad_down(self):
        self.decrease_max_throttle()

    def on_dpad_left(self):
        logging.error("dpad left un-mapped")

    def on_dpad_right(self):
        logging.error("dpad right un-mapped")

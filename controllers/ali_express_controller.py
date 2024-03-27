
from donkeycar.parts.controller import Joystick, JoystickController


class MyJoystick(Joystick):
    #An interface to a physical joystick available at /dev/input/js0
    def __init__(self, *args, **kwargs):
        super(MyJoystick, self).__init__(*args, **kwargs)

            
        self.button_names = {
            0x133 : 'x',
            0x130 : 'a',
            0x134 : 'y',
            0x131 : 'b',
            0x137 : 'rb',
            0x136 : 'lb',
            0x13a : 'sel',
            0x13b : 'start',
            0x13c : 'home',
            0x13e : 'ra',
            0x13d : 'la',
        }


        self.axis_names = {
            0x1 : 'left_vert',
            0x0 : 'left_hori',
            0x4 : 'right_vert',
            0x3 : 'right_hori',
            0x11 : 'dup',
            0x10 : 'dhori',
            0x2 : 'lb2',
            0x5 : 'rb2',
        }



class MyJoystickController(JoystickController):
    #A Controller object that maps inputs to actions
    def __init__(self, *args, **kwargs):
        super(MyJoystickController, self).__init__(*args, **kwargs)


    def init_js(self):
        #attempt to init joystick
        try:
            self.js = MyJoystick(self.dev_fn)
            self.js.init()
        except FileNotFoundError:
            print(self.dev_fn, "not found.")
            self.js = None
        return self.js is not None


    def init_trigger_maps(self):
        #init set of mapping from buttons to function calls
            
        self.button_down_trigger_map = {
            'start' : self.toggle_mode,
            'y' : self.erase_last_N_records,
            'a' : self.emergency_stop,
            'rb' : self.increase_max_throttle,
            'lb' : self.decrease_max_throttle,
            'sel' : self.toggle_constant_throttle,
            'b' : self.toggle_manual_recording,
        }


        self.axis_trigger_map = {
            'right_hori' : self.set_steering,
            'left_vert' : self.set_throttle,
        }



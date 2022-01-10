from .encoders import CommaDelimitedEncoder
from .connection import ArduinoSerialPort


class ArduinoServo:

    def __init__(self,
                 n=1,
                 address=3,
                 connect=False,
                 baud=9600,
                 time_out=1,
                 use_micro=False,
                 zero_point=90,
                 m_range=(600, 2400),
                 a_range=(0, 180),
                 steps=1,
                 # encoder = False,

                 ):

        self.n = n
        self.zero_point = [zero_point] * n
        self.steps = [steps] * n
        self.flip = [0] * n
        self.a_range = [a_range] * n
        self.m_range = [m_range] * n
        self._angles = AnglesList(self.zero_point, self)
        self.use_micro = use_micro

        self.port = ArduinoSerialPort(address, baud, time_out=time_out)

        if connect is True:
            self.port.connect()

        self.encoder = CommaDelimitedEncoder()

    @property
    def is_open(self):
        return self.port.is_open

    @property
    def angles(self):
        return self._angles

    @angles.setter
    def angles(self, new_angles):
        assert isinstance(new_angles, (tuple, list))
        assert len(new_angles) == self.n
        self._angles[:] = new_angles

    def write(self, *args, **kwargs):
        if self.use_micro is True:
            data = []
            for i, angle in enumerate(self.angles):
                data[i] = degree_to_microseconds(angle, *self.m_range[i])
        else:
            data = [int(angle) for angle in self.angles]

        message = self.encoder.encode_data(data)
        self.port.write(message)

    def connect(self, *args, **kwargs):
        self.port.connect(*args, **kwargs)

    def reset(self):
        self.angles = self.zero_points
        self.write()

    def move(self, movements):
        for i, move in enumerate(movements):
            self._angles[i] += move * (-1 ** self.flip[i])

        self.write()

    def close(self):
        self.serial_port.close()


def degree_to_microseconds(pos, min_micro, max_micro, servo_range=180):
    """
    converts degrees to the corresponding microsecond values
    """
    return min_micro + int(pos / servo_range * (max_micro - min_micro))


class AnglesList(list):
    """
    helper data structure (inherets from list) for storing angle values that are within
    specified angle ranges. 
    
    example for controller.a_range = [[0, 180], [70, 130]
    
    >>> angles = AnglesList([90, 90], controller)
    >>> angles[0] = 40000
    >>> print(angles)
    [180, 90]
    >>> angles[1] = 30
    >>> print(angles)
    [180, 70]
    
    """

    def __init__(self, data, controller):

        super().__init__(data)

        assert isinstance(controller, ArduinoServo)
        self.controller = controller
        for i, v in enumerate(self):
            self[i] = v

    def __setitem__(self, idx, value):

        # allows for slicing when setting values
        # such as:
        #
        # angles[:] = [...]
        # angles[3:4] = [1, 2]
        # angles[::2] = [...]
        #
        if isinstance(idx, slice):
            i_start = 0 if idx.start is None else idx.start
            i_stop = len(self) if idx.stop is None else idx.stop
            i_step = 1 if idx.step is None else idx.step
            idx = [i for i in range(i_start, i_stop, i_step)]

        if isinstance(idx, int):
            idx, value = [idx], [value]

        for i, v in zip(idx, value):
            assert v is not True and isinstance(v, (float, int))

            min_val, max_val = self.controller.a_range[i]

            if v < min_val:
                val = min_val
            elif v > max_val:
                val = max_val
            else:
                val = v

            list.__setitem__(self, i, val)

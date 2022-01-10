import serial
import time
import gc

class PanTiltServo:
    
    @staticmethod
    def close_ports():
        for o in gc.get_objects():
            if isinstance(o, serial.Serial):
                o.close()
    
    def __init__(self, port=False, 
                 baud=9600, time_out=1, 
                 start_point=(90,80), x_step = 2, 
                 y_step =1, flip_x=False, flip_y = False, 
                 x_range = (0,180), y_range = (0, 180)
                 ):
        
        self._x, self._y = start_point
        self.start_point = start_point
        
        if port is False: 
            system = platform.system()
            if system == 'Windows': 
                self.port = "COM3"
            elif 'Darwin' in system:
                self.port = '/dev/cu.usbmodem1101'
            else: 
                self.port = '/dev/cu.usbmodem1101'
                
        self.baud = baud
        self.time_out = time_out
        
        PanTiltServo.close_ports()
        self.serial_port = serial.Serial(self.port, self.baud, timeout=self.time_out)
        
        self.x_step = x_step # default step size for left/right
        self.y_step = x_step # default step size for up/down
        
        self.flip_x = flip_x # flips left/right controls
        self.flip_y = flip_y # flips up/down controls
        
        self.x_min, self.x_max = x_range
        self.y_min, self.y_max = y_range
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, new_x):
        if new_x > self.x_max:
            self._x = int(self.x_max)
        elif new_x < self.x_min:
            self._x = int(self.x_min)
        else: 
            self._x = int(new_x)
        
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, new_y):
        if new_y > self.y_max:
            self._y = int(self.y_max)
        elif new_y < self.y_min:
            self._y = int(self.y_min)
        else: 
            self._y = int(new_y)
        
    def write(self, new_x=False, new_y=False):
        if isinstance(new_x, (int, float)):
            self.x = new_x 
        if isinstance(new_y, (int, float)):
            self.y = new_y 
            
        #pos_out = "<{},{}>".format(self.x, self.y)
        pos_out = f"<{self.x},{self.y}>"
        pos_out = bytes(pos_out, 'utf-8')
        self.serial_port.write(pos_out);
        return pos_out
 
    def reset(self):
        self.write(self.start_point[0], self.start_point[1])
        
    def move(self, dx=False, dy=False):
        x_dir = 1 if self.flip_x is False else -1
        y_dir = 1 if self.flip_y is False else -1
        
        x_move = dx if isinstance(dx, (int, float)) else 0
        y_move = dy if isinstance(dy, (int, float)) else 0
        
        old_x = self.x
        old_y = self.y
        
        new_x = old_x + (x_move*x_dir)
        new_y = old_y + (y_move*y_dir)
        
        self.write(new_x, new_y)
        
    def close(self):
        self.serial_port.close()
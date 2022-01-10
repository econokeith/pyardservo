import platform
import gc
import serial
import time


class ArduinoSerialPort:
    _serial_objects = []

    @classmethod
    def close_all(cls):
        """
        class method to close all open serial.Serial objects
        """
        for p in cls._serial_objects:
            p.close()
        cls._serial_objects = []

    @classmethod
    def remove_closed(cls):
        """
        class method to remove all closed serial.Serial objects from cls._serial_objects class attribute
        """
        open_ports = []
        for p in cls._serial_objects:
            if p.is_open:
                open_ports.append(p)
        cls._serial_objects = open_ports

    @staticmethod
    def find_and_close_all():
        """
        static method that searches all instantiated objects for serial.Serial
        objects and closes them all. 
        
        """
        for o in gc.get_objects():
            if isinstance(o, serial.Serial):
                o.close()

    @staticmethod
    def find_all_open():
        """
        static method to return all open serial.Serial objects
        """
        return [o for o in gc.get_objects() if isinstance(o, serial.Serial) and o.is_open]

    def __init__(self, address=3, baud_rate=9600, time_out=1, debug=False, min_wait=5):

        self.address = self._find_prefix(address)

        self.baud_rate = baud_rate
        self.time_out = time_out

        self.connected = False
        self.connection = False
        self.debug = debug

        self.min_wait = min_wait

    @property
    def serial_objects(self):
        return self._serial_objects

    @property
    def is_open(self):
        if isinstance(self.connection, serial.Serial) and self.connection.is_open:
            return True
        else:
            return False

    def connect(self,
                address=False,
                baud=False,
                timeout=False,
                wait=True
                ):
        """
        open connection to serial port
        """
        # make sure connection to desired port is closed

        new_address = self.address if address is False else self._find_prefix(address)
        new_baud = self.baud_rate if baud is False else baud
        timeout = self.time_out if timeout is False else timeout

        if self.is_open:
            self.close()

        else:
            open_ports = self.find_all_open()

            for port in open_ports:
                if port.connection == new_address:
                    port.close()

            self.remove_closed()

        self.connection = serial.Serial(new_address, new_baud, timeout=self.time_out)

        self._wait_for_response(wait)

        self.connected = True
        self._serial_objects.append(self.connection)

        if self.debug is True:
            print(f'servos connected to {self.address}')

    def close(self):
        """close serial port"""
        self.connection.close()
        self.connection = False
        self.remove_closed()

    def write(self, message, wait=True, encoding='utf-8'):
        """
        send message to arduino
        write(self, message, wait=True, silent=True, encoding='utf-8')
        waits  for response wait is True and waits for x seconds if wait=x
        """
        assert isinstance(message, (bytes, str))
        if isinstance(message, str):
            message = message.encode('utf-8')

        if self.debug is True:
            tick = time.time()

        self.connection.write(message)
        self._wait_for_response(wait)
        tock = time.time() if self.debug is True else 0

        if self.debug is True:
            print(f'{message} sent with confirmation in {tock - tick} seconds')

    def read(self):
        self.connection.read()

    def _wait_for_response(self, wait=True, read=True, silent=True):
        """
        helper function to wait for response received message from arduino
        if max_wait = 0 or False, the 
        
        """
        if wait is True:
            wait_time = self.min_wait
        elif isinstance(wait, (int, float)) and wait > 0:
            wait_time = wait
        else:
            return

        tick = time.time()
        total_time = 0
        while not self.connection.inWaiting():
            total_time = time.time() - tick
            if total_time > wait_time:
                raise Exception(f"no response received within max_wait={wait_time} seconds")

        if silent is False or self.debug is True:
            print(f"confirmation received after {round(total_time, 4)} seconds after message sent")

        if read is True:
            return self.connection.read()
        else:
            return True

    @staticmethod
    def _find_prefix(address):
        if isinstance(address, int):

            system = platform.system()
            if system == 'Windows':
                out = f'COM{address}'
            elif 'Darwin' in system:
                out = f'/dev/cu.usbmodem1{address}01'
            else:
                out = f'/dev/cu.usbmodem1{address}01'

        else:
            out = address

        return out

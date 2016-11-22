
import glob
import serial
import time
import usb
import sys

# Arm controller serial properties.
BAUD_RATE = 19200
PARITY = serial.PARITY_NONE
STOP_BITS = serial.STOPBITS_TWO
BYTE_SIZE = serial.EIGHTBITS

OUTPUT_ENCODING = 'latin_1'
READ_TIMEOUT = 1.5
READ_SLEEP_TIME = 0.1


class ArmException(Exception):
    ''' Exception raised when things go wrong with the robot arm. '''
    pass


def search_for_port(port_glob, req, expected_res):

    if usb.core.find(idVendor=0x0403, idProduct=0x6001) is None:
        return None

    ports = glob.glob(port_glob)
    if len(ports) == 0:
        return None

    for port in ports:
        with serial.Serial(
                port,
                baudrate=BAUD_RATE,
                parity=PARITY,
                stopbits=STOP_BITS,
                bytesize=BYTE_SIZE) as ser:

            if not ser.isOpen():
                ser.open()

            # Write a request out.
            if sys.version_info[0] == 2:
                ser.write(str(req).encode('utf-8'))
            else:
                ser.write(bytes(req, 'utf-8'))

            # Wait a short period to allow the connection to generate output.
            time.sleep(0.1)

            # Read output from the serial connection check if it's what we want.
            res = ser.read(ser.in_waiting).decode(OUTPUT_ENCODING)
            if expected_res in res:
                return port

    raise ArmException('ST Robotics connection found, but is not responsive.'
                       + ' Is the arm powered on?')
    return None


class Arm(object):
    ''' Represents an ST Robotics arm. '''

    def __init__(self):
        self.ser = None
        self.port = None


    def connect(self, port=None):
        ''' Open a serial connection to the arm. '''
        if port is None:
            self.port = search_for_port('/dev/ttyUSB*', 'ROBOFORTH\r\n',
                                        'ROBOFORTH')
        else:
            self.port = port

        if self.port is None:
            raise ArmException('ST Robotics connection not found.')

        self.ser = serial.Serial(
                port=self.port,
                baudrate=BAUD_RATE,
                parity=PARITY,
                stopbits=STOP_BITS,
                bytesize=BYTE_SIZE
        )

        # Open the USB connection to the robot.
        if not self.ser.isOpen():
            self.ser.open()

        if not self.ser.isOpen():
            raise ArmException('Failed to open serial port. Exiting.')

        return self.port


    def disconnect(self):
        ''' Disconnect from the arm. '''
        self.ser.close()
        self.ser = None
        self.port = None


    def write(self, text):
        ''' Write text out to the arm. '''
        # Output is converted to bytes with Windows-style line endings.
        if sys.version_info[0] == 2:
            text_bytes = str(text.upper() + '\r\n').encode('utf-8')
        else:
            text_bytes = bytes(text.upper() + '\r\n', 'utf-8')
        self.ser.write(text_bytes)


    def _clean_output(self, out):
        ''' Process the serial output to clean it up. '''
        # To clean the output, leading and trailing whitespace is removed and
        # extraneous '>' characters are stripped.
        return out.strip('\r\n\t >')


    def read(self, raw=False):
        ''' Read data from the arm. Data is returned as a latin_1 encoded
            string, or raw bytes if 'raw' is True. '''
        time.sleep(READ_SLEEP_TIME)
        out = self.ser.read(self.ser.in_waiting)
        if not raw:
            out = out.decode(OUTPUT_ENCODING)

        # NOTE: currently going off of theory that all responses end with '>'
        time_waiting = 0
        while (len(out) == 0 or out.strip()[-1] != '>'):
            time.sleep(READ_SLEEP_TIME)
            time_waiting += READ_SLEEP_TIME
            out += self.ser.read(self.ser.in_waiting).decode(OUTPUT_ENCODING) # TODO
            if time_waiting >= READ_TIMEOUT:
                break

        return self._clean_output(out)


    def dump(self, raw=False):
        ''' Dump all output currently in the arm's output queue. '''
        out = self.ser.read(self.ser.in_waiting)
        if raw:
            return out
        return out.decode(OUTPUT_ENCODING)


    def is_connected(self):
        ''' True if the serial connection to arm is open. False otherwise. '''
        return self.ser.isOpen() if self.ser else False


    def get_info(self):
        ''' Returns status of the robot arm. '''
        return {
            'Connected': self.is_connected(),
            'Port': self.port,
            'Bytes Waiting': self.ser.in_waiting if self.ser else 0
        }


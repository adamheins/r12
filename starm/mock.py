''' Use to mock an arm for testing purposes. '''

class MockArm(object):
    def __init__(self):
        self.connected = False
        self.response = None

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

    def is_connected(self):
        return self.connected

    def read(self):
        if self.response:
            res = self.response
            self.response = None
            return res
        return ''

    def write(self, msg):
        self.response = '{} OK'.format(msg)

    def dump(self):
        if self.response:
            res = self.response
            self.response = None
            return res
        return ''

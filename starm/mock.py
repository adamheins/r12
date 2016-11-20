''' Use to mock an arm for testing purposes. '''

class MockArm(object):
    def __init__(self):
        self.connected = False

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

    def is_connected(self):
        return self.connected

    def read(self):
        return 'READ RESPONSE'

    def write(self, msg):
        pass

    def dump(self):
        return 'DUMP RESPONSE'

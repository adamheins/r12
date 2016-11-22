from setuptools import setup

setup(name='r12',
      version='0.2.0',
      description='Low-level interface for ST Robotics R12 robotic arm.',
      url='https://github.com/adamheins/r12',
      author='Adam Heins',
      author_email='mail@adamheins.com',
      license='MIT',
      packages=['r12'],
      install_requires=[
          'colorama',
          'pyusb',
          'pyserial',
      ],
      scripts=[
          'r12/r12-shell',
      ],
      zip_safe=False)


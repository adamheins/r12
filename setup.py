from setuptools import setup

setup(name='starm',
      version='0.1.1',
      description='Low-level interface for ST Robotics robot arm.',
      url='https://github.com/adamheins/starm',
      author='Adam Heins',
      author_email='mail@adamheins.com',
      license='MIT',
      packages=['starm'],
      install_requires=[
          'pyusb',
          'pyserial',
      ],
      zip_safe=False)


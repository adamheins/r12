from setuptools import setup

setup(name='starm',
      version='0.1.3',
      description='Low-level interface for ST Robotics robot arm.',
      url='https://github.com/adamheins/starm',
      author='Adam Heins',
      author_email='mail@adamheins.com',
      license='MIT',
      packages=['starm'],
      install_requires=[
          'colorama',
          'pyusb',
          'pyserial',
      ],
      scripts=[
          'starm/arm-shell',
      ],
      zip_safe=False)


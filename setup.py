from setuptools import setup

version = open('VERSION').read().strip()

setup(name='r12',
      version=version,
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
      scripts=['r12/r12-shell'],
      include_package_data=True,
      zip_safe=False,
)


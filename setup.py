
from setuptools import setup

setup(name='envy',
      version='0.0.1',
      description='environment manager and tool',
      author='Tom Barron',
      author_email='tusculum@gmail.com',
      url='https://github.com/tbarron/envy',
      packages=['envy'],
      entry_points={'console_scripts': ['nv = nv:main']}
      )

import platform

if platform.system() == 'Windows':
  from .win import *
else:
  from .linux import *

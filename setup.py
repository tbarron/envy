from distutils.core import setup
from distutils.sysconfig import get_python_lib
import os
import pdb

pdb.set_trace()
ep_d = {
    'console_scripts': ["nv = nv:main"]
    }
nv_version = ".nv_version"
nv_root = os.path.join(get_python_lib(), "nv")
if not os.path.exists(nv_version):
    os.system("git describe > %s" % nv_version)
f = open(nv_version, 'r')
version = f.read().strip()
f.close()
setup(name="shnv",
      version=version,
      packages=["nv"],
      entry_points=ep_d,
      author="Tom Barron",
      author_email="tom.barron@comcast.net",
      url="",
      data_files=[(nv_root, [nv_version])]
      )

import os
import subprocess as sp
import tempfile
import unittest

from rosdep2 import main as rdmain

class Issue30TestCase(unittest.TestCase):
    def testIssue30(self):
        d = make_temp_dir()
        try:
            cd(d)
            script = '''#!/bin/bash
mkdir ws
mkdir ws/src
mkdir ws/devel
cd ws/src
catkin_init_workspace > /dev/null
cd ..
cd devel
cmake ../src > /dev/null
cd ../src
git clone git://github.com/ros-drivers/joystick_drivers.git > /dev/null
'''
            run_script('commands.bash', script)
            source('ws/devel/develspace/setup.sh')
            lookup = make_lookup()
            keys = rdmain.get_keys(lookup, ['spacenav_node'], recursive=True)
            self.assertEqual('libspnav-dev libx11-dev spacenavd'.split(),
                             sorted(keys))
        finally:
            sp.call(['rm', '-rf', d])

def make_temp_dir():
    return tempfile.mkdtemp()

def cd(d):
    os.chdir(d)

def write_file(filename, contents):
    with open(filename, 'w') as f:
        f.write(contents)

def run_script(filename, contents):
    """
    Creates a script with the given filename and contents, runs it
    and returns the output.
    """
    write_file(filename, contents)
    os.chmod(filename, 0x755)
    p = sp.Popen([os.path.join('.', filename)], stdout=sp.PIPE)
    p.wait()
    return p.stdout.read()

def source(script):
    """
    Sources a shell script at a given path, updating the environment.
    """
    pipe = sp.Popen(". %s; env" % script, stdout=sp.PIPE, shell=True)
    data = pipe.communicate()[0]
    env = dict((line.split("=", 1) for line in data.splitlines()))
    os.environ.update(env)

def make_lookup():
    """
    Creates a RosdepLookup object.
    """
    import rosdep2.sources_list as sl
    import rosdep2.lookup as rdl
    sources_loader = sl.SourcesListLoader.create_default(
        sources_cache_dir=sl.get_sources_cache_dir(),
        verbose=True)
    return rdl.RosdepLookup.create_from_rospkg(sources_loader=sources_loader)

if __name__ == '__main__':
    unittest.main()


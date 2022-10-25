#!/usr/bin/python
import subprocess
import threading
import select
from config_fuzzer import RunParameters

def get_monitor(pkg_name):

    while True:
        package_id = get_package_id(pkg_name)

        print package_id
        cmd = 'adb -s ' + RunParameters.AVD_SERIAL + ' shell logcat | grep controllable_widgets'

        print(cmd)

        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, universal_newlines=True)
        line = p.stdout.readline()
        print "+++++++++++++ " + line

        return p

        # continuously reading from shell processes
        #for line in iter(p.stdout.readline,""):
        #    print "$$$$$$$$$"+line

def get_monitor_proc(pkg_name):
    package_id = get_package_id(pkg_name)
    cmd = 'adb -s ' + RunParameters.AVD_SERIAL + ' shell logcat | grep controllable_widgets'
    print(cmd)
    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, universal_newlines=True)

    print "-- log monitor is on..."
    return p



# returning the hashcode of the app package name
def get_package_id(pkg_name):
    package_id = java_string_hashcode(pkg_name)
    return abs(package_id)


# returning the same hashcode as java's String.hasCode
def java_string_hashcode(string):
    h = 0
    for c in string:
        h = (31 * h + ord(c)) & 0xFFFFFFFF

    return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000

# extracting the state id from the output of the shell
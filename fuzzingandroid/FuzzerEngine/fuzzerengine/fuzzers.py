import os
import subprocess
import sys

from config_fuzzer import RunParameters


class MonkeyController:


    def __init__(self):
        self.output = []
        self.event_seq_to_transition = []

    # starting the monkey exerciser with
    def run_monkey(self, packageName,event_num,delay):
        del self.output[:]

        cmd = 'adb -s ' + RunParameters.AVD_SERIAL + ' shell monkey -p ' + packageName + ' --ignore-crashes --ignore-timeouts --ignore-security-exceptions  --ignore-native-crashes --throttle '+str(delay) + ' -v  ' + str(event_num) + ' '
        print cmd


        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, universal_newlines=True, close_fds=True)

        # continuously reading output from the monkey process
        while True:

            line = p.stdout.readline()
            print("Monkey event " + line)

            #if it is a monkey event (not random logs) then add it to the seq
            if "Sending" in line:
                #print "Monkey event " + line
                self.event_seq_to_transition.append("" + line)

            #removing the annotations in the event-sequence scripts
            if not line.lstrip().startswith("/"):
                self.output.append(line)

            st = p.poll()
            if line == '' and st != None:
                print "break monkey due to line == '' and p.poll() != None"
                print "line:"+line
                print st
                print('--monkey watcher is terminated!')
                break

            sys.stdout.flush()

     # kill monkey
    def kill_monkey(self):
        print("--killing monkey")
        os.system("adb -s " + RunParameters.AVD_SERIAL +" shell pkill -f monkey")
#!/usr/bin/python
import subprocess
import sys
import os

def named_container_running(name):
    """Checks with docker if a container is running."""
    command = "docker ps -q -f name={}".format(name)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    process.wait()
    id_text = process.stdout.read()
    if not process.returncode == 0:
        print Red+"\a"
        print "ERROR: Docker call in 'named_container_running' failed."
        print "      Command:",command
        print "      Output:",id_text
        print White
        sys.exit(1)
    if len(id_text) < 1:
        return(False)
    else:
        return(id_text)

def kill():
    subprocess.call("docker-compose -f docker-compose.yml kill",shell=True)

def rm():
    subprocess.call("docker-compose -f docker-compose.yml rm ",shell=True)

def up():
    # Is the edgeservice running?
    if named_container_running('edgecdp'):
        # Start up the wind turbine playground
        subprocess.call("docker-compose -f docker-compose.yml up -d ",shell=True)
    else:
        print Red+"\a"
        print "ERROR: Edge Services (edgecdp container) is not running."
        print "FIX:   Start it using the './start_edgeservices.sh' script"
        print "       located in the directory. 'edgeservices'"
        print White
        sys.exit(1)

def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'up':
        up()
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'kill':
        kill()
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'rm':
        rm()


if __name__ == '__main__':
    main()

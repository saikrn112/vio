#!/usr/bin/python
import argparse
import os
from sys import platform
import time
import docker
#below command is from document https://docker-py.readthedocs.io/en/stable/containers.html
ENV_HOME = os.environ["HOME"]
ENV_USER = os.environ["USER"]
ENV_DISPLAY = os.environ["DISPLAY"]

def create_docker_instance(name,args):
    options = ""
    if args.rm:
        options += " --rm "
    if args.it:
        options += " -it "
    if args.display:
        os.system("xhost local:root")
        options += f" --gpus all --privileged -e DISPLAY={ENV_DISPLAY} --net=host -v /tmp/.X11-unix/:/tmp/.X11-unix/ "
    if args.usb:
        options +=  "--privileged --device=/dev/bus/usb:/dev/bus/usb"
    print(f"Creating {name} instance")

    if args.workspace:
        vio_volume = args.workspace
    elif platform == "linux" or platform == "linux2":
        vio_volume = f"{ENV_HOME}/Personal/computer_vision/vio"

    cmd= f"docker run --name {name} {options} -v {vio_volume}:/root/vio/ somidi/vio:v1 /usr/bin/zsh"
    print(cmd)
    if not args.dry_run:
        os.system(cmd)

def connect_to_container(name,args):
    print(f"found runing {name} container, attaching to it's zsh")
    cmd = f"docker exec -it {name} zsh"
    print(cmd)
    if not args.dry_run:
        os.system(cmd)

def main():
    parser = argparse.ArgumentParser(description='start docker instance')

    parser.add_argument( "--rm",action='store_true',help="remove container on exit")
    parser.add_argument( "--it",action='store_true',help="interactive mode")
    parser.add_argument( "--name",default="vio",help="name of the container,default:optical")
    parser.add_argument( "--workspace",default=None,help="interactive mode,default:None")
    parser.add_argument( "--display",action='store_true',help="to attach display to this container")
    parser.add_argument( "--usb",action='store_true',help="to attach usb device to this container")
    parser.add_argument( "--dry_run",action='store_true',help="to dry_run the commands generated by this script")
    args = parser.parse_args()

    name = args.name

    client = docker.from_env()

    if args.display:
        os.system("xhost local:root")

    containers_list = client.containers.list(all=True,sparse=True,filters={'name':f'{name}'})
    containers_len = len(containers_list)
    if containers_len > 1:
        print(f"expected 1 but found more containers {containers_list}")
        exit()
    elif containers_len == 1:
        container = containers_list[0]
        if container.status == "exited":
            print(f"starting container")
            container.start()
            connect_to_container(name,args)
        elif container.status == "running":
            connect_to_container(name,args)
    elif containers_len == 0:
        create_docker_instance(name,args)

if __name__ == '__main__':
    main()

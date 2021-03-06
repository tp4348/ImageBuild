#!/usr/bin/env python

import os
import sys
import subprocess
import time
import get_latest_distro as gld

def is_distro_different_then_current(img1, img2):
    return img1 != img2

'''
Main func
'''
if __name__ == '__main__':

    home = "/home/ubuntu"
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

    # NOTE: /dev/sd* gets assigned according to the order plugged in
    devs = {
        'sda' : {
            'img_version' : None,
            'distro' : 'xenial',
                },
        'sdb' : {
            'img_version' : None,
            'distro' : 'xenial',
                },
        'sdc' : { 
            'img_version' : None,
            'distro' : 'xenial',
                },
        'sdd' : {
            'img_version' : None,
            'distro' : 'xenial',
                },
    }

    while True:
        # Detect if cards are plugged
        for dev in devs:
            path = os.path.join('/dev', dev) 
            print("---------------------------")
            if (os.path.exists(path)):
                # Fetch latest 
                ad = gld.accessDatabase(devs[dev]['distro'])
                latest_fetched_package = ad.fetch_latest_online()
                if latest_fetched_package == 0:
                    print("Could not fetch latest package from " + ad.url)
                    continue
                else:
                    print("Found package: "+latest_fetched_package+", proceeding.")

                # if there was a package file fetched
                if latest_fetched_package != 0:
                    # first compare it to the currently installed package
                    filename = latest_fetched_package[:len(latest_fetched_package) - 3]
                    diff = ad.is_pkg_different_then_current(filename)
                    if diff == False:
                        print("The latest package is already downloaded")
                    elif diff == True:
                        ad.trigger_download(latest_fetched_package)
                    else:
                        print("There was an error checking difference between installed and fetched files")
                        continue
                else:
                    print("Failed to fetch package")
                    continue

                # Check if latest image installed on the SD card
                if is_distro_different_then_current(devs[dev]['img_version'], latest_fetched_package):
                    # Flash image
                    gld.execute('sudo rm -rf ' +path+'1', home)
                    gld.execute('sudo rm -rf ' +path+'2', home)
                    cmd = 'sudo dd if='+os.path.join(home, filename)+' of='+path+' status=progress'
                    gld.execute(cmd, home)
                    devs[dev]['img_version'] = latest_fetched_package
                else:
                    print("Latest image of "+devs[dev]['distro']+" installed on "+dev)

            else:
                devs[dev]['img_version'] = None 
                print("Device "+dev+" not plugged in!")


        time.sleep(1) # TODO: Create an event based system 

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 10:12:08 2021

@author: user
"""
import os
import io
import subprocess

cmd = ["python", "-u", "/home/user/tutorial/GitDir/Microphonics/Testy2.py"]


try:
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, shell=False
    )
    while True:
        output = process.stdout.readline().decode()
        if output == "" and process.poll() is not None:
            break
        if output != "":
            print(output)
    #            for line in process.stdout:
    #     while process.poll() is None:
    #         line = process.stdout.readline()
    #         print ("test:", line)
    #         if not line:
    #             break
    # #                  the real code does filtering here
    # #        output=line.decode()
    # #        print ("test:", line)
    # #                self.ui.AcqProg.setText(output)

    return_code = process.poll()
    if return_code == 0:
        #                self.ui.AcqProg.setText("Test run completed successfully")
        print("Test run completed sucessfully")

    if return_code != 0:
        #        print(err)
        e = subprocess.CalledProcessError(return_code, cmd)
        #                    e.stdout, e.stderr = err
        #                self.ui.AcqProg.setText("Call to microphonics script failed \n"+str(e))
        print("Call returned non-zero value")


except:
    #            self.ui.AcqProg.setText("try failed \n")
    print("try failed")


print("the code waited for the process to complete")

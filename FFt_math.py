# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 09:39:20 2021

@author: bob
"""
# J Nelson 30 Mar 2022
# Using this as a utils file for CommMicro.py

from os import makedirs, path

read_data = []


def readCavDat(fileName):
    header_Data = []
    with open(fileName) as f:
        # watch for line to start with # ACCL
        lini = f.readline()
        while "ACCL" not in lini:
            header_Data.append(lini)
            lini = f.readline()
        next(f)
        next(f)
        # append the # ACCL line to the header
        header_Data.append(lini)
        read_data = f.readlines()

    f.close()

    #   debugging
    #    print('read_data[0:2]')
    #    print(read_data[0:5])
    return (read_data, header_Data)


# Number of sample points


def parseCavDat(read_data):
    cavDat1 = []
    cavDat2 = []
    cavDat3 = []
    cavDat4 = []
    for red in read_data:
        cavDat1.append(float(red[0:8]))
        try:
            if red[10:18] != "":
                cavDat2.append(float(red[10:18]))
            if red[20:28] != "":
                cavDat3.append(float(red[20:28]))
            if red[30:38] != "":
                cavDat4.append(float(red[30:38]))
        except:
            pass

    # print(cavDat3)
    #    print('cavDat1[0:5]')
    #    print(cavDat1[0:5])
    #    print('cavDat2[0:5]')
    #    print(cavDat2[0:5])
    #    print('cavDat3[0:5]')
    #    print(cavDat3[0:5])

    return [cavDat1, cavDat2, cavDat3, cavDat4]


def dummyFileCreator(pathToDatafile):
    #    print(pathToDatafile)
    data, Header = readCavDat("1234_20210617_1227")
    brkFile = "0/"
    indxFilName = pathToDatafile.find(brkFile, 0)
    NewFileName = pathToDatafile[indxFilName + 2 :] + "_microphonics.dat"
    f = open(pathToDatafile + "/" + NewFileName, "x")
    for i in range(len(Header)):
        f.write(str(Header[i]))
    cavDat1, cavDat2, cavDat3, cavDat4 = parseCavDat(data)
    #    print(len(cavDat1))
    for i in range(len(cavDat1)):
        f.write(str(cavDat1[i]) + "\n")
    f.close()
    return


def compatibleMkdirs(filename):
    makedirs(path.dirname(filename), exist_ok=True)
    return filename


# CMID = <SC linac> : <CM ID>
CRYOMODULE_IDS = [
    "ACCL:L0B:01",
    "ACCL:L1B:02",
    "ACCL:L1B:03",
    "ACCL:L1B:H1",
    "ACCL:L1B:H2",
    "ACCL:L2B:04",
    "ACCL:L2B:05",
    "ACCL:L2B:06",
    "ACCL:L2B:07",
    "ACCL:L2B:08",
    "ACCL:L2B:09",
    "ACCL:L2B:10",
    "ACCL:L2B:11",
    "ACCL:L2B:12",
    "ACCL:L2B:13",
    "ACCL:L2B:14",
    "ACCL:L2B:15",
    "ACCL:L3B:16",
    "ACCL:L3B:17",
    "ACCL:L3B:18",
    "ACCL:L3B:19",
    "ACCL:L3B:20",
    "ACCL:L3B:21",
    "ACCL:L3B:22",
    "ACCL:L3B:23",
    "ACCL:L3B:24",
    "ACCL:L3B:25",
    "ACCL:L3B:26",
    "ACCL:L3B:27",
    "ACCL:L3B:28",
    "ACCL:L3B:29",
    "ACCL:L3B:30",
    "ACCL:L3B:31",
    "ACCL:L3B:32",
    "ACCL:L3B:33",
    "ACCL:L3B:34",
    "ACCL:L3B:35",
]


# getter
def CM_IDs():
    return CRYOMODULE_IDS

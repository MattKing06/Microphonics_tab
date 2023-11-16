from datetime import datetime
from math import log2, floor, ceil
import os
import subprocess
import sys
from typing import Union, List


BUFFER_LENGTH = 16384  # Default number of samples in buffer
DEFAULT_SAMPLING_RATE = 2000  # Default number of samples to take


class Model:
    """Performs Microphonics Data Collection using external Python script

    Running the scripts and constructing arguments is handled by DAQProcess class.
    Storing the arguments for DAQProcess is handled by UserArgs class.
    Model class is provided to combine both UserArgs and DAQProcess.
    """

    def __init__(self):
        self.name = "model"
        self.user_arguments = UserArgs()
        self._save_root_location = ""
        self._save_location = ""
        self._output_filename = ""
        self._start_date = datetime.now()
        self.daq = DAQProcess()

    @property
    def sampling_rate(self) -> float:
        """Estimated Sample rate of DAQProcess"""
        return DEFAULT_SAMPLING_RATE / self.user_arguments.decimation_amount

    @property
    def acquire_time(self):
        """Estimated of time it will take to complete DAQProcess"""
        return (
            BUFFER_LENGTH
            * self.user_arguments.decimation_amount
            * self.user_arguments.num_buffers
            / DEFAULT_SAMPLING_RATE
        )

    @property
    def process_return_code(self) -> int:
        """Return-code from DAQProcess"""
        return self.daq.return_code

    @property
    def process_output(self) -> str:
        """Std-out ouput from DAQProcess"""
        return self.daq.output

    @property
    def process_err(self) -> str:
        """Std-error ouput from DAQProcess"""
        return self.daq.error

    def run(self):
        """Contructs the arguments for DAQProcess and runs the script using UserArgs"""
        self.construct_args()
        self.daq.run()

    @property
    def cryomodules(self) -> list:
        """The possible cryomdules to run DAQProcess with."""
        # CMID = <SC linac> : <CM ID>
        return [
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

    @property
    def start_date(self) -> datetime:
        """The datetime when DAQProcess started."""
        return self._start_date

    @property
    def save_location(self):
        """The sub-folder in which data files from DAQProcess will be stored."""
        return self._save_location

    @save_location.setter
    def save_location(self, path: str):
        """Sets the sub-folder in which data files from DAQProcess will be stored."""
        # if not os.path.exists(path):
        # raise FileNotFoundError(
        # f"Could not find {path}, save location not updated."
        # )
        self._save_location = path

    @property
    def save_root_location(self):
        """The root location for data files generated from DAQProcess to be stored."""
        return self._save_root_location

    @save_root_location.setter
    def save_root_location(self, path: str):
        """Set the root location for data files generated from DAQProcess to be stored."""
        # if not os.path.exists(path):
        #    raise FileNotFoundError(
        #        f"Could not find {path}, save root location not updated."
        #    )
        self._save_root_location = path

    @property
    def outfile_name(self) -> str:
        """The filename that is used to store data generated from DAQProcess"""
        return self._output_filename

    @outfile_name.setter
    def outfile_name(self, file: str):
        """Sets the filename that is used to store data generated from DAQProcess"""
        self._output_filename = file

    def set_new_outfile(self):
        """Sets outfile_name to a new filename used in DAQProcess to store data"""
        # Need to make output file name
        # Sergio had res_cav#_c#_yyyymmdd_hhmmss
        # Go to res_cm##_cav####_c#_yyyymmdd_hhmmsss
        timestamp = datetime.now().strftime("%Y%m%d" + "_" + "%H%M%S")
        self.outfile_name = (
            "res_CM"
            + self.user_arguments.cryomodule
            + "_cav"
            + self.user_arguments.cavity_number_str
            + "_c"
            + str(self.user_arguments.num_buffers)
            + "_"
            + timestamp
        )

    def set_new_location(self):
        """Generates a new path used in DAQProcess to store data"""
        # Make the path name to be nice:
        # LASTPATH=DATA_DIR_PATH+'ACCL_'+linac+'_'+cmNumStr+cavNumStr[0]+'0'
        self.save_location = os.path.join(
            self.save_root_location,
            "ACCL_"
            + self.user_arguments.linac
            + "_"
            + self.user_arguments.cryomodule
            + "00",
        )
        # get today's date as 2- or 4-char strings
        # /u1/lcls/physics/rf_lcls2/microphonics/ACCL_L0B_0100/yyyy/mm/dd/
        year = str(self.start_date.year)
        month = "%02d" % self.start_date.month
        day = "%02d" % self.start_date.day
        self.save_location = os.path.join(self.save_location, year, month, day)

    def construct_args(self):
        """Construct the CA command for DAQ, as well as other Microphonics DAQ script args using UserArgs"""
        caCmd = (
            "ca://ACCL:"
            + self.user_arguments.linac
            + ":"
            + str(self.user_arguments.cryomodule)
            + "00:RES"
            + self.user_arguments.rack_str
            + ":"
        )
        self.daq.construct_args(
            out_location=self.save_location,
            ca_command=caCmd,
            decimation=self.user_arguments.decimation_amount,
            cavities=self.user_arguments.cavity_number_list,
            buffer_number=self.user_arguments.num_buffers,
            outfile=self.outfile_name,
        )

    def _read_cavity_datafile(self, filename: str) -> List[str]:
        header_Data = []
        with open(filename) as f:
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
        #   debugging
        #    print('read_data[0:2]')
        #    print(read_data[0:5])
        return (read_data, header_Data)

    def parse_cavity_dataset(self, filename):
        cavity_data, _ = self._read_cavity_datafile(filename)
        cavDat1 = []
        cavDat2 = []
        cavDat3 = []
        cavDat4 = []
        for red in cavity_data:
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


class DAQProcess:
    """Constructs arguments (see UserArgs) needed for DAQ script and runs script in subprocess"""

    def __init__(self):
        self._return_code = 0
        self._output = ""
        self._error = ""
        self._script = (
            "/usr/local/lcls/package/lcls2_llrf/srf/software/res_ctl/res_data_acq.py"
        )
        self._args = []

    def construct_args(
        self, out_location, ca_command, decimation, cavities, buffer_number, outfile
    ):
        """
        Constructs all of the arguments provided for the DAQ script to run.
        Recommended to call this prior to the run function.
        """
        self._args = [
            "python",
            str(self._script),
            "-D",
            str(out_location),
            "-a",
            str(ca_command),
            "-wsp",
            str(decimation),
            "-acav",
        ]
        for cavity_number in cavities:
            self._args += str(cavity_number)
        self._args += [
            "-ch",
            "DF",
            "-c",
            str(buffer_number),
            "-F",
            str(outfile),
        ]

    def run(self):
        """
        Spawn a subprocess to run the DAQ Process script with arguments.
        Stores the return code, output, and error as members variables
        """
        process = subprocess.Popen(
            self.args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        self.output, self.error = process.communicate()
        self.return_code = process.poll()
        print("Return code: ", self.return_code)
        print("Out: ", self.output)
        if len(self.error) > 0:
            print("Err: ", self.error)

    @property
    def return_code(self):
        """The return code from the subprocess generated in run"""
        return self._return_code

    @property
    def output(self):
        """The std-output from the subprocess generated in run()"""
        return self._output

    @output.setter
    def output(self, value: Union[str, bytes]) -> None:
        """Set the output from the subprocess generated in run()"""
        if isinstance(value, bytes):
            self._output = value.decode(sys.stdin.encoding)
        elif isinstance(value, str):
            self._output = value

    @property
    def error(self) -> str:
        """The std-error from the subprocess generated in run()"""
        return self._error

    @error.setter
    def error(self, value: Union[str, bytes]) -> None:
        """Set the std-error from the subprocess generated in run()"""
        if isinstance(value, bytes):
            self._error = value.decode(sys.stdin.encoding)
        elif isinstance(value, str):
            self._error = value

    @property
    def script(self) -> str:
        """The script used for the subprocess in run()"""
        return self._script

    @property
    def args(self) -> list:
        """The arguments for the script used for the subprocess in run()"""
        return self._args

    @args.setter
    def args(self, args: list) -> None:
        """Set the arguments for the script used for the subprocess in run()"""
        self._args = args


class UserArgs:
    """The arguments that are used to perform DAQProcess"""

    def __init__(self):
        # cavNumA/B are '1 2 3 4' with spaces in between for
        #  script call
        # cavNumStr is '1234' for filename
        self._cavity_number_str = ""
        self._cavity_number_list = list()
        self._cryomodule_str = ""
        self._cmid = ""
        self._linac = ""
        self._rack = 0
        self._rack_delta = 0
        self._n_buffers = 0
        self._decimation = 1
        self._allowed_rack_numbers = [0, 1]

    @property
    def cavity_number_str(self) -> str:
        """Selected cavity number as a string (used in DAQProcess)"""
        return self._cavity_number_str

    @cavity_number_str.setter
    def cavity_number_str(self, value: str) -> None:
        """Set the cavity number string (used in DAQProcess)"""
        self._cavity_number_str = value

    @property
    def cavity_number_list(self) -> list:
        """Selected cavity numbers"""
        return self._cavity_number_list

    @cavity_number_list.setter
    def cavity_number_list(self, value: list) -> None:
        """Set the cavity numbers"""
        self._cavity_number_list = value

    @property
    def cryomodule(self) -> str:
        """Selected cryomodule as a string (used in DAQProcess)"""
        return self._cryomodule_str

    @cryomodule.setter
    def cryomodule(self, value: str) -> None:
        """Set the cryomodule string (used in DAQProcess)"""
        self._cryomodule_str = value

    @property
    def cryomodule_id(self) -> str:
        """The cryomodule ID (i.e. ACCL:L3B:20)"""
        return self._cmid

    @cryomodule_id.setter
    def cryomodule_id(self, value: str) -> None:
        """Set the cryomodule ID"""
        # list of cryomodules provided in Model.cryomodules
        self._cmid = value

    @property
    def num_buffers(self) -> str:
        """Number of buffers to use in DAQProcess"""
        return self._n_buffers

    @num_buffers.setter
    def num_buffers(self, value: str) -> None:
        """Set the number of buffers to use in DAQProcess"""
        self._n_buffers = value

    @property
    def decimation_amount(self):
        """The amount of decimation used in DAQProcess"""
        return self._decimation

    @decimation_amount.setter
    def decimation_amount(self, value):
        """Set the amount of decimation used in DAQProcess"""
        # only powers of 2.
        if ceil(log2(value)) != floor(log2(value)):
            print(
                "Only able to set decimation to powers of 2. Keeping decimation as ",
                self._decimation,
            )
            return
        self._decimation = value

    @property
    def linac(self) -> str:
        """The linac that is used in DAQProcess"""
        return self._linac

    @linac.setter
    def linac(self, value: str) -> None:
        """Set the linac that is used in DAQProcess"""
        self._linac = value

    @property
    def rack(self) -> int:
        """The rack that data is collected from in DAQProcess (0, 1) = (A, B)"""
        return self._rack

    @property
    def rack_str(self) -> str:
        """The name for the rack that data is collected from in DAQProcess"""
        # rack is either 1 or 0
        # which evaluate to True, False respectively
        return "B" if self.rack else "A"

    @rack.setter
    def rack(self, value: int) -> None:
        """Set rack to collect data from in DAQProcess, check all_rack_numbers for options"""
        if value not in self._allowed_rack_numbers:
            return print(
                "Value of rack must be one of ",
                self._allowed_rack_numbers,
                ". You tried to set: ",
                value,
            )
        self._rack = value

    @property
    def rack_delta(self) -> int:
        """Offset in cavity number depending on chosen rack (A = 0-4, B=5-9??)"""
        return self._rack_delta

    @rack_delta.setter
    def rack_delta(self, value: int) -> None:
        """Set the cavity number offset for racks."""
        self._rack_delta = value

from datetime import datetime
from math import log2, floor, ceil
import os
import subprocess
import sys
from typing import Union, List


BUFFER_LENGTH = 16384
DEFAULT_SAMPLING_RATE = 2000


class Model:
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
        return DEFAULT_SAMPLING_RATE / self.user_arguments.decimation_amount

    @property
    def acquire_time(self):
        return (
            BUFFER_LENGTH
            * self.user_arguments.decimation_amount
            * self.user_arguments.num_buffers
            / DEFAULT_SAMPLING_RATE
        )

    @property
    def process_return_code(self):
        return self._process_return_code

    @property
    def process_output(self):
        return self._process_output

    @property
    def process_err(self):
        return self._process_err

    def run(self):
        self.daq.construct_args()
        self.daq.run()

    @property
    def cryomodules(self) -> list:
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
        return self._start_date

    @property
    def save_location(self):
        return self._save_location

    @save_location.setter
    def save_location(self, path: str):
        # if not os.path.exists(path):
        # raise FileNotFoundError(
        # f"Could not find {path}, save location not updated."
        # )
        self._save_location = path

    @property
    def save_root_location(self):
        return self._save_root_location

    @save_root_location.setter
    def save_root_location(self, path: str):
        # if not os.path.exists(path):
        #    raise FileNotFoundError(
        #        f"Could not find {path}, save root location not updated."
        #    )
        self._save_root_location = path

    @property
    def outfile_name(self) -> str:
        return self._output_filename

    @outfile_name.setter
    def outfile_name(self, file: str):
        self._output_filename = file

    def set_new_outfile(self):
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
        # Make the path name to be nice:
        # LASTPATH=DATA_DIR_PATH+'ACCL_'+liNac+'_'+cmNumStr+cavNumStr[0]+'0'
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
        self.args += [
            "-ch",
            "DF",
            "-c",
            str(buffer_number),
            "-F",
            str(outfile),
        ]

    def run(self):
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
        return self._return_code

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value: Union[str, bytes]) -> None:
        if isinstance(value, bytes):
            self._output = value.decode(sys.stdin.encoding)
        elif isinstance(value, str):
            self._output = value

    @property
    def error(self) -> str:
        return self._error

    @error.setter
    def error(self, value: Union[str, bytes]) -> None:
        if isinstance(value, bytes):
            self._error = value.decode(sys.stdin.encoding)
        elif isinstance(value, str):
            self._error = value

    @property
    def script(self) -> str:
        return self._script

    @property
    def args(self) -> list:
        return self._args

    @args.setter
    def args(self, args: list) -> None:
        self._args = args


class UserArgs:
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
        self._decimation = 0

    @property
    def cavity_number_str(self) -> str:
        return self._cavity_number_str

    @cavity_number_str.setter
    def cavity_number_str(self, value: str) -> None:
        self._cavity_number_str = value

    @property
    def cavity_number_list(self) -> list:
        return self._cavity_number_list

    @cavity_number_list.setter
    def cavity_number_list(self, value: list) -> None:
        self._cavity_number_list = value

    @property
    def cryomodule(self) -> str:
        return self._cryomodule_str

    @cryomodule.setter
    def cryomodule(self, value: str) -> None:
        self._cryomodule_str = value

    @property
    def cryomodule_id(self) -> str:
        return self._cmid

    @cryomodule_id.setter
    def cryomodule_id(self, value: str) -> None:
        self._cmid = value

    @property
    def num_buffers(self) -> str:
        return self._n_buffers

    @num_buffers.setter
    def num_buffers(self, value: str) -> None:
        self._n_buffers = value

    @property
    def decimation_amount(self):
        return self._decimation

    @decimation_amount.setter
    def decimation_amount(self, value):
        # only powers of 2.
        if ceil(log2(value)) != floor(log2(value)):
            print("Only able to set decimation to powers of 2.")
            return
        self._decimation = value

    @property
    def linac(self) -> str:
        return self._linac

    @linac.setter
    def linac(self, value: str) -> None:
        self._linac = value

    @property
    def rack(self) -> int:
        return self._rack

    @property
    def rack_str(self) -> str:
        return "B" if self.rack else "A"

    @rack.setter
    def rack(self, value: int) -> None:
        self._rack = value

    @property
    def rack_delta(self) -> int:
        return self._rack_delta

    @rack_delta.setter
    def rack_delta(self, value: int) -> None:
        self._rack_delta = value

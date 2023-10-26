import os
from datetime import datetime


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
        self._rack = -1
        self._rack_delta = -1

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
    def linac(self) -> str:
        return self._linac

    @linac.setter
    def linac(self, value: str) -> None:
        self._linac = value

    @property
    def rack(self) -> int:
        return self._rack

    @rack.setter
    def rack(self, value: int) -> None:
        self._rack = value

    @property
    def rack_delta(self) -> int:
        return self._rack_delta

    @rack_delta.setter
    def rack_delta(self, value: int) -> None:
        self._rack_delta = value


class Model:
    user_arguments: UserArgs

    def __init__(self):
        self.name = "model"
        self.user_arguments = UserArgs()
        self._save_root_location = ""
        self._save_location = ""
        self._start_date = datetime.now()

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
        year = str(self.start_date.year)
        month = "%02d" % self.start_date.month
        day = "%02d" % self.start_date.day
        self.save_location = os.path.join(self.save_location, year, month, day)


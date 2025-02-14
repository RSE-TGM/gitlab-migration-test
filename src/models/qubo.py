from typing import List
from datetime import datetime
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class Qubo:
    """ see the FRER QUBO 96x96 datasheet in the docs.
    """

    _fields = ["VL1-N", "VL2-N", "VL3-N", "VL1-L2", "VL2-L3", "VL3-L1"] + ["IL1", "IL2", "IL3"] + ["F", "P", "Q"]
    _units = ["mV"] * 6 + ["mA"] * 3 + ["mHz", "W", "VAr"]
    f_units = [f"{f}_{u}" for f, u in zip(_fields, _units)]

    sql_cols = ["utc_timestamp"] + f_units
    sql_df: pd.DataFrame = pd.DataFrame(columns=sql_cols)
    nr_measurements = len(f_units)
    register_start: int = 256
    register_length: int = nr_measurements * 2  # FRER/QUBO uses val = HI*2^16 + LB*2^0

    def convert_registers_to_df_values(self, regs: List[int]) -> pd.DataFrame:
        """ The register conversion proceeds as explained in the example below:

        :param regs: (example) [3, 31977, 3, 35334, 3, 33952, 6, 4802, 6, 6791, 6, 5727, 0, 28083, ...]
        :return: pandas df

        1. zip two-by-two the items in the input regs (which is 1D array) and get a 2D array, such that:
        regs_2D_array = [ [3, 31977], [3, 35334], [3, 33952], [6,  4802], [6,  6791], [6,  5727], [0, 28083], ...]

        2. multiply the first 'column' of the regs_2D_array by the factor 65536 (= 2^16), such that:
        regs_2D_array = [ [196608, 31977], [196608,35334], [196608, 33952], ... ]

        3. sum the zipped elements to get the integer values which correspond to the measurements and assign the values
        to the correct columns in the pandas dataframe

        """
        # step 1
        regs_2D_array = np.array(np.split(np.array(regs), self.nr_measurements))
        # step 2
        regs_2D_array[:, 0] *= 65536  # 65536 = 2^16
        # step 3
        self.sql_df.loc[0, self.f_units] = np.sum(regs_2D_array, axis=1)
        self.sql_df.loc[0, "utc_timestamp"] = datetime.now()

        return self.sql_df

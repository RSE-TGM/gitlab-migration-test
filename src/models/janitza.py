from typing import List, Generator
from datetime import datetime
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class Janitza:
    """ see the Janitza UMG604-PRO datasheet in the docs. """

    _fields = ["VL1-N", "VL2-N", "VL3-N", "VL1-L2", "VL2-L3", "VL3-L1"] + \
              ["IL1", "IL2", "IL3", "ITot"] + \
              ["P1", "P2", "P3", "PTot"] + \
              ["S1", "S2", "S3", "STot"] + \
              ["Q1", "Q2", "Q3", "QTot"] + \
              ["cos_phi1", "cos_phi2", "cos_phi3"] + ["freq"] + ["Phase_Seq"] + \
              ["RlEn1", "RlEn2", "RlEn3", "RlEn13",
               "RlEn1_cons", "RlEn2_c", "RlEn3_cons", "RlEn13_cons",
               "RlEn1_dlv", "RlEn2_dlv", "RlEn3_dlv", "RlEn13_dlv"] + \
              ["AppE1", "AppE2", "AppE3", "AppE13"] + \
              ["ReactEn1", "ReactE2", "ReactE3", "ReactE13",
               "ReactE1_ind", "ReactE2_ind", "ReactE3_ind", "ReactE13_ind",
               "ReactE1_cap", "ReactE2_cap", "ReactE3_cap", "ReactE3_cap"] + \
              ["H_UL1N", "H_UL2N", "H_UL3N", "H_IL1", "H_IL2", "H_IL3"]

    _units = ["V"] * 6 + \
             ["A"] * 4 + ["W"] * 4 + ["VA"] * 4 + ["var"] * 4 + \
             ["nr"] * 3 + ["Hz"] + ["nr"] + \
             ["Wh"] * 12 + \
             ["VAh"] * 4 + \
             ["varh"] * 12 + \
             ["nr"] * 6

    f_units = [f"{f}_{u}" for f, u in zip(_fields, _units)]

    sql_cols = ["utc_timestamp"] + f_units
    sql_df: pd.DataFrame = pd.DataFrame(columns=sql_cols)
    nr_measurements = len(f_units)

    register_start: int = 19000
    register_length: int = nr_measurements * 2

    def convert_registers_to_df_values(self, regs: List[int]) -> pd.DataFrame:
        """ The register conversion proceeds as explained in the example below:

        :param regs: (example) [17250, 17789, 17250, 43978, 17251, 22677,  .. ]
        :return: pandas df

        1. zip two-by-two the numbers in the input register (which is given as 1D array) and get a 2D array, such that:
        regs_2D_array = [ [17250, 17789], [17250, 1743978], ...]

        2. convert the zipped couples to their binary representation

        3. convert the binaries to the float values according to ieee754 std (sign * 2^exp * mantissa, see for example
         https://www.h-schmidt.net/FloatConverter/IEEE754.html)

        NB: [17250, 17789] --> 01000011011000100100010101111101 --> +1 * 2^7 * 1,776.. --> 226.271

        """
        # step 1
        regs_2D_array = np.array(np.split(np.array(regs), self.nr_measurements))

        # step 2 yield binaries from register values
        binaries_ieee754 = self.registers_to_binary(regs_2D_array)

        # step 3 calculate the ieee754 floating point numbers from binaries and set them as df values
        self.sql_df.loc[0, self.sql_cols[1]:] = [self.binary_to_value(_) for _ in binaries_ieee754]  # type: ignore
        self.sql_df.loc[0, self.sql_cols[0]] = datetime.now()

        return self.sql_df[
            [
                'utc_timestamp', 'freq_Hz',
                'VL1-N_V', 'VL2-N_V', 'VL3-N_V',
                'VL1-L2_V', 'VL2-L3_V', 'VL3-L1_V',
                'IL1_A', 'IL2_A', 'IL3_A', 'ITot_A',
                'P1_W', 'P2_W', 'P3_W', 'PTot_W',
                'S1_VA', 'S2_VA', 'S3_VA', 'STot_VA',
                'Q1_var', 'Q2_var', 'Q3_var', 'QTot_var',
                'RlEn1_Wh', 'RlEn2_Wh', 'RlEn3_Wh', 'RlEn13_Wh',
                'ReactEn1_varh', 'ReactE2_varh', 'ReactE3_varh', 'ReactE13_varh',
                'H_UL1N_nr', 'H_UL2N_nr', 'H_UL3N_nr', 'H_IL1_nr', 'H_IL2_nr', 'H_IL3_nr'
            ]
        ]

    @staticmethod
    def registers_to_binary(regs_2D_array: np.ndarray) -> Generator:
        for reg in regs_2D_array:
            yield '{0:016b}'.format(reg[0]) + '{0:016b}'.format(reg[1])

    @staticmethod
    def binary_to_value(binary: str) -> float:
        sign = 1 if binary[0] == "0" else -1
        exponent = int(binary[1:9], 2) - 127
        mantissa = 1 + sum([int(x)/(2**n) for n, x in enumerate(binary[9:], start=1)])
        return sign * mantissa * 2**exponent

import pandas as pd
from datetime import datetime, timedelta
from typing import Final

class PVData:
    x: Final[int]

    def __init__(self, df_data: pd.DataFrame,x, verbose: bool = False):
        self.input = df_data
        self.verbose = verbose
        
        self.__define_range()

    def __define_range(self):
        self.from_date = pd.to_datetime(self.input['DateTime']).min().date()
        self.to_date = pd.to_datetime(self.input['DateTime']).max().date()
        self.x=1

        print(self.x)
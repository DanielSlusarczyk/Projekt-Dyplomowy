import pandas as pd
from datetime import timedelta
from typing import Final
from source.Operation import *

class PVData:
    from_date: Final[str]
    to_date: Final[str]
    input_data: Final[pd.DataFrame]


    def __init__(self, df_data: pd.DataFrame, verbose: bool = False):
        self.input_data = df_data
        self.verbose = verbose
        
        self.__define_range()
        self.__fill()

    def __define_range(self):
        self.from_date = pd.to_datetime(self.input_data['DateTime']).min().date()
        self.to_date = pd.to_datetime(self.input_data['DateTime']).max().date()

        if self.verbose:
            print(f'From %s to %s' % (self.from_date, self.to_date))

    def __fill(self):
        self.input_data['DateTime'] = pd.to_datetime(self.input_data['DateTime'])

        tmp_date = self.from_date

        while tmp_date <= self.to_date:
            year, month, day = split_data(tmp_date)
            
            if len(pv[(pv['Year'] == year) & (pv['Month'] == month) & (pv['Day'] == day)]) == 0:
                pv.loc[len(pv)]=['%s-%s-%s' % (year, month, day), 0, year, month, day, '00', '00', '00']
                print('Day %s is missing' % (from_date))

            tmp_date += timedelta(days=1)
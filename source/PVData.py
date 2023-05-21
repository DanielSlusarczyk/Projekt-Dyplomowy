import pandas as pd
from datetime import timedelta
from typing import Final
from source.Operation import *

class PVData:
    from_date: Final[str]
    to_date: Final[str]
    input_data: Final[pd.DataFrame]
    grouped_data = {}
    
    def __init__(self, df_data: pd.DataFrame, verbose: bool = False):
        self.input_data = df_data
        self.verbose = verbose

        self.__define_types()
        self.__define_range()
        self.__fill()
        self.__split()

    def get(self, columns=None) -> pd.DataFrame:
        if columns is None:
            return self.data
        else:
            return self.data[columns]
        
    def group(self, by, function='mean') -> pd.DataFrame:

        data = self.data.drop(['DateTime', 'Time', 'Date'], axis=1)

        if str(by) in self.grouped_data:
            data = self.grouped_data[str(by)]
        else:
            data = data.groupby(by)
            self.grouped_data[str(by)] = data

        if function == 'mean':
            return pd.DataFrame(data.mean()).reset_index()
        
        if function == 'count':
            return pd.DataFrame(data.size()).reset_index()

        raise TypeError("Unimplemented method")

    def __define_types(self):
        self.input_data.rename(columns={'Moc chwilowa PV': 'PV_output'}, inplace=True)
        self.input_data['DateTime'] = pd.to_datetime(self.input_data['DateTime'])
    
    def __define_range(self):
        self.from_date = self.input_data['DateTime'].min().date()
        self.to_date = self.input_data['DateTime'].max().date()

        if self.verbose:
            print(f'Dataset from %s to %s' % (self.from_date, self.to_date))

    def __fill(self):
        self.data = self.input_data.copy()
        tmp_date = self.from_date

        if self.verbose:
            print('Missing days: ', end='')

        # Fill missing probes from day with example probe     
        while tmp_date <= self.to_date:

            if not tmp_date in self.input_data['DateTime'].dt.date.values:
                if self.verbose:
                    print('[%s] ' % (tmp_date), end='')

                self.data.loc[len(self.data)] = {
                    'DateTime' : pd.to_datetime('%s 12:00:00' % (tmp_date)),
                    'Pv_output' : 0}

            tmp_date += timedelta(days=1)
        
        if self.verbose:
            print('')

        self.data.sort_values(by='DateTime', inplace=True)
        
    def __split(self):
        self.data['Year'] = self.data['DateTime'].dt.year
        self.data['Month'] = self.data['DateTime'].dt.month
        self.data['Day'] = self.data['DateTime'].dt.day
        self.data['Hour'] = self.data['DateTime'].dt.hour
        self.data['Minute'] = self.data['DateTime'].dt.minute
        self.data['Second'] = self.data['DateTime'].dt.second
        self.data['Date'] = self.data['DateTime'].dt.date
        self.data['Time'] = self.data['DateTime'].dt.time
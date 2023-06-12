import calendar
import pandas as pd
import numpy as np
from datetime import timedelta
from typing import Final
from source.Operation import *
from sklearn.preprocessing import MinMaxScaler

class PVData:
    from_date: Final[str]
    to_date: Final[str]
    input_data: Final[pd.DataFrame]

    grouped_data = {}
    production_data = None

    max_production = None
    nmb_of_days = None
    nmb_of_months = None
    nmb_of_years = None
    month_names = dict((i, month_name) for i, month_name in enumerate(calendar.month_name) if i != 0)
    
    def __init__(self, df_data: pd.DataFrame, verbose: bool = False):
        self.input_data = df_data
        self.verbose = verbose

        self.__define_types()
        self.__define_range()
        self.__fill()
        self.__split()
        self.__info()

    def get(self, columns=None) -> pd.DataFrame:
        if columns is None:
            return self.data
        else:
            return pd.DataFrame(self.data[columns])
        
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
            return pd.DataFrame(data.size().reset_index(name='Count'))
        
        if function == 'min':
            return pd.DataFrame(data.min()).reset_index()
        
        if function == 'sum':
            return pd.DataFrame(data.sum()).reset_index()

        if function == 'max':
            return pd.DataFrame(data.max()).reset_index()

        raise TypeError("Unimplemented method")
    
    def production(self, year=None, month=None, day=None) -> pd.DataFrame:
        if self.production_data is None:
            data = self.get(columns=['Time', 'Date', 'DateTime'])

            # Start and end of production
            start_per_day = pd.DataFrame(data.groupby(['Date']).min().reset_index())
            end_per_day = pd.DataFrame(data.groupby(['Date']).max().reset_index())

            # Time of production
            time_diff = end_per_day['DateTime'] - start_per_day['DateTime']
            pv_timing = pd.DataFrame({'Date' : start_per_day['Date'], 'Start' : start_per_day['Time'], 'End' : end_per_day['Time'], 'Time': time_diff.dt.total_seconds() / 3600})

            # Prepare dateframe
            per_day = self.group(['Year', 'Month', 'Day'])[['Year', 'Month', 'Day', 'PV_output']]
            per_day['Time'] = pv_timing['Time']
            per_day['Output'] = pv_timing['Time'] * per_day['PV_output']
            per_day.rename(columns={'PV_output': 'Avg_output'}, inplace=True)

            self.production_data = per_day

            self.max_production = per_day['Output'].max()

        filtered_date = self.production_data
        if year is not None:
            filtered_date = filtered_date[(filtered_date['Year'] == year)]

            if month is not None:
                filtered_date = filtered_date[(filtered_date['Month'] == month)]

                if day is not None:
                    filtered_date = filtered_date[(filtered_date['Day'] == day)]

        return pd.DataFrame(filtered_date)
    
    def samples(self, year=None, month=None, day=None, scale=None, group_factor=1, feature_range=(0, 1)) -> pd.DataFrame:

        filtered_date = self.data
        scaled_cols = []

        if year is not None:
            filtered_date = filtered_date[(filtered_date['Year'] == year)]

            if month is not None:
                filtered_date = filtered_date[(filtered_date['Month'] == month)]

                if day is not None:
                    filtered_date = filtered_date[(filtered_date['Day'] == day)]

        filtered_date['PlotTime'] = filtered_date['Hour'] * 3600 + filtered_date['Minute'] * 60 + filtered_date['Second']

        if scale is not None:
            scaler = MinMaxScaler(feature_range=feature_range)
            scaled_cols = [col + '_scaled' for col in scale]
            filtered_date.reset_index(drop=True, inplace=True)

            filtered_date[scaled_cols] = pd.DataFrame(scaler.fit_transform(filtered_date[scale]), columns=scale)

        if group_factor > 1:
            filtered_date = filtered_date.assign(Group=lambda x: np.floor(x['Minute']/group_factor))
            filtered_date = filtered_date[['Date', 'Hour', 'Group', 'PlotTime', 'PV_output'] + scaled_cols].groupby(['Date', 'Hour', 'Group']).mean().reset_index()
        
        return pd.DataFrame(filtered_date)


    def __define_types(self):
        self.input_data.rename(columns={'Moc chwilowa PV': 'PV_output'}, inplace=True)
        self.input_data['DateTime'] = pd.to_datetime(self.input_data['DateTime'])
        self.input_data['PV_output'] = self.input_data['PV_output'].astype('float')
    
    def __define_range(self):
        self.from_date = self.input_data['DateTime'].min().date()
        self.to_date = self.input_data['DateTime'].max().date()

        if self.verbose:
            print(f'Dataset from %s to %s' % (self.from_date, self.to_date))

    def __fill(self):
        self.data = pd.DataFrame(self.input_data)
        tmp_date = self.from_date

        if self.verbose:
            print('Missing days: ', end='')

        
        row_index = 0
        nmb_of_rows = len(self.input_data)
        missing_days = []

        # Find missing days
        while tmp_date <= self.to_date:
            if tmp_date == self.input_data.at[row_index, 'DateTime'].date():

                while row_index < nmb_of_rows and tmp_date == self.input_data.at[row_index, 'DateTime'].date():
                    row_index += 1

                tmp_date += timedelta(days=1)
            else:
                missing_days.append(tmp_date)
                tmp_date += timedelta(days=1)
        
        # Fill missing days
        for missing_day in missing_days:
            if self.verbose:
                print('[%s] ' % (missing_day), end='')

            self.data.loc[len(self.data)] = {
                'DateTime' : pd.to_datetime('%s 12:00:00' % (missing_day)),
                'PV_output' : 0}
        
        if self.verbose:
            print('\nMissing days: %s\n' % (len(missing_days)))

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

    def __info(self):
        days = self.group(['Year', 'Month', 'Day'])
        self.nmb_of_days = len(days)

        months = self.group(['Year', 'Month'])
        self.nmb_of_months = len(months)

        years = self.group(['Year'])
        self.nmb_of_years = len(years)

        if self.verbose:
            print('Summary:\n\tYears: \t\t%s \n\tMonths: \t%s \n\tDays: \t\t%s' %(self.nmb_of_years, self.nmb_of_months, self.nmb_of_days))
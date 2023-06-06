import calendar
import pandas as pd
from typing import Final
from source.Operation import *
from sklearn.preprocessing import MinMaxScaler

class WData:
    from_date: Final[str]
    to_date: Final[str]
    input_data: Final[pd.DataFrame]

    grouped_data = {}

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
        self.__split()
        self.__info()

    def get(self, columns=None) -> pd.DataFrame:
        if columns is None:
            return self.data
        else:
            return pd.DataFrame(self.data[columns])
    
    def samples(self, year=None, month=None, day=None, scale=None, feature_range=(0, 1)) -> pd.DataFrame:

        filtered_date = self.data
        if year is not None:
            filtered_date = filtered_date[(filtered_date['Year'] == year)]

            if month is not None:
                filtered_date = filtered_date[(filtered_date['Month'] == month)]

                if day is not None:
                    filtered_date = filtered_date[(filtered_date['Day'] == day)]

        filtered_date['PlotTime'] = filtered_date['Hour'] * 3600 + filtered_date['Minute'] * 60 + filtered_date['Second']

        if scale is not None:
            scaler = MinMaxScaler(feature_range=feature_range)
            filtered_date.reset_index(drop=True, inplace=True)

            filtered_date[scale] = pd.DataFrame(scaler.fit_transform(filtered_date[scale]), columns=scale)
        
        return pd.DataFrame(filtered_date)

    def __define_types(self):
        self.input_data.rename(columns={'PeriodStart': 'DateTime'}, inplace=True)
        self.input_data['DateTime'] = pd.to_datetime(self.input_data['DateTime'])
        self.input_data['DateTime'] = self.input_data['DateTime'].dt.tz_convert(None)

        self.input_data = self.input_data.drop(['PeriodEnd'], axis=1)
    
    def __define_range(self):
        self.from_date = self.input_data['DateTime'].min().date()
        self.to_date = self.input_data['DateTime'].max().date()

        if self.verbose:
            print(f'Dataset from %s to %s' % (self.from_date, self.to_date))

        self.data = pd.DataFrame(self.input_data)
        
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
        days = self.data.groupby(['Year', 'Month', 'Day'])
        self.nmb_of_days = len(days)

        months = self.data.groupby(['Year', 'Month'])
        self.nmb_of_months = len(months)

        years = self.data.groupby(['Year'])
        self.nmb_of_years = len(years)

        if self.verbose:
            print('Summary:\n\tYears: \t%s \n\tMonths: \t%s \n\tDays: \t%s' %(self.nmb_of_years, self.nmb_of_months, self.nmb_of_days))
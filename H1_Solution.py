import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame


def getUniqueAscii(file: str) -> DataFrame:
    """
    Given the country data, return a pandas dataframe, with cleaned city-city_ascii mapping
    :param file: str, countries' csv data file
    :return: a cleaned pandas dataframe
    """
    df = pd.read_csv(file)
    df = df.dropna()
    # print(df)
    df = df[['city', 'city_ascii', 'lat']]
    df = df.drop_duplicates(subset=['city'])
    # print(df)
    return df


def joinData(temp_data: DataFrame, ascii_data: DataFrame) -> DataFrame:
    """
    Given two dataframes, join them based on common column and clean the data
    :param temp_data: the cleaned temperature dataframe
    :param ascii_data: the cleaned city-city_ascii mapping dataframe
    :return: a joined and cleaned dataframe
    """
    # joined_df = temp_data.set_index('City').join(asc_data.set_index('city'))
    joined_df = pd.merge(temp_data, ascii_data, how='outer', on='city')
    print(joined_df)
    new_df = joined_df.drop_duplicates(
        subset=['city', 'Year'],
        keep='last').reset_index(drop=True)
    print(new_df)
    return new_df


def getAvgTemp(file: str) -> DataFrame:
    """
    Given a csv date with country, monthly temperature
    :param file: str, a csv data file
    :return: pandas.dataframe
    """
    df = pd.read_csv(file)
    df = df.dropna()
    # print(df)
    # add a column of year extract from date info
    df['Year'] = pd.DatetimeIndex(df['dt']).year
    df = df.rename(columns={'City': 'city'})
    # group by city and year, and calculate the avg temp
    group_df = df.groupby(['city', 'Year'])
    mean_df = group_df['AverageTemperature'].mean()
    mean_df = mean_df.reset_index()
    # print(mean_df)
    return mean_df


if __name__ == '__main__':
    tem_data = getAvgTemp('h1_data/GlobalLandTemperaturesByCity.csv')
    asc_data = getUniqueAscii('h1_data/worldcities.csv')
    joined = joinData(tem_data, asc_data)
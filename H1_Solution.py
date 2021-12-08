import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame


def get_unique_ascii(file: str) -> DataFrame:
    """
    Given the country data, return a pandas dataframe, with cleaned city-city_ascii mapping
    :param file: str, countries' csv data file
    :return: a cleaned pandas dataframe
    """
    df = pd.read_csv(file)
    df = df.dropna()
    # print(df)
    df = df[["city", "city_ascii", "lat"]]
    df = df.drop_duplicates(subset=["city"])  # remove duplicates
    # print(df)
    return df


def join_data(temp_data: DataFrame, ascii_data: DataFrame) -> DataFrame:
    """
    Given two dataframes, join them based on common column and clean the data
    :param temp_data: the cleaned temperature dataframe
    :param ascii_data: the cleaned city-city_ascii mapping dataframe
    :return: a joined and cleaned dataframe
    """
    # joined_df = temp_data.set_index('City').join(asc_data.set_index('city'))
    # merge the two tables, based on common column
    joined_df = pd.merge(temp_data, ascii_data, how="outer", on="city")
    # print(joined_df)
    new_df = joined_df.drop_duplicates(
        subset=["city", "Year"], keep="last"
    ).reset_index(drop=True)
    new_df.dropna()
    # print(new_df)
    return new_df


def get_avg_temp(file: str) -> DataFrame:
    """
    Given a csv date with country, monthly temperature
    :param file: str, a csv data file
    :return: pandas.dataframe
    """
    df = pd.read_csv(file)
    df = df.dropna()
    # print(df)
    # add a column of year extract from date info
    df["Year"] = pd.DatetimeIndex(df["dt"]).year
    # update some columns' name
    df = df.rename(columns={"City": "city", "AverageTemperature": "AvgTemp"})
    # group by city and year, and calculate the avg temp
    group_df = df.groupby(["city", "Year"])
    mean_df = group_df["AvgTemp"].mean()
    mean_df = mean_df.reset_index()
    # print(mean_df)
    return mean_df


def plot_temp_change(city_name: str, year: int, df: DataFrame) -> None:
    """
    Given information of city, start year, and pandes dataframe,
    plot the temperature change at that city since the given start year
    :param city_name: str, city we want to check
    :param year: int, the start year we want to be plotted
    :param df: pandas.dataframe, a cleaned dataframe including useful infos
    :return: None
    """
    df = df[df.Year >= year]  # extract the dataframe by given info
    city_case = df[df.city == city_name]
    # print(city_case)
    plt.plot(city_case.Year, city_case.AvgTemp)
    plt.xlabel("year")
    plt.ylabel("temperature(°C)")
    plt.title("temperature change at {}, since {}".format(city_name, year))
    plt.savefig("sample_output/output1.png")
    # plt.show()


def plot_change_compare(city1: str, city2: str, year: int, df: DataFrame) -> None:
    """
    Given two cities and start year, plot a figure to show the percentage of change, based on the start value
    :param city1: str, the first city's name
    :param city2: str, the second city's name
    :param year: int, input start year
    :param df: pandas.Dataframe, a well cleaned dataframe, including related infos
    :return: None, (with a plot to show)
    """
    df = df[df.Year >= year]
    city1_case = df[df.city == city1]
    city2_case = df[df.city == city2]
    # compute the percentage of change
    plt.plot(city1_case.Year, city1_case.AvgTemp / city1_case.AvgTemp.iloc[0] * 100)
    plt.plot(city2_case.Year, city2_case.AvgTemp / city2_case.AvgTemp.iloc[0] * 100)
    plt.legend([city1, city2])
    plt.xlabel("year")
    plt.ylabel("temperature change (temp / start * 100)")
    plt.title("temperature change comparison, since {}".format(year))
    plt.savefig("sample_output/output2.png")
    # plt.show()


def change_in_100years(df: DataFrame) -> None:
    """
    Given a dataframe of city and temperature in different years, create a scatter plot that shows
    the temperature change from 1901 to 2000, according their latitude value
    :param df: pandas.Dataframe, raw temperature data for city in different years
    :return: None, with a plot shows
    """
    df = df[df.lat >= 0]  # get only northern hemisphere
    df = df[df.Year.between(1901, 2000)]  # take data between 1901 and 2000
    # group by city and calculate the difference between first temp and last temp
    grouped_data = df.groupby(["city", "lat"])["AvgTemp"].agg(["first", "last"])
    grouped_data["diffs"] = grouped_data["last"] - grouped_data["first"]
    grouped_data = grouped_data.reset_index()
    # print(grouped_data)
    # create the scatter plot
    plt.scatter(grouped_data["lat"], grouped_data["diffs"])
    plt.xlabel("latitude")
    plt.ylabel("temperature change (1901--2000)")
    plt.title("scatter plot of temperature changes in various cities")
    plt.savefig("sample_output/output3.png")
    # plt.show()
    # return grouped_data


if __name__ == "__main__":

    # process and clean the data files
    tem_data = get_avg_temp("h1_data/GlobalLandTemperaturesByCity.csv")
    asc_data = get_unique_ascii("h1_data/worldcities.csv")

    # join the table for use, mapping city to ascii name
    joined_data = join_data(tem_data, asc_data)

    # print(joined_data)
    # plot temperature change for given city
    plot_temp_change("Miami", 1980, joined_data)

    # comparison of the rate of change between the two cities
    plot_change_compare("Seattle", "Miami", 1950, joined_data)

    # plot the scatter plot, changes by latitude
    change_in_100years(joined_data)

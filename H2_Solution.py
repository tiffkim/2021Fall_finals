import pandas as pd
import matplotlib.pyplot as plt

# Hypothesis #2: Countries with ascending GDP and population have growing CO2 emission per capita than
# countries with descending GDP and population. Datasets needed: GDP, population, CO2 emission by countries
from pandas import DataFrame


def get_data(filename: str) -> pd.DataFrame:
    """
    read in the given file and store clean country data in pandas dataframe
    :param filename: str, a given file name
    :return: pandas.Dataframe
    """
    df = pd.read_csv(filename)
    columns = ["Country Code"] + [str(i) for i in range(2010, 2021)]
    return df[columns].reset_index(drop=True).rename(columns={"Country Code": "Code"})


def get_co2_data(filename: str) -> pd.DataFrame:
    """
    read in the given file and store cleaned data in pandas Dataframe
    :param filename: str, a given file name
    :return: pandas.Dataframe
    """
    df = pd.read_csv(filename)
    return df[df["Year"].between(2010, 2020, inclusive="both")].reset_index(drop=True)


def merge_data(
    gdp_data: pd.DataFrame, pop_data: pd.DataFrame, co2_data: pd.DataFrame
) -> pd.DataFrame:
    """
    given 3 dataframes with different information, join and merge to a single cleaned dataframe
    :param gdp_data: pandas.Dataframe of gdp info
    :param pop_data: pandas.Dataframe of pop info
    :param co2_data: pandas.Dataframe of co2 info
    :return: pandas.Dataframe
    """
    gdp_data = gdp_data.melt(
        id_vars=["Code"], var_name="Year", value_name="GDP growth %"
    )
    gdp_data["Year"] = gdp_data["Year"].astype(int)
    pop_data = pop_data.melt(id_vars=["Code"], var_name="Year", value_name="population")
    pop_data["Year"] = pop_data["Year"].astype(int)
    return (
        pd.merge(
            pd.merge(co2_data, gdp_data, how="left", on=["Code", "Year"]),
            pop_data,
            how="inner",
            on=["Code", "Year"],
        )
        .dropna()
        .reset_index(drop=True)
    )


def calculate_population_growth(grouped: pd.DataFrame, country: str) -> int:
    """
    given the grouped data and country, computed the growth of population
    :param grouped: a pandas.Dataframe
    :param country: str, country info
    :return: the int number the population growth
    """
    country_df = grouped.get_group(country)
    min_year = country_df["Year"].min()
    max_year = country_df["Year"].max()
    if max_year == 2020:
        max_year -= 1
    initial = country_df.loc[country_df["Year"] == min_year, "population"].values[0]
    final = country_df.loc[country_df["Year"] == max_year, "population"].values[0]
    return (final - initial) * 100 / initial


def calculate_avg_growth(grouped, country, column):
    """
    given the grouped data, country and column info
    :param grouped: a pandas.Dataframe
    :param country: str, country info
    :param column: str, column info
    :return: the int number the average growth
    """
    country_df = grouped.get_group(country)
    return country_df[country_df["Year"] != 2020][column].mean()


def get_country_data(df):
    """
    Given a dataframe, get country's data and generate a cleaned country dataframe
    :param df: a pandas.Dataframe
    :return: a pandas.Dataframe
    """
    grouped = df.groupby("Entity")
    countries = list()
    pop_growths = list()
    gdp_growths = list()
    avg_co2 = list()
    for country in df["Entity"].unique():
        countries.append(country)
        pop_growths.append(calculate_population_growth(grouped, country))
        gdp_growths.append(calculate_avg_growth(grouped, country, "GDP growth %"))
        avg_co2.append(
            calculate_avg_growth(grouped, country, "Annual CO2 emissions (per capita)")
        )
    data = {
        "country": countries,
        "population growth": pop_growths,
        "gdp growth": gdp_growths,
        "avg co2": avg_co2,
    }
    return pd.DataFrame(data)


def plot_correlation(
    population_growth: pd.Series,
    gdp_growth: pd.Series,
    avg_co2: pd.Series,
    country_df: DataFrame,
) -> None:
    """
    Given three pandas series, plot the correlation fiture
    :param population_growth:
    :param gdp_growth:
    :param avg_co2:
    :param country_df:
    :return: None, with a plot to show
    """
    x = country_df[population_growth]
    y = country_df[gdp_growth]
    c = country_df[avg_co2]
    # Plot...
    plt.scatter(x, y, c=c)
    cbar = plt.colorbar()
    cbar.set_label("Average Increas in Co2 Emission%")
    plt.xlabel("population growth %")
    plt.ylabel("gdp growth %")
    plt.title(
        "Average CO2 emission growth percentage by population growth and gdp growth"
    )
    plt.show()


def get_percentile(country_df):
    """
    Given a country dataframe, calculate and add percentile info to it
    :param country_df: pandas.Dataframe, with info of country
    :return: pandas.Dataframe, with percentile info in it.
    """
    country_df.loc[
        (
            country_df["population growth"]
            < country_df["population growth"].quantile(0.25)
        )
        & (country_df["gdp growth"] < country_df["gdp growth"].quantile(0.25)),
        "label",
    ] = "lower"
    country_df.loc[
        (
            country_df["population growth"]
            > country_df["population growth"].quantile(0.75)
        )
        & (country_df["gdp growth"] > country_df["gdp growth"].quantile(0.75)),
        "label",
    ] = "higher"
    country_df.dropna(inplace=True)
    return country_df


if __name__ == "__main__":
    gdp_df = get_data(
        "/Users/chanmitk/Downloads/API_NY.GDP.MKTP.KD.ZG_DS2_en_csv_v2_3358388/API_NY.GDP.MKTP.KD.ZG_DS2_en_csv_v2_3358388.csv"
    )
    pop_df = get_data(
        "/Users/chanmitk/Downloads/API_SP.POP.TOTL_DS2_en_csv_v2_3358390/API_SP.POP.TOTL_DS2_en_csv_v2_3358390.csv"
    )
    co2_df = get_co2_data("/Users/chanmitk/Desktop/co2.csv")
    merged_df = merge_data(gdp_df, pop_df, co2_df)
    country_df = get_country_data(merged_df)

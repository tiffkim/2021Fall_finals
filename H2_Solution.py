import pandas as pd
import matplotlib.pyplot as plt

#Hypothesis #2: Countries with ascending GDP and population have growing CO2 emission per capita than
#countries with descending GDP and population. Datasets needed: GDP, population, CO2 emission by countries


def get_data(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename)
    columns = ["Country Code"] + [str(i) for i in range(2010, 2021)]
    return df[columns].reset_index(drop=True).rename(columns={"Country Code": "Code"})


def get_co2_data(filename: str) -> pd.DataFrame:
    df = pd.read_csv(filename)
    return df[df["Year"].between(2010, 2020, inclusive="both")].reset_index(drop=True)


def merge_data(gdp_data: pd.DataFrame, pop_data: pd.DataFrame, co2_data: pd.DataFrame) -> pd.DataFrame:
    gdp_data = gdp_data.melt(id_vars=["Code"], var_name="Year", value_name="GDP growth %")
    gdp_data["Year"] = gdp_data["Year"].astype(int)
    pop_data = pop_data.melt(id_vars=["Code"], var_name="Year", value_name="population")
    pop_data["Year"] = pop_data["Year"].astype(int)
    return pd.merge(
        pd.merge(
            co2_data,
            gdp_data,
            how='left',
            on=['Code', 'Year']
        ),
        pop_data,
        how='inner',
        on=['Code', 'Year']
    ).dropna().reset_index(drop=True)


def calculate_population_growth(grouped, country):
    country_df = grouped.get_group(country)
    min_year = country_df["Year"].min()
    max_year = country_df["Year"].max()
    if max_year == 2020:
        max_year -= 1
    initial = country_df.loc[country_df["Year"] == min_year, "population"].values[0]
    final = country_df.loc[country_df["Year"] == max_year, "population"].values[0]
    return (final - initial) * 100 / initial


def calculate_avg_growth(grouped, country, column):
    country_df = grouped.get_group(country)
    return country_df[country_df["Year"] != 2020][column].mean()

def get_country_data(df):
    grouped = df.groupby("Entity")
    countries = list()
    pop_growths = list()
    gdp_growths = list()
    avg_co2 = list()
    for country in df["Entity"].unique():
        countries.append(country)
        pop_growths.append(calculate_population_growth(grouped, country))
        gdp_growths.append(calculate_avg_growth(grouped, country, "GDP growth %"))
        avg_co2.append(calculate_avg_growth(grouped, country, "Annual CO2 emissions (per capita)"))
    data = {"country": countries, "population growth": pop_growths, "gdp growth": gdp_growths, "avg co2": avg_co2}
    return pd.DataFrame(data)

def plot_correlation(population growth: pd.Series, gdp growth: pd.Series, avg co2: pd.Series, country_df: DataFrame) -> None:
    """
    Given three variables: population growth and gdp growth percentage and average co2 emission in percentage.
    :param population growth: pd.Series, the population growth percentage values
    :param gdp growth: pd.Series, the gdp growth percentage values
    :param avg co2: pd.Series, the average growth of co2 emission in percentage
    :param country_df: pandas.Dataframe, all three variables by countries
    :return: None, (with a plot to show)
    """
    x = country_df["population growth"]
    y = country_df["gdp growth"]
    c = country_df["avg co2"]
    # Plot...
    plt.scatter(x, y, c=c)
    cbar = plt.colorbar()
    cbar.set_label('Average Increas in Co2 Emission%')
    plt.xlabel('population growth %')
    plt.ylabel('gdp growth %')
    plt.title('Average CO2 emission growth percentage by population growth and gdp growth')
    plt.show()

def get_percentile(country_df):
    """
    Given th.
    :param population growth: pd.Series, the population growth percentage values
    :param gdp growth: pd.Series, the gdp growth percentage values
    :param avg co2: pd.Series, the average growth of co2 emission in percentage
    :param country_df: pandas.Dataframe, all three variables by countries
    :return: None, (with a plot to show)
    """
    country_df.loc[(country_df["population growth"] < country_df["population growth"].quantile(0.25)) & (
                country_df["gdp growth"] < country_df["gdp growth"].quantile(0.25)), "label"] = "lower"
    country_df.loc[(country_df["population growth"] > country_df["population growth"].quantile(0.75)) & (
                country_df["gdp growth"] > country_df["gdp growth"].quantile(0.75)), "label"] = "higher"
    country_df.dropna(inplace=True)
    return country_df


if __name__ == "__main__":
    gdp_df = get_data("/Users/chanmitk/Downloads/API_NY.GDP.MKTP.KD.ZG_DS2_en_csv_v2_3358388/API_NY.GDP.MKTP.KD.ZG_DS2_en_csv_v2_3358388.csv")
    pop_df = get_data("/Users/chanmitk/Downloads/API_SP.POP.TOTL_DS2_en_csv_v2_3358390/API_SP.POP.TOTL_DS2_en_csv_v2_3358390.csv")
    co2_df = get_co2_data("/Users/chanmitk/Desktop/co2.csv")
    merged_df = merge_data(gdp_df, pop_df, co2_df)
    country_df = get_country_data(merged_df)


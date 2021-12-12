import pandas as pd

#Hypothesis #2: Countries with ascending GDP and population emit higher CO2 per capita than
#countries with descending GDP. Datasets needed: GDP, population, CO2 emission by countries


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


if __name__ == "__main__":
    gdp_df = get_data("/Users/chanmitk/Downloads/API_NY.GDP.MKTP.KD.ZG_DS2_en_csv_v2_3358388/API_NY.GDP.MKTP.KD.ZG_DS2_en_csv_v2_3358388.csv")
    pop_df = get_data("/Users/chanmitk/Downloads/API_SP.POP.TOTL_DS2_en_csv_v2_3358390/API_SP.POP.TOTL_DS2_en_csv_v2_3358390.csv")
    co2_df = get_co2_data("/Users/chanmitk/Desktop/co2.csv")
    merged_df = merge_data(gdp_df, pop_df, co2_df)
    country_df = get_country_data(merged_df)


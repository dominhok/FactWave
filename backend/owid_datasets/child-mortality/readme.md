# Child mortality rate - Data package

This data package contains the data that powers the chart ["Child mortality rate"](https://ourworldindata.org/grapher/child-mortality) on the Our World in Data website. It was downloaded on August 07, 2025.

## CSV Structure

The high level structure of the CSV file is that each row is an observation for an entity (usually a country or region) and a timepoint (usually a year).

The first two columns in the CSV file are "Entity" and "Code". "Entity" is the name of the entity (e.g. "United States"). "Code" is the OWID internal entity code that we use if the entity is a country or region. For normal countries, this is the same as the [iso alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) code of the entity (e.g. "USA") - for non-standard countries like historical countries these are custom codes.

The third column is either "Year" or "Day". If the data is annual, this is "Year" and contains only the year as an integer. If the column is "Day", the column contains a date string in the form "YYYY-MM-DD".

The final column is the data column, which is the time series that powers the chart. If the CSV data is downloaded using the "full data" option, then the column corresponds to the time series below. If the CSV data is downloaded using the "only selected data visible in the chart" option then the data column is transformed depending on the chart type and thus the association with the time series might not be as straightforward.

## Metadata.json structure

The .metadata.json file contains metadata about the data package. The "charts" key contains information to recreate the chart, like the title, subtitle etc.. The "columns" key contains information about each of the columns in the csv, like the unit, timespan covered, citation for the data etc..

## About the data

Our World in Data is almost never the original producer of the data - almost all of the data we use has been compiled by others. If you want to re-use data, it is your responsibility to ensure that you adhere to the sources' license and to credit them correctly. Please note that a single time series may have more than one source - e.g. when we stich together data from different time periods by different producers or when we calculate per capita metrics using population data from a second source.

## Detailed information about the data


## Child mortality rate – Long-run data – Gapminder; UN IGME
The long-run estimated share of newborns who die before reaching the age of five.
Last updated: April 25, 2025  
Date range: 1751–2023  
Unit: deaths per 100 live births  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
Gapminder (2015); UN Inter-agency Group for Child Mortality Estimation (2025) – processed by Our World in Data

#### Full citation
Gapminder (2015); UN Inter-agency Group for Child Mortality Estimation (2025) – processed by Our World in Data. “Child mortality rate – Gapminder; UN IGME – Long-run data” [dataset]. United Nations Inter-agency Group for Child Mortality Estimation, “United Nations Inter-agency Group for Child Mortality Estimation”; Gapminder, “Child mortality rate under age five v7”; Gapminder based on UN IGME & UN WPP, “Under-five Mortality v11”; Various sources, “Population” [original data].
Source: Gapminder (2015); UN Inter-agency Group for Child Mortality Estimation (2025) – processed by Our World In Data

### What you should know about this data
* What could be more tragic than the death of a young child? Child mortality, the death of children under the age of five, is still extremely common in our world today.
* The historical data makes clear that it doesn’t have to be this way: societies can protect their children and reduce child mortality to very low rates. For child mortality to reach low levels, many things have to go right at the same time: good healthcare, good nutrition, clean water and sanitation, maternal health, and high living standards. We can, therefore, think of child mortality as a proxy indicator of a country’s living conditions.
* The chart shows our long-run data on child mortality, which allows you to see how child mortality has changed in countries around the world. It combines data from two sources: Gapminder and the UN Inter-agency Group for Child Mortality Estimation (UN IGME).
* [Gapminder](https://www.gapminder.org/data/documentation/gd005/) provides estimates of child mortality rates from 1800 to 2015. The full list of sources used can be found in [their documentation](https://www.gapminder.org/data/documentation/gd005/).
* [UN IGME](https://childmortality.org/all-cause-mortality/data) provides estimates of child mortality rates for some countries from 1932 onward.
* For years where data from both sources is available, we prioritize the UN IGME data. See [this page](https://docs.google.com/spreadsheets/d/1n-WO7yEbi6sXPpeWrorSEVu8w_Yu5dM0n97q1h16L0g/edit?gid=0#gid=0) for more details on which source is used for each data point.
* This indicator is calculated as the number of children under the age of five who died in a given year, divided by the number of newborns in that year.

### Sources

#### United Nations Inter-agency Group for Child Mortality Estimation
Retrieved on: 2025-03-25  
Retrieved from: https://childmortality.org/all-cause-mortality/data  

#### Gapminder – Child mortality rate under age five
Retrieved on: 2023-09-18  
Retrieved from: https://www.gapminder.org/data/documentation/gd005/  

#### Gapminder based on UN IGME & UN WPP – Under-five Mortality
Retrieved on: 2023-09-21  
Retrieved from: https://docs.google.com/spreadsheets/d/1Av7eps_zEK73-AdbFYEmtTrwFKlfruBYXdrnXAOFVpM/edit#gid=501532268  

#### Various sources – Population
Retrieved on: 2024-07-11  
Retrieved from: https://ourworldindata.org/population-sources  

#### Notes on our processing step for this indicator
This indicator is a combination of data from two sources:
  - Gapminder, which provides estimates of child mortality rates for the years 1800 to 2015.
  - The UN Inter-agency Group for Child Mortality Estimation (UN IGME) provides estimates of child mortality rates, for some countries from 1932 onward.

For years where data from both sources is available, we prioritize the UN IGME data. See [this page](https://docs.google.com/spreadsheets/d/1n-WO7yEbi6sXPpeWrorSEVu8w_Yu5dM0n97q1h16L0g/edit?gid=0#gid=0) for more details on which source is used for each data point.

In the Gapminder dataset we remove rows where the source is labelled as "Guesstimate" or "Model based on Life Expectancy" to try and ensure we use the best available data.

We remove data for Austria before 1830 from the Gapminder dataset, as there is a jump in 1830 that is likely an error.


    
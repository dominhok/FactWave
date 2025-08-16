# Annual GDP growth - Data package

This data package contains the data that powers the chart ["Annual GDP growth"](https://ourworldindata.org/grapher/real-gdp-growth) on the Our World in Data website.

## CSV Structure

The high level structure of the CSV file is that each row is an observation for an entity (usually a country or region) and a timepoint (usually a year).

The first two columns in the CSV file are "Entity" and "Code". "Entity" is the name of the entity (e.g. "United States"). "Code" is the OWID internal entity code that we use if the entity is a country or region. For normal countries, this is the same as the [iso alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) code of the entity (e.g. "USA") - for non-standard countries like historical countries these are custom codes.

The third column is either "Year" or "Day". If the data is annual, this is "Year" and contains only the year as an integer. If the column is "Day", the column contains a date string in the form "YYYY-MM-DD".

The remaining columns are the data columns, each of which is a time series. If the CSV data is downloaded using the "full data" option, then each column corresponds to one time series below. If the CSV data is downloaded using the "only selected data visible in the chart" option then the data columns are transformed depending on the chart type and thus the association with the time series might not be as straightforward.

## Metadata.json structure

The .metadata.json file contains metadata about the data package. The "charts" key contains information to recreate the chart, like the title, subtitle etc.. The "columns" key contains information about each of the columns in the csv, like the unit, timespan covered, citation for the data etc..

## About the data

Our World in Data is almost never the original producer of the data - almost all of the data we use has been compiled by others. If you want to re-use data, it is your responsibility to ensure that you adhere to the sources' license and to credit them correctly. Please note that a single time series may have more than one source - e.g. when we stich together data from different time periods by different producers or when we calculate per capita metrics using population data from a second source.

### How we process data at Our World In Data
All data and visualizations on Our World in Data rely on data sourced from one or several original data providers. Preparing this original data involves several processing steps. Depending on the data, this can include standardizing country names and world region definitions, converting units, calculating derived indicators such as per capita measures, as well as adding or adapting metadata such as the name or the description given to an indicator.
[Read about our data pipeline](https://docs.owid.io/projects/etl/)

## Detailed information about each time series


## Gross domestic product, constant prices - Percent change - Observations
Annual percent change in gross domestic product. This data is adjusted for inflation.
Last updated: April 25, 2025  
Next update: April 2026  
Date range: 1980–2024  
Unit: %  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
International Monetary Fund (2025) – with minor processing by Our World in Data

#### Full citation
International Monetary Fund (2025) – with minor processing by Our World in Data. “Gross domestic product, constant prices - Percent change - Observations” [dataset]. International Monetary Fund, “World Economic Outlook (WEO) April 2025” [original data].
Source: International Monetary Fund (2025) – with minor processing by Our World In Data

### How is this data described by its producer - International Monetary Fund (2025)?
Gross domestic product, constant prices. Percent change. Annual percentages of constant price GDP are year-on-year changes; the base year is country-specific. Expenditure-based GDP is total final expenditures at purchasers' prices (including the f.o.b. value of exports of goods and services), less the f.o.b. value of imports of goods and services. [SNA 1993]

### Source

#### International Monetary Fund – World Economic Outlook (WEO)
Retrieved on: 2025-04-25  
Retrieved from: https://www.imf.org/en/Publications/WEO/weo-database/2025/april  


## Gross domestic product, constant prices - Percent change - Forecasts
Near-term projections of the annual percent change in gross domestic product. This data is adjusted for inflation.
Last updated: April 25, 2025  
Next update: April 2026  
Date range: 2010–2030  
Unit: %  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
International Monetary Fund (2025) – with minor processing by Our World in Data

#### Full citation
International Monetary Fund (2025) – with minor processing by Our World in Data. “Gross domestic product, constant prices - Percent change - Forecasts” [dataset]. International Monetary Fund, “World Economic Outlook (WEO) April 2025” [original data].
Source: International Monetary Fund (2025) – with minor processing by Our World In Data

### How is this data described by its producer - International Monetary Fund (2025)?
Gross domestic product, constant prices. Percent change. Annual percentages of constant price GDP are year-on-year changes; the base year is country-specific. Expenditure-based GDP is total final expenditures at purchasers' prices (including the f.o.b. value of exports of goods and services), less the f.o.b. value of imports of goods and services. [SNA 1993]

### Source

#### International Monetary Fund – World Economic Outlook (WEO)
Retrieved on: 2025-04-25  
Retrieved from: https://www.imf.org/en/Publications/WEO/weo-database/2025/april  


    
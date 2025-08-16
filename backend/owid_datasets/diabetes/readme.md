# Diabetes prevalence - Data package

This data package contains the data that powers the chart ["Diabetes prevalence"](https://ourworldindata.org/grapher/diabetes-prevalence) on the Our World in Data website. It was downloaded on August 07, 2025.

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


## Diabetes prevalence (% of population ages 20 to 79)
Last updated: January 24, 2025  
Next update: January 2026  
Date range: 2000–2021  
Unit: % of population ages 20 to 79  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
International Diabetes Federation, via World Bank (2025) – processed by Our World in Data

#### Full citation
International Diabetes Federation, via World Bank (2025) – processed by Our World in Data. “Diabetes prevalence (% of population ages 20 to 79)” [dataset]. International Diabetes Federation, via World Bank, “World Development Indicators” [original data].
Source: International Diabetes Federation, via World Bank (2025) – processed by Our World In Data

### How is this data described by its producer - International Diabetes Federation, via World Bank (2025)?
Diabetes prevalence refers to the percentage of people ages 20-79 who have type 1 or type 2 diabetes. It is calculated by adjusting to a standard population age-structure.

### Limitations and exceptions:
The limited availability of data on health status is a major constraint in assessing the health situation in developing countries. Surveillance data are lacking for many major public health concerns. Estimates of prevalence and incidence are available for some diseases but are often unreliable and incomplete. National health authorities differ widely in capacity and willingness to collect or report information.

### Source

#### International Diabetes Federation, via World Bank – World Development Indicators
Retrieved on: 2025-01-24  
Retrieved from: https://data.worldbank.org/indicator/SH.STA.DIAB.ZS  


    
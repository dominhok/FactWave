# Nuclear power generation - Data package

This data package contains the data that powers the chart ["Nuclear power generation"](https://ourworldindata.org/grapher/nuclear-energy-generation) on the Our World in Data website. It was downloaded on August 07, 2025.

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


## Electricity generation from nuclear
Measured in [terawatt-hours](#dod:watt-hours).
Last updated: June 27, 2025  
Next update: June 2026  
Date range: 1965–2024  
Unit: terawatt-hours  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
Ember (2025); Energy Institute - Statistical Review of World Energy (2025) – with major processing by Our World in Data

#### Full citation
Ember (2025); Energy Institute - Statistical Review of World Energy (2025) – with major processing by Our World in Data. “Electricity generation from nuclear” [dataset]. Ember, “Yearly Electricity Data Europe”; Ember, “Yearly Electricity Data”; Energy Institute, “Statistical Review of World Energy” [original data].
Source: Ember (2025), Energy Institute - Statistical Review of World Energy (2025) – with major processing by Our World In Data

### Sources

#### Ember – Yearly Electricity Data Europe
Retrieved on: 2025-05-12  
Retrieved from: https://ember-energy.org/data/yearly-electricity-data/  

#### Ember – Yearly Electricity Data
Retrieved on: 2025-05-12  
Retrieved from: https://ember-energy.org/data/yearly-electricity-data/  

#### Energy Institute – Statistical Review of World Energy
Retrieved on: 2025-06-27  
Retrieved from: https://www.energyinst.org/statistical-review/  

#### Notes on our processing step for this indicator
- While the Energy Institute (EI) provides a longer time series (dating back to 1965) than Ember (dating back only to 1990 for European countries and 2000 for other countries), EI does not cover all countries or all sources of electricity (for example, generation from bioenergy is missing). Therefore, when data from Ember is available for a given country and year, we use it as the primary data source. Where Ember data is unavailable, we supplement it with data from EI.


    
# Share of primary energy consumption from renewable sources - Data package

This data package contains the data that powers the chart ["Share of primary energy consumption from renewable sources"](https://ourworldindata.org/grapher/renewable-share-energy) on the Our World in Data website. It was downloaded on August 07, 2025.

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


## Share of primary energy consumption that comes from renewables – Using the substitution method
Measured as a percentage of the total [primary energy](#dod:primaryenergy), using the [substitution method](#dod:substitutionmethod).
Last updated: June 27, 2025  
Next update: June 2026  
Date range: 1965–2024  
Unit: %  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
Energy Institute - Statistical Review of World Energy (2025) – with major processing by Our World in Data

#### Full citation
Energy Institute - Statistical Review of World Energy (2025) – with major processing by Our World in Data. “Share of primary energy consumption that comes from renewables – Using the substitution method” [dataset]. Energy Institute, “Statistical Review of World Energy” [original data].
Source: Energy Institute - Statistical Review of World Energy (2025) – with major processing by Our World In Data

### What you should know about this data
* Figures are based on gross generation and do not account for cross-border electricity supply.
* Primary energy is measured using the "substitution method" (also called "input-equivalent" primary energy). This method is used for non-fossil sources of electricity (namely renewables and nuclear), and measures the amount of fossil fuels that would be required by thermal power stations to generate the same amount of non-fossil electricity.
For example, if a country's nuclear power generated 100 TWh of electricity, and assuming that the efficiency of a standard thermal power plant is 38%, the input-equivalent primary energy for this country would be 100 TWh / 0.38 = 263 TWh = 0.95 EJ. This input-equivalent primary energy takes account of the inefficiencies in energy production from fossil fuels and provides a better approximation of each source's share of energy consumption. You can find more details in [the Statistical Review of World Energy's methodology document](https://www.energyinst.org/__data/assets/pdf_file/0003/1055541/Methodology.pdf).

### Source

#### Energy Institute – Statistical Review of World Energy
Retrieved on: 2025-06-27  
Retrieved from: https://www.energyinst.org/statistical-review/  


    
# CO₂ emissions per capita - Data package

This data package contains the data that powers the chart ["CO₂ emissions per capita"](https://ourworldindata.org/grapher/co-emissions-per-capita) on the Our World in Data website. It was downloaded on August 07, 2025.

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


## CO₂ emissions per capita
Carbon dioxide (CO₂) emissions from [burning fossil fuels and industrial processes](#dod:fossilemissions). This includes emissions from transport, electricity generation, and heating, but not [land-use change](#dod:land-use-change-emissions).

Last updated: November 21, 2024  
Next update: November 2025  
Date range: 1750–2023  
Unit: tonnes per person  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
Global Carbon Budget (2024); Population based on various sources (2024) – with major processing by Our World in Data

#### Full citation
Global Carbon Budget (2024); Population based on various sources (2024) – with major processing by Our World in Data. “CO₂ emissions per capita” [dataset]. Global Carbon Project, “Global Carbon Budget”; Various sources, “Population” [original data].
Source: Global Carbon Budget (2024), Population based on various sources (2024) – with major processing by Our World In Data

### What you should know about this data
* Carbon dioxide (CO₂) is the primary [greenhouse gas](#dod:ghgemissions) causing climate change.
* Global CO₂ emissions have stayed just below five tonnes per person for over a decade. But across countries, emissions vary widely, rising in some, falling in others.
* Fossil fuel burning is the main source of CO₂ emissions. This data includes [fossil CO₂ emissions](#dod:fossilemissions) from activities such as transport, electricity generation, and heating.
* These figures don't include CO₂ emissions from [changes in land use](#dod:land-use-change-emissions), like deforestation or reforestation.
* Emissions from international aviation and shipping are not included in the data for any individual country or region. They are only counted in the global total.
* This data is based on territorial emissions, meaning the emissions produced within a country's borders, but not those from imported goods. For example, emissions from imported steel are counted in the country where the steel is produced. To learn more and look at emissions adjusted for trade, read our article: [How do CO₂ emissions compare when we adjust for trade?](https://ourworldindata.org/consumption-based-co2)
* The data comes from the Global Carbon Budget. Fossil CO₂ emissions are estimated using national statistics on energy use — such as coal, oil, and gas consumption — and industrial production, particularly cement. These figures are converted into CO₂ emissions using standardized emission factors. For more details, read [the Global Carbon Budget paper](https://doi.org/10.5194/essd-15-5301-2023).
* CO₂ emissions per capita are calculated by dividing emissions by population. They represent the average emissions per person in a country or region. To learn more about how different metrics capture the distribution of CO₂ emissions, read our article: [Per capita, national, historical: how do countries compare on CO2 metrics?](https://ourworldindata.org/co2-emissions-metrics)

### Sources

#### Global Carbon Project – Global Carbon Budget
Retrieved on: 2024-11-21  
Retrieved from: https://globalcarbonbudget.org/  

#### Various sources – Population
Retrieved on: 2024-07-11  
Retrieved from: https://ourworldindata.org/population-sources  

#### Notes on our processing step for this indicator
- Global emissions are converted from tonnes of carbon to tonnes of carbon dioxide (CO₂) using a factor of 3.664. This is the conversion factor [recommended by the Global Carbon Project](https://globalcarbonbudgetdata.org/downloads/jGJH0-data/Global+Carbon+Budget+v2024+Dataset+Descriptions.pdf). It reflects that one tonne of carbon, when fully oxidized, forms 3.664 tonnes of CO₂, based on the relative molecular weights of carbon and oxygen in CO₂.
- Emissions from the 1991 Kuwaiti oil fires are included in Kuwait's emissions for that year.
- To calculate CO₂ emissions per capita, we divide the original data by a country's estimated population. These estimates come from our population dataset based on [multiple sources](https://ourworldindata.org/population-sources).



    
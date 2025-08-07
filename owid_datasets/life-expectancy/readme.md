# Life expectancy - Data package

This data package contains the data that powers the chart ["Life expectancy"](https://ourworldindata.org/grapher/life-expectancy) on the Our World in Data website. It was downloaded on August 07, 2025.

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


## Life expectancy – Long-run data – Riley; Zijdeman et al.; HMD; UN WPP
[Period life expectancy](#dod:period-life-expectancy) is the number of years the average person born in a certain year would live if they experienced the same chances of dying at each age as people did that year.
Last updated: December 3, 2024  
Next update: December 2025  
Date range: 1543–2023  
Unit: years  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
Riley (2005); Zijdeman et al. (2015); HMD (2024); UN WPP (2024) – with major processing by Our World in Data

#### Full citation
Riley (2005); Zijdeman et al. (2015); HMD (2024); UN WPP (2024) – with major processing by Our World in Data. “Life expectancy – Riley; Zijdeman et al.; HMD; UN WPP – Long-run data” [dataset]. Human Mortality Database, “Human Mortality Database”; United Nations, “World Population Prospects”; Zijdeman et al., “Life Expectancy at birth v2”; James C. Riley, “Estimates of Regional and Global Life Expectancy, 1800-2001” [original data].
Source: Riley (2005); Zijdeman et al. (2015); HMD (2024); UN WPP (2024) – with major processing by Our World In Data

### What you should know about this data
* Across the world, people are living longer. In 1900, the global average life expectancy was 32 years. By 2023, this had more than doubled to 73 years.
* Countries around the world made big improvements, and life expectancy more than doubled in every region. This wasn’t just due to falling child mortality; people started living longer at all ages.
* Even after World War II, there have been large drops in life expectancy, such as during the Great Leap Forward famine in China, the HIV/AIDS epidemic in sub-Saharan Africa, the Rwandan genocide, or the COVID-19 pandemic.
* This chart shows long-run estimates of life expectancy compiled by our team from several data sources.
* Period life expectancy is an indicator that summarizes death rates across all age groups in one particular year. It shows how long the average baby born in that year would be expected to live if they experienced the same chances of dying at each age as people did in that year.
* Before 1950, for country-level data, we rely on the [Human Mortality Database (2024)](https://www.mortality.org/Data/ZippedDataFiles) combined with [Zijdeman (2015)](https://clio-infra.eu/Indicators/LifeExpectancyatBirthTotal.html). For regional data, we use [Riley (2005)](https://doi.org/10.1111/j.1728-4457.2005.00083.x). From 1950 onward, we use the [United Nations World Population Prospects (2024)](https://population.un.org/wpp/downloads).
* Detailed information on the source of each data point can be found on [this page](https://docs.google.com/spreadsheets/d/1LnrU1V3p2wq7sAPY4AHRdH1urol3cKev7prEvlLfSU4/edit?gid=0#gid=0).

### Sources

#### Human Mortality Database
Retrieved on: 2024-11-27  
Retrieved from: https://www.mortality.org/Data/ZippedDataFiles  

#### United Nations – World Population Prospects
Retrieved on: 2024-12-02  
Retrieved from: https://population.un.org/wpp/downloads/  

#### Zijdeman et al. – Life Expectancy at birth
Retrieved on: 2023-10-10  
Retrieved from: https://clio-infra.eu/Indicators/LifeExpectancyatBirthTotal.html  

#### James C. Riley – Estimates of Regional and Global Life Expectancy, 1800-2001
Retrieved on: 2023-10-10  
Retrieved from: https://doi.org/10.1111/j.1728-4457.2005.00083.x  

#### Notes on our processing step for this indicator
This chart combines data from several sources. For country-level data before 1950, we use the Human Mortality Database (2024) data and Zijdeman et al. (2015). For country-years where these sources overlap, we use the Human Mortality Database.

For regional data, before 1950, we use Riley's (2005) estimates.

From 1950 onwards, we use the United Nations World Population Prospects (2024) for both country-level and regional data.

Detailed information on the source of each data point can be found on [this page](https://docs.google.com/spreadsheets/d/1LnrU1V3p2wq7sAPY4AHRdH1urol3cKev7prEvlLfSU4/edit?gid=0#gid=0).


    
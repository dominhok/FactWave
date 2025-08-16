# Maternal mortality ratio - Data package

This data package contains the data that powers the chart ["Maternal mortality ratio"](https://ourworldindata.org/grapher/maternal-mortality) on the Our World in Data website.

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


## Maternal mortality ratio
The estimated number of women who die from [maternal conditions](#dod:maternal-mortality) per 100,000 live births, based on data from death certificates, large-scale surveys, and statistical modeling.
Last updated: July 8, 2024  
Next update: September 2025  
Date range: 1751–2020  
Unit: deaths per 100,000 live births  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
UN MMEIG (2023) and other sources – with major processing by Our World in Data

#### Full citation
UN MMEIG (2023); WHO Mortality Database (2025); UN, World Population Prospects (2024); Gapminder (2010) – with major processing by Our World in Data. “Maternal mortality ratio” [dataset]. UN MMEIG (WHO, UNICEF, UNFPA, World Bank Group and UNDESA/ Population Division), “Trends in maternal mortality 2020”; WHO Mortality Database, “WHO Mortality Database”; United Nations, “World Population Prospects”; Gapminder, “Maternal mortality ratio V1” [original data].
Source: UN MMEIG (2023), WHO Mortality Database (2025), UN, World Population Prospects (2024), Gapminder (2010) – with major processing by Our World In Data

### What you should know about this data
* Maternal deaths are defined as a death of a woman while pregnant or within 42 days of termination of pregnancy, irrespective of the duration and site of pregnancy,
from any cause related or aggravated by the pregnancy or its management, but not from accidental or incidental causes.

### Sources

#### UN MMEIG (WHO, UNICEF, UNFPA, World Bank Group and UNDESA/ Population Division) – Trends in maternal mortality
Retrieved on: 2024-07-08  
Retrieved from: https://www.who.int/publications/i/item/9789240068759  

#### WHO Mortality Database
Retrieved on: 2025-04-17  
Retrieved from: https://platform.who.int/mortality  

#### United Nations – World Population Prospects
Retrieved on: 2024-07-11  
Retrieved from: https://population.un.org/wpp/downloads/  

#### Gapminder – Maternal mortality ratio
Retrieved on: 2024-07-08  
Retrieved from: https://www.gapminder.org/data/documentation/gd010/  

#### Notes on our processing step for this indicator
- The dataset combines three sources: WHO Mortality Database (before 1985), Gapminder (before 1985, if WHO Mortality Database data are unavailable), UN MMEIG (1985 onwards).
  The WHO Mortality Database and Gapminder contain reported figures from countries, and are likely to underestimate the true maternal mortality figures. The UN MMEIG aims to estimates the true rate, by adjusting for underreporting and misclassification. Sudden jumps in mortality rate in 1985 are a consequence of switching data sources (from reported to estimated figures).
- For the years between 1950 - 1985 we calculated the maternal mortality ratio and maternal mortality rate based
  on the number of maternal deaths from the WHO mortality database and live births and female population of reproductive age from the UN WPP.
- Where the reported maternal deaths in the WHO Mortality Database differed significantly from the estimated figures in the UN MMEIG data, we opted not to include them.
- Where a data point is attached to a range of years in the Gapminder data set, we used the midpoint of the range.
- The UN MMEIG data shown (post 1985) is the point estimate - this means there is a 50% chance that the true measure lies above this point,
  and a 50% chance that the true value lies below this point.
- We calculated regional aggregates by summing the maternal deaths and live births of all countries in the region and then calculating the MMR based on these figures.


## World regions according to OWID
Last updated: January 1, 2023  
Date range: 2023–2023  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
Our World in Data – processed by Our World in Data

#### Full citation
Our World in Data – processed by Our World in Data. “World regions according to OWID” [dataset]. Our World in Data, “Regions” [original data].
Source: Our World in Data

### Source

#### Our World in Data – Regions


    
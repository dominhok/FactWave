# Weekly confirmed COVID-19 deaths - Data package

This data package contains the data that powers the chart ["Weekly confirmed COVID-19 deaths"](undefined) on the Our World in Data website. It was downloaded on August 07, 2025.

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


## Weekly deaths
Cumulative number of confirmed deaths over the previous week. Due to varying protocols and challenges in the attribution of the cause of death, the number of confirmed deaths may not accurately represent the true number of deaths caused by COVID-19.
Last updated: August 6, 2025  
Next update: September 2025  
Unit: deaths  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
World Health Organization (2025) – processed by Our World in Data

#### Full citation
World Health Organization (2025) – processed by Our World in Data. “Weekly deaths” [dataset]. World Health Organization, “COVID-19 Dashboard WHO COVID-19 Dashboard - Daily cases and deaths” [original data].
Source: World Health Organization (2025) – processed by Our World In Data

### What you should know about this data
* The actual death toll from COVID-19 is likely to be higher than the number of confirmed deaths – this is due to limited testing, [poorly functioning death registries](#dod:crvs), challenges in determining the cause of death, and disruptions during the pandemic. The difference between reported confirmed deaths and actual deaths varies between countries.
* [Excess mortality](https://ourworldindata.org/excess-mortality-covid) is a more comprehensive measure of the total mortality impact of the pandemic, compared to the number of confirmed COVID-19 deaths. This is because it captures not only confirmed deaths, but also COVID-19 deaths that were not accurately diagnosed.
* COVID-19 deaths may be recorded in different ways between countries (e.g., some countries may only count hospital deaths, whilst others also include deaths in homes).
* Data are presented by the date of reporting rather than symptom onset, and retrospective updates by countries can sometimes lead to sudden spikes or even negative values.
* WHO encourages weekly reporting to reduce inconsistencies in daily reporting frequencies across countries and help minimize the risk of misinterpreting periods of zero reporting as zero deaths.
* We provide more detail on these points in [Deaths from COVID-19: background](https://ourworldindata.org/covid-deaths#deaths-from-covid-19-background).

### Source

#### World Health Organization – COVID-19 Dashboard
Retrieved on: 2025-08-06  
Retrieved from: https://covid19.who.int/  


    
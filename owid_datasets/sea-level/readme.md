# Sea level rise - Data package

This data package contains the data that powers the chart ["Sea level rise"](https://ourworldindata.org/grapher/sea-level) on the Our World in Data website.

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


## Global sea level according to Church and White (2011)
Last updated: July 18, 2025  
Next update: September 2025  
Unit: millimeters  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
NOAA Climate.gov (2022) – processed by Our World in Data

#### Full citation
NOAA Climate.gov (2022) – processed by Our World in Data. “Global sea level according to Church and White (2011)” [dataset]. NOAA Climate.gov, “Climate Change: Global Sea Level” [original data].
Source: NOAA Climate.gov (2022) – processed by Our World In Data

### Source

#### NOAA Climate.gov – Climate Change: Global Sea Level
Retrieved on: 2024-01-28  
Retrieved from: https://www.climate.gov/news-features/understanding-climate/climate-change-global-sea-level  


## Global sea level according to UHSLC
Last updated: July 18, 2025  
Next update: September 2025  
Unit: millimeters  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
NOAA Climate.gov (2022) – processed by Our World in Data

#### Full citation
NOAA Climate.gov (2022) – processed by Our World in Data. “Global sea level according to UHSLC” [dataset]. NOAA Climate.gov, “Climate Change: Global Sea Level” [original data].
Source: NOAA Climate.gov (2022) – processed by Our World In Data

### Source

#### NOAA Climate.gov – Climate Change: Global Sea Level
Retrieved on: 2024-01-28  
Retrieved from: https://www.climate.gov/news-features/understanding-climate/climate-change-global-sea-level  


## Global sea level as an average of Church and White (2011) and UHSLC data
Last updated: July 18, 2025  
Next update: September 2025  
Unit: millimeters  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
NOAA Climate.gov (2022) – processed by Our World in Data

#### Full citation
NOAA Climate.gov (2022) – processed by Our World in Data. “Global sea level as an average of Church and White (2011) and UHSLC data” [dataset]. NOAA Climate.gov, “Climate Change: Global Sea Level” [original data].
Source: NOAA Climate.gov (2022) – processed by Our World In Data

### Source

#### NOAA Climate.gov – Climate Change: Global Sea Level
Retrieved on: 2024-01-28  
Retrieved from: https://www.climate.gov/news-features/understanding-climate/climate-change-global-sea-level  


    
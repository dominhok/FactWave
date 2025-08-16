# The Universal Health Coverage (UHC) Service Coverage Index - Data package

This data package contains the data that powers the chart ["The Universal Health Coverage (UHC) Service Coverage Index"](https://ourworldindata.org/grapher/universal-health-coverage-index) on the Our World in Data website. It was downloaded on August 07, 2025.

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


## UHC Service Coverage Index (SDG 3.8.1)
Coverage of essential health services (defined as the average coverage of essential services based on tracer interventions that include reproductive, maternal, newborn and child health, infectious diseases, non-communicable diseases and service capacity and access, among the general and the most disadvantaged population). The indicator is an index reported on a unitless scale of 0 to 100, which is computed as the geometric mean of 14 tracer indicators of health service coverage. The tracer indicators are as follows, organized by four components of service coverage: 1\. Reproductive, maternal, newborn and child health 2\. Infectious diseases 3\. Noncommunicable diseases 4\. Service capacity and access
Last updated: May 19, 2025  
Next update: May 2026  
Date range: 2000–2021  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
World Health Organization - Global Health Observatory (2025) – processed by Our World in Data

#### Full citation
World Health Organization - Global Health Observatory (2025) – processed by Our World in Data. “UHC Service Coverage Index (SDG 3.8.1)” [dataset]. World Health Organization, “Global Health Observatory” [original data].
Source: World Health Organization - Global Health Observatory (2025) – processed by Our World In Data

### How is this data described by its producer - World Health Organization - Global Health Observatory (2025)?
#### Rationale
Target 3.8 is defined as “Achieve universal health coverage, including financial risk protection, access to quality essential health-care services and access to safe, effective, quality and affordable essential medicines and vaccines for all”. The concern is with all people and communities receiving the quality health services they need (including medicines and other health products), without financial hardship. Two indicators have been chosen to monitor target 3.8 within the SDG framework. Indicator 3.8.1 is for health service coverage and indicator 3.8.2 focuses on health expenditures in relation to a household’s budget to identify financial hardship caused by direct health care payments. Taken together, indicators 3.8.1 and 3.8.2 are meant to capture the service coverage and financial protection dimensions, respectively, of target 3.8. These two indicators should be always monitored jointly.

#### Definition
Coverage of essential health services (defined as the average coverage of essential services based on tracer interventions that include reproductive, maternal, newborn and child health, infectious diseases, non-communicable diseases and service capacity and access, among the general and the most disadvantaged population). The indicator is an index reported on a unitless scale of 0 to 100, which is computed as the geometric mean of 14 tracer indicators of health service coverage. The tracer indicators are as follows, organized by four components of service coverage: 1\. Reproductive, maternal, newborn and child health 2\. Infectious diseases 3\. Noncommunicable diseases 4\. Service capacity and access

#### Method of measurement
For each country, the most recent value for each tracer indicators is taken from WHO or other international agencies

#### Method of estimation
The index is computed using geometric means of the tracer indicators.

### Source

#### World Health Organization – Global Health Observatory
Retrieved on: 2025-05-19  
Retrieved from: https://www.who.int/data/gho  


    
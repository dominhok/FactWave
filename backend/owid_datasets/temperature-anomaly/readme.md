# Annual temperature anomalies relative to the pre-industrial period - Data package

This data package contains the data that powers the chart ["Annual temperature anomalies relative to the pre-industrial period"](https://ourworldindata.org/grapher/temperature-anomaly) on the Our World in Data website.

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


## Global average temperature anomaly relative to 1861-1890
The difference in average land-sea surface temperature compared to the 1861-1890 mean, in degrees Celsius.
Last updated: July 18, 2025  
Next update: September 2025  
Date range: 1850–2025  
Unit: degrees Celsius  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
Met Office Hadley Centre - HadCRUT5 (2025) – with major processing by Our World in Data

#### Full citation
Met Office Hadley Centre - HadCRUT5 (2025) – with major processing by Our World in Data. “Global average temperature anomaly relative to 1861-1890” [dataset]. Met Office Hadley Centre, “HadCRUT5 HadCRUT.5.0.2.0” [original data].
Source: Met Office Hadley Centre - HadCRUT5 (2025) – with major processing by Our World In Data

### What you should know about this data
* Temperature anomalies show how many degrees Celsius temperatures have changed compared to the 1861-1890 period. This baseline period is commonly used to highlight the changes in temperature since pre-industrial times, prior to major human impacts.
* Temperature averages and anomalies are calculated over all land and ocean surfaces.
* The data includes separate measurements for the Northern and Southern Hemispheres, which helps researchers analyze regional differences.
* The global temperature anomaly is the average of both hemisphere measurements.
* This data is based on the HadCRUT4 method. This method averages temperature measurements onto a fixed grid. If no data is available for a grid cell, it remains empty and adds extra uncertainty when calculating averages like the global mean.
* Despite different approaches, HadCRUT4 and other methods show similar global temperature trends.

### How is this data described by its producer - Met Office Hadley Centre - HadCRUT5 (2025)?
The 1961-90 period is most often used as a baseline because it is the period recommended by the World Meteorological Organisation. In some cases other periods are used. For global average temperatures, an 1861-1890 period is sometimes used to show the warming since the "pre-industrial" period.

### Source

#### Met Office Hadley Centre – HadCRUT5
Retrieved on: 2025-07-18  
Retrieved from: https://www.metoffice.gov.uk/hadobs/hadcrut5/  


## Lower bound of the annual temperature anomaly (95% confidence interval)
Last updated: July 18, 2025  
Next update: September 2025  
Date range: 1850–2025  
Unit: degrees Celsius  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
Met Office Hadley Centre - HadCRUT5 (2025) – with major processing by Our World in Data

#### Full citation
Met Office Hadley Centre - HadCRUT5 (2025) – with major processing by Our World in Data. “Lower bound of the annual temperature anomaly (95% confidence interval)” [dataset]. Met Office Hadley Centre, “HadCRUT5 HadCRUT.5.0.2.0” [original data].
Source: Met Office Hadley Centre - HadCRUT5 (2025) – with major processing by Our World In Data

### What you should know about this data
* Temperature anomalies show how many degrees Celsius temperatures have changed compared to the 1861-1890 period. This baseline period is commonly used to highlight the changes in temperature since pre-industrial times, prior to major human impacts.
* Temperature averages and anomalies are calculated over all land and ocean surfaces.
* The data includes separate measurements for the Northern and Southern Hemispheres, which helps researchers analyze regional differences.
* The global temperature anomaly is the average of both hemisphere measurements.
* This data is based on the HadCRUT4 method. This method averages temperature measurements onto a fixed grid. If no data is available for a grid cell, it remains empty and adds extra uncertainty when calculating averages like the global mean.
* Despite different approaches, HadCRUT4 and other methods show similar global temperature trends.

### How is this data described by its producer - Met Office Hadley Centre - HadCRUT5 (2025)?
The 1961-90 period is most often used as a baseline because it is the period recommended by the World Meteorological Organisation. In some cases other periods are used. For global average temperatures, an 1861-1890 period is sometimes used to show the warming since the "pre-industrial" period.

### Source

#### Met Office Hadley Centre – HadCRUT5
Retrieved on: 2025-07-18  
Retrieved from: https://www.metoffice.gov.uk/hadobs/hadcrut5/  


## Upper bound of the annual temperature anomaly (95% confidence interval)
Last updated: July 18, 2025  
Next update: September 2025  
Date range: 1850–2025  
Unit: degrees Celsius  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
Met Office Hadley Centre - HadCRUT5 (2025) – with major processing by Our World in Data

#### Full citation
Met Office Hadley Centre - HadCRUT5 (2025) – with major processing by Our World in Data. “Upper bound of the annual temperature anomaly (95% confidence interval)” [dataset]. Met Office Hadley Centre, “HadCRUT5 HadCRUT.5.0.2.0” [original data].
Source: Met Office Hadley Centre - HadCRUT5 (2025) – with major processing by Our World In Data

### What you should know about this data
* Temperature anomalies show how many degrees Celsius temperatures have changed compared to the 1861-1890 period. This baseline period is commonly used to highlight the changes in temperature since pre-industrial times, prior to major human impacts.
* Temperature averages and anomalies are calculated over all land and ocean surfaces.
* The data includes separate measurements for the Northern and Southern Hemispheres, which helps researchers analyze regional differences.
* The global temperature anomaly is the average of both hemisphere measurements.
* This data is based on the HadCRUT4 method. This method averages temperature measurements onto a fixed grid. If no data is available for a grid cell, it remains empty and adds extra uncertainty when calculating averages like the global mean.
* Despite different approaches, HadCRUT4 and other methods show similar global temperature trends.

### How is this data described by its producer - Met Office Hadley Centre - HadCRUT5 (2025)?
The 1961-90 period is most often used as a baseline because it is the period recommended by the World Meteorological Organisation. In some cases other periods are used. For global average temperatures, an 1861-1890 period is sometimes used to show the warming since the "pre-industrial" period.

### Source

#### Met Office Hadley Centre – HadCRUT5
Retrieved on: 2025-07-18  
Retrieved from: https://www.metoffice.gov.uk/hadobs/hadcrut5/  


    
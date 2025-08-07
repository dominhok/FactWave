# Exposure to particulate matter air pollution - Data package

This data package contains the data that powers the chart ["Exposure to particulate matter air pollution"](https://ourworldindata.org/grapher/pm25-air-pollution) on the Our World in Data website. It was downloaded on August 07, 2025.

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


## Concentrations of fine particulate matter (PM2.5) - Residence area type: Total
The mean annual concentration of fine suspended particles of less than 2.5 microns in diameters is a common measure of air pollution. The mean is a population-weighted average for urban population in a country.
Last updated: May 19, 2025  
Next update: May 2026  
Date range: 2010–2019  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
World Health Organization - Global Health Observatory (2025) – processed by Our World in Data

#### Full citation
World Health Organization - Global Health Observatory (2025) – processed by Our World in Data. “Concentrations of fine particulate matter (PM2.5) - Residence area type: Total” [dataset]. World Health Organization, “Global Health Observatory” [original data].
Source: World Health Organization - Global Health Observatory (2025) – processed by Our World In Data

### How is this data described by its producer - World Health Organization - Global Health Observatory (2025)?
#### Rationale
Air pollution consists of many pollutants, among other particulate matter. These particles are able to penetrate deeply into the respiratory tract and therefore constitute a risk for health by increasing mortality from respiratory infections and diseases, lung cancer, and selected cardiovascular diseases.

#### Definition
The mean annual concentration of fine suspended particles of less than 2.5 microns in diameters is a common measure of air pollution. The mean is a population-weighted average for urban population in a country.

#### Method of measurement
Concentration of PM2.5 are regularly measured from fixed-site, population-oriented monitors located within the metropolitan areas. High-quality measurements of PM concentration from all the monitors in the metropolitan area can be averaged to develop a single estimate.

#### Method of estimation
Although PM is measured at many thousands of locations throughout the world, the amount of monitors in different geographical areas vary, with some areas having little or no monitoring. In order to produce global estimates at high resolution (0.1◦ grid‐cells), additional data is required. Annual urban mean concentration of PM2.5 is estimated with improved modelling using data integration from satellite remote sensing, population estimates, topography and ground measurements.

### Source

#### World Health Organization – Global Health Observatory
Retrieved on: 2025-05-19  
Retrieved from: https://www.who.int/data/gho  


    
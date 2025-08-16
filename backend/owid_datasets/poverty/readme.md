# Share of population living in extreme poverty - Data package

This data package contains the data that powers the chart ["Share of population living in extreme poverty"](https://ourworldindata.org/grapher/share-of-population-in-extreme-poverty) on the Our World in Data website.

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


## Share of population in poverty ($3 a day)
Percentage of population living in households with an income or consumption below $3 per day.
Last updated: June 5, 2025  
Next update: December 2025  
Date range: 1963–2025  
Unit: %  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
World Bank Poverty and Inequality Platform (2025) – with major processing by Our World in Data

#### Full citation
World Bank Poverty and Inequality Platform (2025) – with major processing by Our World in Data. “Share of population in poverty ($3 a day) – World Bank” [dataset]. World Bank Poverty and Inequality Platform, “World Bank Poverty and Inequality Platform (PIP) 20250401_2021, 20250401_2017” [original data].
Source: World Bank Poverty and Inequality Platform (2025) – with major processing by Our World In Data

### What you should know about this data
* Extreme poverty here is defined as living below the International Poverty Line of $3 per day.
* The data is measured in international-$ at 2021 prices – this adjusts for inflation and for differences in living costs between countries.
* Depending on the country and year, the data relates to income (measured after taxes and benefits) or to consumption, per capita. _Per capita_ means that the income of each household is attributed equally to each member of the household (including children).
* Non-market sources of income, including food grown by subsistence farmers for their own consumption, are taken into account.
* Regional and global estimates are extrapolated up until the year of the data release using GDP growth estimates and forecasts. For more details about the methodology, please refer to the [World Bank PIP documentation](https://datanalytics.worldbank.org/PIP-Methodology/lineupestimates.html#nowcasts).

### How is this data described by its producer - World Bank Poverty and Inequality Platform (2025)?
% of population living in households with consumption or income per person below the poverty line at 2021 international prices. As a result of revisions in PPP exchange rates, poverty rates for individual countries cannot be compared with poverty rates reported in earlier editions.

### Source

#### World Bank Poverty and Inequality Platform – World Bank Poverty and Inequality Platform (PIP)
Retrieved on: 2025-06-05  
Retrieved from: https://pip.worldbank.org  

#### Notes on our processing step for this indicator
For most countries in the PIP dataset, estimates relate to _either_ disposable income or consumption, for all available years. A number of countries, however, have a mix of income and consumption data points, with both data types sometimes available for particular years.

In most of our charts, we present the data with some data points dropped in order to present single series for each country. This allows us to make readable visualizations that combine multiple countries and metrics. In choosing which data points to drop, we try to strike a balance between maintaining comparability over time and showing as long a time series as possible. As such, the exact approach varies somewhat across countries.

If you would like to see the original data with _all_ available income and consumption data points shown separately, you can do so in our [Poverty Data Explorer](https://ourworldindata.org/explorers/poverty-explorer?Indicator=Share+in+poverty&Poverty+line=%2410+per+day&Household+survey+data+type=Show+data+from+both+income+and+consumption+surveys&Show+breaks+between+less+comparable+surveys=true&country=ROU~CHN~BLR~PER).


    
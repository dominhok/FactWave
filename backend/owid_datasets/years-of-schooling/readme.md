# Average years of schooling - Data package

This data package contains the data that powers the chart ["Average years of schooling"](https://ourworldindata.org/grapher/mean-years-of-schooling-long-run) on the Our World in Data website. It was downloaded on August 07, 2025.

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


## Average years of schooling
Average years of formal education for individuals aged 15-64.
Last updated: July 17, 2023  
Date range: 1870–2040  
Unit: years  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
Barro and Lee (2015); Lee and Lee (2016) – with major processing by Our World in Data

#### Full citation
Barro and Lee (2015); Lee and Lee (2016) – with major processing by Our World in Data. “Average years of schooling” [dataset]. Barro and Lee, “Projections of Educational Attainment”; Lee and Lee, “Human Capital in the Long Run” [original data].
Source: Barro and Lee (2015), Lee and Lee (2016) – with major processing by Our World In Data

### What you should know about this data
* For the years leading up to 2015, the data are derived from historical estimates, providing a retrospective view of education levels. For the years 2015 and beyond, the projections are grounded in the historical data of 2010, which serve as the foundational benchmark. These forward-looking projections are then crafted by analyzing trends in school enrollment and changes in population structures. These trends are informed by forecasts from the United Nations, ensuring a global perspective and understanding of future educational developments.
* The method to estimate average years of schooling takes into account the age distribution in the population. This is important because access to education can vary significantly across generations. Older generations may have had fewer educational opportunities than younger ones, which affects the overall average education level.
* It also considers the typical duration required to complete each education level. For instance, primary education usually takes about 6 years, secondary education 4-6 years, and higher education may take even longer. Understanding the time investment required for different education levels is essential for accurate assessment.
* At its core, the method calculates the average years of schooling. This is achieved by determining the percentage of the population that has completed each education level and multiplying it by the duration of that level. The sum of these results gives a comprehensive view of both the extent of educational attainment and the time spent in education by the population.
* The method is dynamic, adapting to changes over time and across regions. For example, if a country increases the length of primary education, this change is included in subsequent calculations. This adaptability ensures that the average years of education remain relevant and accurate over time and across different educational systems.
* Note that the method does not take into account the quality of education. It only considers the number of years spent in education. This means that the average years of schooling may not reflect the actual skills and knowledge of the population.

### Sources

#### Barro and Lee – Projections of Educational Attainment
Retrieved on: 2023-11-20  
Retrieved from: http://www.barrolee.com/  

#### Lee and Lee – Human Capital in the Long Run
Retrieved on: 2023-11-20  
Retrieved from: https://barrolee.github.io/BarroLeeDataSet/DataLeeLee.html  

#### Notes on our processing step for this indicator
Historical data up to the year 2010 has been sourced from 'Human Capital in the Long Run' by Lee and Lee (2016). This historical data was then combined with recent projections provided by Barro ane Lee (2015).

Regional aggregates were computed by Our World in Data through yearly population-weighted averages, where annual values are proportionally adjusted to emphasize the influence of larger populations.



    
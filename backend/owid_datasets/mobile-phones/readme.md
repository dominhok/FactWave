# Mobile phone subscriptions per 100 people - Data package

This data package contains the data that powers the chart ["Mobile phone subscriptions per 100 people"](https://ourworldindata.org/grapher/mobile-cellular-subscriptions-per-100-people) on the Our World in Data website. It was downloaded on August 07, 2025.

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


## Mobile cellular subscriptions (per 100 people)
Last updated: January 24, 2025  
Next update: January 2026  
Date range: 1960–2023  
Unit: per 100 people  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
International Telecommunication Union (ITU), via World Bank (2025) – processed by Our World in Data

#### Full citation
International Telecommunication Union (ITU), via World Bank (2025) – processed by Our World in Data. “Mobile cellular subscriptions (per 100 people)” [dataset]. International Telecommunication Union (ITU), via World Bank, “World Development Indicators” [original data].
Source: International Telecommunication Union (ITU), via World Bank (2025) – processed by Our World In Data

### How is this data described by its producer - International Telecommunication Union (ITU), via World Bank (2025)?
Mobile cellular telephone subscriptions are subscriptions to a public mobile telephone service that provide access to the PSTN using cellular technology. The indicator includes (and is split into) the number of postpaid subscriptions, and the number of active prepaid accounts (i.e. that have been used during the last three months). The indicator applies to all mobile cellular subscriptions that offer voice communications. It excludes subscriptions via data cards or USB modems, subscriptions to public mobile data services, private trunked mobile radio, telepoint, radio paging and telemetry services.

### Limitations and exceptions:
Operators have traditionally been the main source of telecommunications data, so information on subscriptions has been widely available for most countries. This gives a general idea of access, but a more precise measure is the penetration rate - the share of households with access to telecommunications. During the past few years more information on information and communication technology use has become available from household and business surveys. Also important are data on actual use of telecommunications services. Ideally, statistics on telecommunications (and other information and communications technologies) should be compiled for all three measures: subscriptions, access, and use. The quality of data varies among reporting countries as a result of differences in regulations covering data provision and availability.

Discrepancies between global and national figures may arise when countries use a different definition than the one used by ITU. For example, some countries do not include the number of ISDN channels when calculating the number of fixed telephone lines. Discrepancies may also arise in cases where the end of a fiscal year differs from that used by ITU, which is the end of December of every year. A number of countries have fiscal years that end in March or June of every year. Data are usually not adjusted but discrepancies in the definition, reference year or the break in comparability in between years are noted in a data note. For this reason, data are not always strictly comparable. Missing values are estimated by ITU.

Mobile subscriptions include both analogue and digital cellular systems (IMT-2000 (Third Generation, 3G) and 4G subscriptions, but excludes mobile broadband subscriptions via data cards or USB modems. Subscriptions to public mobile data services, private trunked mobile radio, telepoint or radio paging, and telemetry services are also excluded, but all mobile cellular subscriptions that offer voice communications are included. Both postpaid and prepaid subscriptions are included.

### Statistical concept and methodology:
Refers to the subscriptions to a public mobile telephone service and provides access to Public Switched Telephone Network (PSTN) using cellular technology, including number of pre-paid SIM cards active during the past three months. This includes both analogue and digital cellular systems (IMT-2000 (Third Generation, 3G) and 4G subscriptions, but excludes mobile broadband subscriptions via data cards or USB modems. Subscriptions to public mobile data services, private trunked mobile radio, telepoint or radio paging, and telemetry services should also be excluded. This should include all mobile cellular subscriptions that offer voice communications.

Data on mobile cellular subscribers are derived using administrative data that countries (usually the regulatory telecommunication authority or the Ministry in charge of telecommunications) regularly, and at least annually, collect from telecommunications operators.

Data for this indicator are readily available for approximately 90 percent of countries, either through ITU's World Telecommunication Indicators questionnaires or from official information available on the Ministry or Regulator's website. For the rest, information can be aggregated through operators' data (mainly through annual reports) and complemented by market research reports.

Mobile cellular subscriptions (per 100 people) indicator is derived by all mobile subscriptions divided by the country's population and multiplied by 100. For additional/latest information on sources and country notes, please also refer to: https://www.itu.int/en/ITU-D/Statistics/Pages/stat/default.aspx

### Source

#### International Telecommunication Union (ITU), via World Bank – World Development Indicators
Retrieved on: 2025-01-24  
Retrieved from: https://data.worldbank.org/indicator/IT.CEL.SETS.P2  


    
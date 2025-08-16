# Share of land covered by forest - Data package

This data package contains the data that powers the chart ["Share of land covered by forest"](https://ourworldindata.org/grapher/forest-area-as-share-of-land-area) on the Our World in Data website.

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


## Share of land covered by forest
The share of land area covered by forest, including both natural forests and forest plantations.
Last updated: May 9, 2025  
Next update: May 2026  
Date range: 1000–2020  
Unit: %  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
Department for Environment, Food & Rural Affairs (2013) and other sources – with major processing by Our World in Data

#### Full citation
Department for Environment, Food & Rural Affairs (2013); Food and Agriculture Organization of the United Nations Regional Office for Asia and the Pacific (2009); Forest Research (2002); Mather A.S., Fairbairn J., and Needle C.J. (1999); Osamu Saito (2009); Yi-Ying Chen et al. (2019); A.S. Mather (2008); Kleinn, C., Corrales, L., & Morales, D. (2002); Soo Bae J., Won Joo, R. and Kim, Y.S. (2012); United States Department of Agriculture, Forest Service (2014); He, F., Yang, F, & Wang, Y. (2024); Scottish Government (2019); Food and Agriculture Organization of the United Nations (2024) – with major processing by Our World in Data. “Share of land covered by forest” [dataset]. Department for Environment, Food & Rural Affairs, “DEFRA - Government Forestry and Woodlands Policy Statement”; Food and Agriculture Organization of the United Nations Regional Office for Asia and the Pacific, “Vietnam Forestry Outlook Study”; Forest Research, “National inventory of woodland and trees”; Mather A.S., Fairbairn J., and Needle C.J., “The course and drivers of the forest transition: The case of France”; Osamu Saito, “Forest history and the Great Divergence: China, Japan, and the West compared”; Yi-Ying Chen et al., “Reconstructing Taiwan’s land cover changes between 1904 and 2015 from historical maps and satellite images”; A.S. Mather, “Forest transition theory and the reforesting of Scotland”; Kleinn, C., Corrales, L., & Morales, D., “Forest area in Costa Rica: A comparative study of tropical forest cover estimates over time”; Soo Bae J., Won Joo, R. and Kim, Y.S., “Forest transition in South Korea: Reality, path and drivers”; United States Department of Agriculture, Forest Service, “U.S. Forest Resource Facts and Historical Trends”; He, F., Yang, F, & Wang, Y., “Reconstructing forest and grassland cover changes in China over the past millennium”; Scottish Government, “Scotland's Forestry Strategy: 2019-2029”; Food and Agriculture Organization of the United Nations, “Land, Inputs and Sustainability: Land Use” [original data].
Source: Department for Environment, Food & Rural Affairs (2013), Food and Agriculture Organization of the United Nations Regional Office for Asia and the Pacific (2009), Forest Research (2002), Mather A.S., Fairbairn J., and Needle C.J. (1999), Osamu Saito (2009), Yi-Ying Chen et al. (2019), A.S. Mather (2008), Kleinn, C., Corrales, L., & Morales, D. (2002), Soo Bae J., Won Joo, R. and Kim, Y.S. (2012), United States Department of Agriculture, Forest Service (2014), He, F., Yang, F, & Wang, Y. (2024), Scottish Government (2019), Food and Agriculture Organization of the United Nations (2024) – with major processing by Our World In Data

### What you should know about this data
* This indicator shows the share of a country’s land area that is covered by forest. It includes both natural forests and forest plantations, where that distinction is available.
* For 1990 onwards, data comes from the Food and Agriculture Organization (FAO), which uses a consistent global definition: forest is land with tree canopy cover greater than 10%, spanning more than 0.5 hectares, with trees that can reach at least 5 metres in height. It includes plantations but excludes land where other uses (such as agriculture or urban development) dominate ([FAO definition](https://www.fao.org/4/y1997e/y1997e1m.htm)).
* We linearly interpolate the data for the years between the FAO FRA data points, which are typically given every 5 years.
* For years prior to 1990, the data is drawn from historical estimates published by sources including the USDA Forest Service, DEFRA, Forest Research, and others. These estimates typically rely on older maps, land surveys, and expert reconstructions.
* Where possible, pre-1990 estimates include both natural forests and plantations to match the FAO’s definition. However, definitions and methods vary by source and country, and users should interpret older data points with some caution.
* The details for the historical estimates are provided below:
- China (1000-1960): [He et al. (2025): Reconstructing forest and grassland cover changes in China over the past millennium](https://link.springer.com/article/10.1007/s11430-024-1454-4)
- Costa Rica (1940-1969): [Kleinn et al. (2002): Forest area in Costa Rica: A comparative study of tropical forest cover estimates over time](https://link.springer.com/article/10.1023/A:1012659129083)
- England (1086-1650): [Department for Environment, Food and Rural Affairs (DEFRA) report: Government Forestry and Woodlands Policy Statement](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/221023/pb13871-forestry-policy-statement.pdf)
- England (1870-1980): [Forest Research report: National inventory of woodland and trees](https://www.forestresearch.gov.uk/tools-and-resources/national-forest-inventory/national-inventory-of-woodland-and-trees/national-inventory-of-woodland-and-trees-england/)
- England (2019): [Scottish Government report: Scotland's Forestry Strategy: 2019-2029](https://www.gov.scot/binaries/content/documents/govscot/publications/strategy-plan/2019/02/scotlands-forestry-strategy-20192029/documents/scotlands-forestry-strategy-2019-2029/scotlands-forestry-strategy-2019-2029/govscot%3Adocument/scotlands-forestry-strategy-2019-2029.pdf)
- France (1000-1976): [Mather et al. (1999): The course and drivers of the forest transition in France](https://www.sciencedirect.com/science/article/abs/pii/S0743016798000230)
- Japan (1600-1985): [Saito, O. (2009): Forest history and the Great Divergence: China, Japan, and the West compared](https://www.cambridge.org/core/journals/journal-of-global-history/article/abs/forest-history-and-the-great-divergence-china-japan-and-the-west-compared/6140D78077980694B07B40B6396C0343)
- Philippines (1934-1988): [Center for International Forestry Research (CIFOR) report: One century of forest rehabilitation in the Philippines](https://www.cifor.org/publications/pdf_files/Books/Bchokkalingam0605.pdf&sa=D&source=editors&ust=1747056384183598&usg=AOvVaw1Hqe87fsPmuVQLF1K6hWYO)
- Scotland (1600-1750): [Mather, A.S. (2008)](https://www.tandfonline.com/doi/pdf/10.1080/00369220418737194)
- Scotland (1870-1988): [Forest Research report: National inventory of woodland and trees](https://www.forestresearch.gov.uk/tools-and-resources/national-forest-inventory/national-inventory-of-woodland-and-trees/national-inventory-of-woodland-and-trees-scotland/)
- Scotland (2019): [Scottish Government report: Scotland's Forestry Strategy: 2019-2029](https://www.gov.scot/binaries/content/documents/govscot/publications/strategy-plan/2019/02/scotlands-forestry-strategy-20192029/documents/scotlands-forestry-strategy-2019-2029/scotlands-forestry-strategy-2019-2029/govscot%3Adocument/scotlands-forestry-strategy-2019-2029.pdf)
- South Korea (1948-1980): [Bae J.S. et al. (2012) Forest transition in South Korea: Reality, path and drivers](https://www.sciencedirect.com/science/article/pii/S0264837711000615)
- Taiwan (1904-1982): [Chen Y et al (2019) Reconstructing Taiwan’s land cover changes between 1904 and 2015 from historical maps and satellite images](https://pmc.ncbi.nlm.nih.gov/articles/PMC6403323/)
- United States (1630-1907): [U.S. Department of Agriculture Forest Service (USDA FS) report: U.S. Forest Facts and Historical Trends](https://web.archive.org/web/20220728061823/https://www.fia.fs.fed.us/library/brochures/docs/2000/ForestFactsMetric.pdf)
- United States (1920-1987): [U.S. Department of Agriculture Forest Service (USDA FS) report (2014): U.S. Forest Resource Facts and Historical Trends](https://www.fs.usda.gov/sites/default/files/legacy_files/media/types/publication/field_pdf/forestfacts-2014aug-fs1035-508complete.pdf)
- Vietnam (1943-1985): [Forest Science Institute of Vietnam (FSIV) and Food and Agriculture Organization of the United Nations (FAO) report: Vietnam Forestry Outlook Study](https://web.archive.org/web/20230715025310/http://www.fao.org/3/am254e/am254e00.pdf)

### Sources

#### Department for Environment, Food & Rural Affairs – DEFRA - Government Forestry and Woodlands Policy Statement
Retrieved on: 2025-05-06  
Retrieved from: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/221023/pb13871-forestry-policy-statement.pdf  

#### Food and Agriculture Organization of the United Nations Regional Office for Asia and the Pacific – Vietnam Forestry Outlook Study
Retrieved on: 2025-05-06  
Retrieved from: https://web.archive.org/web/20230715025310/http://www.fao.org/3/am254e/am254e00.pdf  

#### Forest Research – National inventory of woodland and trees
Retrieved on: 2025-05-06  
Retrieved from: https://www.forestresearch.gov.uk/tools-and-resources/national-forest-inventory/national-inventory-of-woodland-and-trees/  

#### Mather A.S., Fairbairn J., and Needle C.J. – The course and drivers of the forest transition: The case of France
Retrieved on: 2025-05-07  
Retrieved from: https://www.sciencedirect.com/science/article/abs/pii/S0743016798000230  

#### Osamu Saito – Forest history and the Great Divergence: China, Japan, and the West compared
Retrieved on: 2025-05-07  
Retrieved from: https://www.cambridge.org/core/journals/journal-of-global-history/article/abs/forest-history-and-the-great-divergence-china-japan-and-the-west-compared/6140D78077980694B07B40B6396C0343  

#### Yi-Ying Chen et al. – Reconstructing Taiwan’s land cover changes between 1904 and 2015 from historical maps and satellite images
Retrieved on: 2025-05-07  
Retrieved from: https://www.nature.com/articles/s41598-019-40063-1  

#### A.S. Mather – Forest transition theory and the reforesting of Scotland
Retrieved on: 2025-05-08  
Retrieved from: https://www.tandfonline.com/doi/abs/10.1080/00369220418737194  

#### Kleinn, C., Corrales, L., & Morales, D. – Forest area in Costa Rica: A comparative study of tropical forest cover estimates over time
Retrieved on: 2025-05-08  
Retrieved from: https://link.springer.com/article/10.1023/A:1012659129083  

#### Soo Bae J., Won Joo, R. and Kim, Y.S. – Forest transition in South Korea: Reality, path and drivers
Retrieved on: 2025-05-08  
Retrieved from: https://www.sciencedirect.com/science/article/abs/pii/S0264837711000615  

#### United States Department of Agriculture, Forest Service – U.S. Forest Resource Facts and Historical Trends
Retrieved on: 2025-05-07  
Retrieved from: https://www.fs.usda.gov/sites/default/files/legacy_files/media/types/publication/field_pdf/forestfacts-2014aug-fs1035-508complete.pdf  

#### He, F., Yang, F, & Wang, Y. – Reconstructing forest and grassland cover changes in China over the past millennium
Retrieved on: 2025-05-16  
Retrieved from: https://link.springer.com/article/10.1007/s11430-024-1454-4  

#### Scottish Government – Scotland's Forestry Strategy: 2019-2029
Retrieved on: 2025-05-30  
Retrieved from: https://www.gov.scot/binaries/content/documents/govscot/publications/strategy-plan/2019/02/scotlands-forestry-strategy-20192029/documents/scotlands-forestry-strategy-2019-2029/scotlands-forestry-strategy-2019-2029/govscot%3Adocument/scotlands-forestry-strategy-2019-2029.pdf  

#### Food and Agriculture Organization of the United Nations – Land, Inputs and Sustainability: Land Use
Retrieved on: 2025-03-17  
Retrieved from: http://www.fao.org/faostat/en/#data/RL  

#### Notes on our processing step for this indicator
This variable is a combination of historical sources of forest cover data from various organizations, including FAO, USDA Forest Service, DEFRA, Forest Research and others; and more recent data from the FAO Global Forest Resources Assessment (FRA) data and the total land area variable from the FAO Land Use data. FAO FRA data is used for the 1990 onwards, while historical data is sourced from various papers and reports.


    
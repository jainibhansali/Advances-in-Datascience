# Team5assignment1
## TeamMembers:
  1. Tushar Goel
  2. Jaini Bhansali

## Problem 1:
To extract tables from 10Q filings using r or Python. Given a accession number and CIK programattically generate the URL and extract data from the 10Q file. Dockerize images and  zip the file and upload to Amazon S3
## Problem 2: 
Missing Data Analysis. Handle edgar log data with missing data,compute summary metrics,check observable anomalies ,logging operations
## Abstract
Part 1 :Our approach to address Part 1 involved scraping the Edgar Data Website when Accession Number and CIK as input arguments for part 1. The form is parsed for the 10Q filing using Python Libraries and data is input into a data frame. We then implemented data cleansing which included extracting only tables with the data. Followed by aligning the columns, removing ‘$’ signs which occupied individual columns, removing NaN, None and any occurrences of blank columns and after removing the Nan and None values realigned the columns by looping through the data frame.
Part 2 : Log files were extracted and analysed for missing data. Anomalies were identified. Optimum techniques were implemented to handle missing data for categorical and Numerical fields. Summarization metrics were identified. Analysis was plotted on pyplots for enhanced understanding. Checked data to identify outliers. Missing data in  log data has also been handled. If data is not found for 1 particluar day , programattically looks for the next available day with data. If the month does not have data it provodes a message 'No data available'
### US-east-1 does not work as an s3 location due to API contraints
### Contents
The folder team5Assignment1 consists of Part1ofPart1, Part2ofPart1 which addresses Problem 1. Part 2 addresses Problem 2 of the assignment.
### Exception Handling and Logging
1.	We passed Accession Key, CIK, Amazon s3 keys , S3 location, year as arguments by the user
2.	Handled scenarios when CIK and Accession Key are blank or incorrect.Appropriate errors are provided in these cases
3.  Logging is done using logging.info(). and logging.warning()
4. Logging has been done during url creation, in case of exceptions,when data is missing and incase of invlid or incomplete aws keys
5.	We have accomadated logging. Logging details can be found in the file name ‘Part2.log’
6.	Logging occurs at different instances.
### INFO
1.	Language used : Python
2.	Process Followed : Data Ingestion, Data Wrangling, Data Cleansing, Exploratory Data Analysis
3.	Tools used :  Jupyter Notebook, boto 3, boto, Amazon S3 bucket

### For further Details please refer the Assignment1_Documentation.pdf file



# Australian-Suburb-Housing-Price-Predictor
Application that is designed to scrape the data for a particular suburb and use that data to train and validate a machine learning model that'll provide price predictions given a subset of information.


## Workflow(Local)
1. Take postcode as input
2. Scrape data from Domain.com.au
3. Clean data
4. Transform data as necessary
5. Split data into training data/validation data
6. Train multiple machine learning models and validate which model is the best
7. Host model locally for inference
8. Invoke model locally

## Workflow(Cloud)
1. Do all data preprocessing & cleaning locally
2. Upload preprocessed data to S3
3. Run SageMaker Pipeline
 - Splits data into training data and validation data
 - SageMaker Pipeline creates multiple SageMaker Training Jobs
 - Validates which model is the best using validation data
4. Adds model to model package
5. Host model to SM Endpoint
6. Invoke SM Endpoint

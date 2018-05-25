# Assignment 2

#### The Detailed Problem statement can be found in the Assignment2.pdf 

## Part1
  1. Write a Luigi Pipeline to scrape data and do Feature Engineering
  In the Directory Part1, the files declined.py and loandata.py when run using the below commands will start the luigi pipelines for     accepted loan data and declined loan data.
  ##Note: Make Sure you have an active internet connection

  #### Command to run the LUIGI pipeline for Accepted Loan Data 
  python loandata.py --local-scheduler FeatureEngineering

  #### Command to run the LUIGI pipeline for Declined Loan Data
  python declined.py --local-scheduler DeclinedFeatureEngineering
  
  For the Feature Selection we have computed various metrics that can be found in the FeatureSelection.csv
  More information on that can be found in the documentation
  
  2. Compute Summary metrics for the Loan Data
  In the Folder Part1 the filename SummaryMetricsAssignment2.ipynb has all the summary metrics along with the desription of what they signify
  
## Part2 
  #### Note: All the sample code for running individual REST API's is present in directory Part2/RestAPI/
  
  1. Create a classification model,compute best  and deploy it on azure
    The Classification model code for jupyter is in the Part2 folder in Classification.ipynb
    The best accuracy was given by Randomforestclassfier which was 100%
    All the metrics are described in the documentation
  
  2. Create 3 Clusterin models one with manual clustering, algorithm clustering, no clustering
      For manual clustering in the Part2 Folder you will find the file Part2_ManualClustering.ipynb which divides the data into cluster
      For algorithm clustering in the Part2 Folder you will find the file Part2_ClusteringAlgorithm_1.ipynb which divides the data into cluster
  3. Deploy predicition models for all the clusters made in the previous part and calculate the MAE,RMSE,MAPE and deploy best models on azure
    We deployed 9 prediction models on Azure for every cluster made initial evaluation of models on jupyter can be found in the Part2 Folder. The names of the IPYNB Files are self descriptive 
    For Each REST API you will find sample test code in the restapi folder in the Part2 Folder 
    The names of each model REST API is self descriptive
    
  4. Deploy the models
    In Folder Part2 we have a script DeploymentScript_assignment2.ipynb which creates the whole pipeline
    first it decides whether to give a loan or not
#### Note: In the question we were not told to deploy the clustering model so there is a kmeancluster.pkl that you need to download from the Part2 folder to run the deployment script
    if given it assigns it to a cluster and runs it on 3 different prediction algorithms and gives the highest interest rate
    
# Results: 100% Accuracy for Classification, 0.02 MAE for Prediction of interest rates
All the other results are present in the csv file Algorithmresults.csv

    
    
    

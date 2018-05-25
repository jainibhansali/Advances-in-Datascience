import pandas as pd
from pandas import DataFrame,read_csv
import numpy as np
from sklearn.utils import check_array
from sklearn import neighbors
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
import boto3


prop2017=pd.read_csv("properties_2017.csv")
train2017=pd.read_csv("train_2017.csv",parse_dates=['transactiondate'])
prop2016=pd.read_csv("properties_2016.csv")
train2016=pd.read_csv("train_2016_v2.csv",parse_dates=['transactiondate'])
merged_17=train2017.merge(prop2017,on='parcelid',how='inner')
merged_16=train2016.merge(prop2016,on='parcelid',how='inner')
merged_16['year']=2016
merged_17['year']=2017
frames=[merged_17,merged_16]
finmerged=pd.concat(frames)
finmerged.reset_index(inplace=True)
finmerged.drop('index',axis=1,inplace=True)
finmerged['taxdelinquencyflag'].replace("Y",1,inplace=True)
finmerged['hashottuborspa'].replace(True,1,inplace=True)
finmerged['fireplaceflag'].replace(True,1,inplace=True)
finmerged.drop('buildingclasstypeid',axis=1,inplace=True)
def hr_func(ts):
    return ts.month
finmerged['time_month'] = finmerged['transactiondate'].apply(hr_func)
finmerged.drop('architecturalstyletypeid',axis=1,inplace=True)
finmerged.drop('basementsqft',axis=1,inplace=True)
finmerged.drop('decktypeid',axis=1,inplace=True)
finmerged.drop('finishedsquarefeet13',axis=1,inplace=True)
finmerged.drop('finishedsquarefeet15',axis=1,inplace=True)
finmerged.drop('finishedsquarefeet50',axis=1,inplace=True)
finmerged.drop('finishedsquarefeet6',axis=1,inplace=True)
finmerged.drop('poolsizesum',axis=1,inplace=True)
finmerged.drop('hashottuborspa',axis=1,inplace=True)
finmerged.drop('pooltypeid10',axis=1,inplace=True)
finmerged.drop('storytypeid',axis=1,inplace=True)
finmerged.drop('typeconstructiontypeid',axis=1,inplace=True)
finmerged.drop('yardbuildingsqft17',axis=1,inplace=True)
finmerged.drop('yardbuildingsqft26',axis=1,inplace=True)
finmerged=finmerged[np.isfinite(finmerged['latitude'])]
finmerged['poolcnt'].fillna(0,inplace=True)
finmerged['pooltypeid7'].fillna(0,inplace=True)
finmerged["pooltypeid2"].fillna(0,inplace=True)
finmerged.drop(['finishedsquarefeet12'],axis=1,inplace=True)
finmerged.drop('calculatedbathnbr',axis=1,inplace=True)
finmerged.drop('fullbathcnt',axis=1,inplace=True)
finmerged['threequarterbathnbr'].fillna(0,inplace=True)
finmerged['airconditioningtypeid'].fillna(5,inplace=True)
finmerged.loc[(finmerged['fireplaceflag']==1),'fireplacecnt']= 1
finmerged['fireplacecnt'].fillna(0,inplace=True)
finmerged.drop(['fireplaceflag'],axis=1,inplace=True)
finmerged['taxdelinquencyflag'].fillna(0,inplace=True)
finmerged['garagecarcnt'].fillna(0,inplace=True)
finmerged.loc[(finmerged['garagecarcnt']==0),'garagetotalsqft']= 0
finmerged['garagetotalsqft']=finmerged.groupby(['garagecarcnt'])['garagetotalsqft'].apply(lambda x: x.fillna(x.mean()))
finmerged['taxdelinquencyyear'].fillna(0,inplace=True)
finmerged["structuretaxvaluedollarcnt"].fillna(finmerged.taxvaluedollarcnt-finmerged.landtaxvaluedollarcnt,inplace=True)
finmerged["landtaxvaluedollarcnt"].fillna(finmerged.taxvaluedollarcnt-finmerged.structuretaxvaluedollarcnt,inplace=True)
finmerged.drop(finmerged.loc[finmerged.taxvaluedollarcnt.isnull()].index,axis=0,inplace=True)
finmerged.drop('censustractandblock',axis=1,inplace=True)
finmerged['taxamount'].fillna(finmerged['taxamount'].mean(),inplace=True)


#this code is taken from a kaggle kernel and helps me to fill in values for regions using k nearest neighbor
#where it makes the most sense
#https://www.kaggle.com/auroralht/restoring-the-missing-geo-data

def fillna_knn( df, base, target, fraction = 1, threshold = 80, n_neighbors = 5 ):
    assert isinstance( base , list ) or isinstance( base , np.ndarray ) and isinstance( target, str ) 
    whole = [ target ] + base
    
    miss = df[target].isnull()
    notmiss = ~miss 
    nummiss = miss.sum()
    
    enc = OneHotEncoder()
    X_target = df.loc[ notmiss, whole ].sample( frac = fraction )
    
    enc.fit( X_target[ target ].unique().reshape( (-1,1) ) )
    
    Y = enc.transform( X_target[ target ].values.reshape((-1,1)) ).toarray()
    X = X_target[ base  ]
    
    print( 'fitting' )
    n_neighbors = n_neighbors
    clf = neighbors.KNeighborsClassifier( n_neighbors, weights = 'uniform' )
    clf.fit( X, Y )
    
    print( 'the shape of active features: ' ,enc.active_features_.shape )
    
    print( 'predicting' )
    Z = clf.predict(df.loc[miss, base])
    
    numunperdicted = Z[:,0].sum()
    if numunperdicted / nummiss *100 < threshold :
        print( 'writing result to df' )    
        df.loc[ miss, target ]  = np.dot( Z , enc.active_features_ )
        print( 'num of unperdictable data: ', numunperdicted )
        return enc
    else:
        print( 'out of threshold: {}% > {}%'.format( numunperdicted / nummiss *100 , threshold ) )

#function to deal with variables that are actually string/categories
def zoningcode2int( df, target ):
    storenull = df[ target ].isnull()
    enc = LabelEncoder( )
    df[ target ] = df[ target ].astype( str )

    print('fit and transform')
    df[ target ]= enc.fit_transform( df[ target ].values )
    print( 'num of categories: ', enc.classes_.shape  )
    df.loc[ storenull, target ] = np.nan
    print('recover the nan value')
    return enc

	
#regionidcity, regionidneighborhood & regionidzip - assume it is the same as the nereast property. 
#As mentioned above, this is ok if there's a property very nearby to the one with missing values (I leave it up to the reader to check if this is the case!)
fillna_knn( df = finmerged,
                  base = [ 'latitude', 'longitude' ] ,
                  target = 'regionidcity', fraction = 0.3, n_neighbors = 5 )

fillna_knn( df = finmerged,
                  base = [ 'latitude', 'longitude' ] ,
                  target = 'regionidneighborhood', fraction = 0.3, n_neighbors = 5 )

fillna_knn( df = finmerged,
                  base = [ 'latitude', 'longitude' ] ,
                  target = 'regionidzip', fraction = 0.3, n_neighbors = 5 )

# #unitcnt - the number of structures the unit is built into. Assume it is the same as the nearest properties. If the property with missing values is in a block of flats or in a terrace street then this is probably ok - but again I leave it up to the reader to check if this is the case!
fillna_knn( df = finmerged,
                  base = [ 'latitude', 'longitude' ] ,
                  target = 'unitcnt', fraction = 0.3, n_neighbors = 5 )

#yearbuilt - assume it is the same as the nearest property. This assumes properties all near to each other were built around the same time
fillna_knn( df = finmerged,
                  base = [ 'latitude', 'longitude' ] ,
                  target = 'yearbuilt', fraction = 0.3, n_neighbors = 5 )

#lot size square feet - not sure what to do about this one. Lets use nearest neighbours. Assume it has same lot size as property closest to it
fillna_knn( df = finmerged,
                  base = [ 'latitude', 'longitude' ] ,
                  target = 'lotsizesquarefeet', fraction = 0.1, n_neighbors = 1 )

#yearbuilt - assume it is the same as the nearest property. This assumes properties all near to each other were built around the same time
fillna_knn( df = finmerged,
                  base = [ 'latitude', 'longitude' ] ,
                  target = 'buildingqualitytypeid', fraction = 0.3, n_neighbors = 5 )

zoningcode2int( df = finmerged,
                            target = 'propertyzoningdesc' )

fillna_knn( df = finmerged,
                  base = [ 'latitude', 'longitude' ] ,
                  target = 'propertyzoningdesc', fraction = 0.3, n_neighbors = 5 )

zoningcode2int( df = finmerged,
                            target = 'propertycountylandusecode' )

finmerged['calculatedfinishedsquarefeet'].fillna(finmerged['calculatedfinishedsquarefeet'].mean(),inplace=True)
finmerged['heatingorsystemtypeid'].fillna(2,inplace=True)
finmerged.drop('numberofstories',axis=1,inplace=True)
finmerged.drop('finishedfloor1squarefeet',axis=1,inplace=True)
finmerged.dropna(axis=0,how="any",inplace=True)

finmerged.to_csv("zillowdata.csv",index=False)
buckname="zillodata"
client = boto3.client('s3',"us-west-2",aws_access_key_id=akey,aws_secret_access_key="putyoursecretaccesskey")
client.create_bucket(Bucket=buckname,CreateBucketConfiguration={'LocationConstraint':"us-west-2"})
client.upload_file("zillowdata.csv", buckname, "zillowdata.csv")

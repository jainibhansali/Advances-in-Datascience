import argparse
import sys
import logging
import datetime
import requests, zipfile, io
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import os
import boto3

parser = argparse.ArgumentParser()
parser.add_argument("--year",help="put year to fetch log files")
parser.add_argument("--akey",help="put your amazon access keys")
parser.add_argument("--skey",help="put your amazon secret access key")
parser.add_argument("--s3loc",help="put the region you want to select for amazon s3")

now=datetime.datetime.now()
u=[]
now1= str(now)
logging.basicConfig(filename="Part2.log",level=logging.DEBUG)

args=parser.parse_args()
if args.year=="1":
	print("Please enter a  year to run the program")
	msg=now1+"  No year entered so exiting the system"
	logging.warning(msg)
	sys.exit(0)

if args.akey == "1" or args.skey == "1":
	logging.warning("No Access key or Secret access key provided")
	print("please enter both access key and secret access key and rerun the program ")
	sys.exit(0)

if args.s3loc == "1":
	logging.info("No S3 locaion provided please put in the location")
	print("No S3 locaion provided please put in the location")
	sys.exit(0)
else:
	s3loc=args.s3loc
	logging.info("S3loc present")	

akey=args.akey
skey=args.skey

years=int(args.year)
	
k=pd.DataFrame()
cont=0
res=pd.DataFrame()
finrow=0
l=None
if not os.path.exists('Part2'):
	msg=str(now)+"    Creating directory for saving tables"
	logging.info(msg)
	os.makedirs('Part2')


if years<2003 or years>2016:
    msg=now1+"  system exited because the data enetered for the year was not present"
    logging.info(msg)
    sys.exit(0)
try:
	for m in range(1,13):
		qtr=None
		if m==1 or m==2 or m==3:
			m1="0"+str(m)
			qtr="Qtr1"      
		elif m==4 or m==5 or m==6:
			m1="0"+str(m)
			qtr="Qtr2"
		elif m==7 or m==8 or m==9:
			m1="0"+str(m)
			qtr="Qtr3"
		elif m==10 or m==11 or m==12:
			m1=str(m)
			qtr="Qtr4"
		msg=now1+"  creating the url for each month"
		logging.info(msg)
		url="http://www.sec.gov/dera/data/Public-EDGAR-log-file-data/" + str(years)+ "/"+qtr+"/"+"log"+str(years)+str(m1)+"01.zip"
		filename="log"+str(years)+str(m1)+"01.csv"
		msg=now1+"  creating the stream to fetch data"
		logging.info(msg)
		r =requests.get(url,stream=True)
		z = zipfile.ZipFile(io.BytesIO(r.content))
		x=z.extractall(os.path.join('Part2'))
		j = pd.read_csv(os.path.join('Part2',filename))
		if j.empty:
			for i in range(1,31):
				y=None
				if i<10:
					y="0"+str(i)
				else:
					y=str(i)
				url="http://www.sec.gov/dera/data/Public-EDGAR-log-file-data/" + str(years)+ "/"+qtr+"/"+"log"+str(years)+str(m1)+y+".zip"
				filename="log"+str(years)+str(m1)+y+".csv"
				r =requests.get(url,stream=True)
				z = zipfile.ZipFile(io.BytesIO(r.content))
				x=z.extractall(os.path.join('Part2'))
				jj = pd.read_csv(os.path.join('Part2',filename))
				if jj.empty:
					continue
				else:
					break
except:
	print("error when connecting to the url please try again")
	msg=now1+"  error encountered when connectng to the url"
	logging.warning(msg)

k2=pd.DataFrame()
cont=0
res=pd.DataFrame()
finrow=0
l=None
	
for m in range(1,13):
	try:
		qtr=None
		if m==1 or m==2 or m==3:
			m1="0"+str(m)
			qtr="Qtr1"      
		elif m==4 or m==5 or m==6:
			m1="0"+str(m)
			qtr="Qtr2"
		elif m==7 or m==8 or m==9:
			m1="0"+str(m)
			qtr="Qtr3"
		elif m==10 or m==11 or m==12:
			m1=str(m)
			qtr="Qtr4"
		msg=str(now)+"    Reading csvs one by one directory for saving tables"
		logging.info(msg)
		filename="log"+str(years)+str(m1)+"01.csv"
		k = pd.read_csv(os.path.join('Part2',filename))
		summaryfile=os.path.join('Part2',str(years)+'Summaries.csv')
		f = open(summaryfile, 'a')
		if k.empty:
			y=None
			for i in range(1,31):
				y=None
				if i<10:
					y="0"+str(i)
				else:
					y=str(i)
				filename="log"+str(years)+str(m1)+y+".csv"
				k = pd.read_csv(os.path.join('Part2',filename))
				if k.empty:
					continue
				else:
					break
			if y=="30" and k.empty:
				f.write("No data present for this particular month   ")
				f.write(filename)
				f.write('\n \n \n \n')
				continue
		msg=str(now)+"    changing datatypes of the columns"
		logging.info(msg)
		k['zone'] = k['zone'].astype('int64')
		k['cik'] = k['cik'].astype('int64')
		k['code'] = k['code'].astype('int64')
		k['idx'] = k['idx'].astype('int64')
		k['noagent'] = k['noagent'].astype('int64')
		k['norefer'] = k['norefer'].astype('int64')
		k['crawler'] = k['crawler'].astype('int64')
		k['find'] = k['find'].astype('int64')
	
		k.dropna(axis=0,how="all",inplace=True)
		k1=k.reset_index(drop=True)



	#renaming the column size as it creates conflict with inbuilt functions
		k1=k1.rename(columns={'size':'Size'})

	#Locking fields for allowable values only
		msg=str(now)+"    Validating the column values"
		logging.info(msg)
		k1.loc[k1['Size']<0,'Size']=np.nan
		k1.loc[~(k1['idx'].isin([0,1])),'idx']=np.nan
		k1.loc[~(k1['norefer'].isin([0,1])),'norefer']=np.nan
		k1.loc[~(k1['noagent'].isin([0,1])),'noagent']=np.nan
		k1.loc[~(k1['crawler'].isin([0,1])),'crawler']=np.nan
		k1.loc[~(k1['browser'].isin(['mie','fox','saf','chr','sea','opr','oth','win','mac','lin','iph','ipd','and','rim','iem'])),'browser']=np.nan

	#checking the maximum count of the browser for the year
		msg=str(now)+"    Finding the the browser eith maximum count for that year"
		logging.info(msg)
		max_bro = k1.groupby(["browser"]).size().rename('countmaxbrowser').idxmax() 
	#print(max_bro)
	#checking the maximum count of the code for the year
		max_code= k1.groupby(["code"]).size().rename('countmaxcode').idxmax()
		msg=str(now)+"    checking the max code for that month"
		logging.info(msg)
	#print(max_code)
	#checking the maximum count of the find for the year
		msg=str(now)+"    max count for the find of that year"
		logging.info(msg)
		max_find=k1.groupby(["find"]).size().rename('countmaxfind').idxmax()
	#print(max_find)
	#checking the maximum count of the extension for the year
		msg=str(now)+"    count of max extention"
		logging.info(msg)
		max_extention=k1.groupby(["extention"]).size().rename('countmaxextention').idxmax()
	#print(max_extention)
	#checking the maximum count of the zone for the year
		msg=str(now)+"    Rcount of max zone"
		logging.info(msg)
		max_zone=k1.groupby(["zone"]).size().rename('countmaxzone').idxmax()
	#print(max_zone)
	#checking the maximum count of the idx for the year
		msg=str(now)+"    count of max idx"
		logging.info(msg)
		max_idx=k1.groupby(["idx"]).size().rename('countmaxidx').idxmax()
	#print(max_idx)

	#Filling Nan values with max Categorical Values
		msg=str(now)+"    Replacing the nan values with appropriate values"
		logging.info(msg)
		k1['browser'].fillna(max_bro,inplace=True)
		k1['code'].fillna(max_code,inplace=True)
		k1['find'].fillna(max_find,inplace=True)
		k1['zone'].fillna(max_zone,inplace=True)
		k1['extention'].fillna(max_extention,inplace=True)
		k1['idx'].fillna(max_idx,inplace=True)

	#Filling empty values with Categorical Values
		k1['norefer'].fillna(1,inplace=True)
		k1['noagent'].fillna(1,inplace=True)
		k1['crawler'].fillna(0,inplace=True)

	#Filling Numerical Data Size Grouping by idx and filling by mean
		k1['Size']=k1.groupby(['idx'])['Size'].apply(lambda x: x.fillna(x.mean()))


	#If cik,Accession,ip,date are empty fields drop the records	
		msg=str(now)+"    dropping rows which have null values for the following columns"
		logging.info(msg)
		k1.dropna(subset=['cik'],inplace=True)
		k1.dropna(subset=['accession'],inplace=True)
		k1.dropna(subset=['ip'],inplace=True)
		k1.dropna(subset=['date'],inplace=True)
		msg=now1+"  merging all data to a single dataframe"
		logging.info(msg)
		if cont==0: 
			k2=k1
		else:
			k2=k2.append(k1)
		cont+=1

	#Starting the summary metrics
		msg=str(now)+"    Missing data handled now starting summary metrics"
		logging.info(msg)
		msg=str(now)+"    Describing the stats for all the column to help us decide the metrics"
		logging.info(msg)
		f.write('Starting Summary Metrics for file ')
		f.write(filename)
		f.write('\n \n \n \n')
		f.write('Describing all the data columns with its statistics value \n')
		f.write('\n')
		k1.describe(include='all').transpose().to_csv(f)
		k1.reset_index(drop=True)



	#providing mean and median sizes for each browser
		msg=str(now)+"    mean and median of file sizes openend in browser"
		logging.info(msg)
		print("Mean and Median Sizes for each Browser")
		df1 = k1.groupby('browser').agg({'Size':['mean', 'median'],'crawler': len})
		df1.columns = ['_'.join(col) for col in df1.columns]
		k1.reset_index(drop=True)
		f.write('\n')
		f.write("Providing mean and median sizes for each browser")
		f.write('\n \n')
		df1.to_csv(f)


	#providing the mean and sum of file size on basis of idx
		msg=str(now)+"    taking mean file size on basis of idx we find a lot of difference in this metrics"
		logging.info(msg)
		print("Mean and Sum of File Sizes on the basis of IDX")
		df2 = k1.groupby('idx').agg({'Size':['mean', 'sum']})
		df2.columns = ['_'.join(col) for col in df2.columns]
		k1.reset_index(drop=True)
		print(df2)
		f.write('\n')
		f.write("Providing the mean and sum of file size on basis of idx")
		f.write('\n \n')
		df2.to_csv(f)

#calculating median grouping by idx column using median
		msg=str(now)+"    Median of all data on the basis of idx"
		logging.info(msg)
		da=k1.groupby('idx').median()
		k1.reset_index(drop=True)
		print(da)
		f.write('\n')
		f.write("Calculating median grouping by idx column using median")
		f.write('\n \n')
		da.to_csv(f)
	#Top 5 CIK
		msg=str(now)+"    Top searched cik's"
		logging.info(msg)
		count_cik=k1[['cik','ip']].groupby(['cik'])['ip'].count().reset_index(name='count').sort_values(['count'],ascending=False).head(5)
		print(count_cik)
		k1.reset_index(drop=True)
		f.write('\n')
		f.write("Top 5 CIK")
		f.write('\n \n')
		count_cik.to_csv(f)
	
		msg=str(now)+"    checking count of status code"
		logging.info(msg)
		count_code=k1[['code','ip']].groupby(['code'])['ip'].count().reset_index(name='count').sort_values(['count'],ascending=False)
		print(count_code)
		k1.reset_index(drop=True)
		f.write('\n')
		f.write("Number of hits per IP ")
		f.write('\n \n')
		count_code.to_csv(f)
	#Number of hits per date 
		msg=str(now)+"    number of request made per day"
		logging.info(msg)
		count_date=k1[['date','ip']].groupby(['date'])['ip'].count().reset_index(name='count').sort_values(['count'],ascending=False)
		print(count_date)
		k1.reset_index(drop=True)
		f.write('\n')
		f.write("Number of hits per date ")
		f.write('\n \n')
		count_date.to_csv(f)
		msg=str(now)+"    mean file size on the basis of a date"
		logging.info(msg)
		mean_date=k1[['date','Size']].groupby(['date'])['Size'].mean().reset_index(name='mean').sort_values(['mean'],ascending=False)
		print(mean_date)
		k1.reset_index(drop=True)
		f.write('\n')
		f.write("Average File size by date Sorted by Mean ")
		f.write('\n \n')
		mean_date.to_csv(f)
		msg=str(now)+"    mean file size on basis of cik"
		logging.info(msg)
		cik_date=k1[['cik','Size']].groupby(['cik'])['Size'].mean().reset_index(name='mean').sort_values(['mean'],ascending=False).head(5)
		print(cik_date)
		k1.reset_index(drop=True)
		f.write("Average CIK by date Sorted by Mean ")
		f.write('\n')
		cik_date.to_csv(f)
		f.close()
	except:
		msg=now1+"   Error while cleaning and summarizing data"
		logging.warning(msg)


##-----------------------------------------------------------------##
#Top 5 CIK

datafile=os.path.join('Part2',str(years)+'Compileddata.csv')
f2 = open(datafile, 'a')
k2.to_csv(f2)
f2.close()
msg=str(now)+"    plotting the graph for top 5 cik"
logging.info(msg)
count_cik=k2[['cik','ip']].groupby(['cik'])['ip'].count().reset_index(name='count').sort_values(['count'],ascending=False).head(5)
k2.reset_index(drop=True)
print(count_cik)
x = np.array(range(len(count_cik)))
y = count_cik['count']
my_xticks = count_cik['cik']
#plt.xticks(count_code.index, count_code['code'], rotation=90,y='count')
plt.xticks(x, my_xticks)
plt.bar(x,y)
plt.title('Top 5 CIK by Count of Hits')
plt.ylabel('Count of Hits')
plt.xlabel('CIK-')
plt.savefig(os.path.join('Part2','Top5CIKbyCount.png'),dpi=100)
plt.show()
plt.clf()	

##------------------------------------------------------------------##	
#Number of hits per IP 
msg=str(now)+"    plotting the graph for number of status code"
logging.info(msg)


try:
	count_code=k2[['code','ip']].groupby(['code'])['ip'].count().reset_index(name='count').sort_values(['count'],ascending=False)
	k2.reset_index(drop=True)
	print(count_code)

#plotting graph
	x = np.array(range(len(count_code)))
	y = count_code['count']
	my_xticks = count_code['code']
#plt.xticks(count_code.index, count_code['code'], rotation=90,y='count')
	plt.xticks(x, my_xticks)
	plt.bar(x,y)
	plt.title('Count of status codes for all request')
	plt.ylabel('Count of Hits')
	plt.xlabel('Code')
	plt.savefig(os.path.join('Part2','NumberofHitsperIP.png'),dpi=100)
	plt.show()
	plt.clf()
except:
	msg=str(now)+"    error plotting 2nd graph"
	logging.info(msg)






##-----------------------------------------------------------------------------------##
#Number of hits per date 
try:
	msg=str(now)+"    number of requests made pe day"
	logging.info(msg)
	count_date=k2[['date','ip']].groupby(['date'])['ip'].count().reset_index(name='count').sort_values(['count'],ascending=False)
	print(count_date)
	k2.reset_index(drop=True)

#PLotting graph by date
	x = np.array(range(len(count_date)))
	y = count_date['count']
	my_xticks = count_date['date']
#plt.xticks(count_code.index, count_code['code'], rotation=90,y='count')
	plt.xticks(x, my_xticks)
#plt.plot(x,y)
	plt.xticks(rotation=70)
	plt.bar(x,y,align='center', alpha=0.5)
	plt.title('Number of Hits by Date')
	plt.ylabel('Count of Hits')
	plt.xlabel('Date',fontsize=2)
	plt.savefig(os.path.join('Part2','NumberofHitsPerDate.png'),dpi=100)
	plt.show()
	plt.clf()

except:
	msg=str(now)+"    error plotting 3rd graph"
	logging.info(msg)
##----------------------------------------------------------------------------------##
msg=str(now)+"    Average file size opened on a date"
logging.info(msg)

#Avg File size by date 
try:
	mean_date=k2[['date','Size']].groupby(['date'])['Size'].mean().reset_index(name='mean').sort_values(['mean'],ascending=False)
	print(mean_date)
	k2.reset_index(drop=True)

#Plotting graph
	x = np.array(range(len(mean_date)))
	y = mean_date['mean']
	my_xticks = mean_date['date']
#plt.xticks(count_code.index, count_code['code'], rotation=90,y='count')
	plt.xticks(x, my_xticks)
#plt.plot(x,y)
	plt.xticks(rotation=70)
	plt.yticks(rotation=30)
	plt.bar(x,y,align='center', alpha=0.5)
	plt.title('Average File Size by Date')
	plt.ylabel('Avg File Size')
	plt.xlabel('Date')
	plt.savefig(os.path.join('Part2','AvgFilebyDate.png'),dpi=100)
	plt.show()
	plt.clf()
except:
	msg=str(now)+"    error plotting 4th graph"
	logging.info(msg)
##-----------------------------------------------------------------------------##
msg=str(now)+"    average mean file size of cik "
logging.info(msg)
try:
	cik_date=k2[['cik','Size']].groupby(['cik'])['Size'].mean().reset_index(name='mean').sort_values(['mean'],ascending=False).head(5)

	k2.reset_index(drop=True)

#PLotting graph by cik and size
	x = np.array(range(len(cik_date)))
	print(x)
	y = cik_date['mean']
	print(y)
	my_xticks = cik_date['cik']
#plt.xticks(count_code.index, count_code['code'], rotation=90,y='count')
	plt.xticks(x, my_xticks)
#plt.plot(x,y)
	plt.xticks(rotation=70)
	plt.bar(x,y,align='center', alpha=0.5)
	plt.title('Average File Size by CIK')
	plt.ylabel('Avg File Size')
	plt.xlabel('CIK')
	plt.savefig(os.path.join('Part2','CIKvsSize.png'),dpi=100)
	plt.show()
	plt.clf()
except:
	msg=str(now)+"    error plotting 5th graph"
	logging.info(msg)

###----------------------------------------------------------------------####

msg=str(now)+"    Average traffic per hour everyday"
logging.info(msg)

try:
	k2['fintime']=pd.to_datetime(k2['time'])
	def hr_func(ts):
		return ts.hour
	k2['time_hour'] = k2['fintime'].apply(hr_func)

	Time_Trend=k2[['ip','time_hour']].groupby(['time_hour'])['ip'].count().reset_index(name='count').sort_values(['time_hour'],ascending=True)
	print(Time_Trend)


#PLotting graph of TimeSeries
	x = np.array(range(len(Time_Trend)))
	print(x)
	y = Time_Trend['count']
	print(y)
	my_xticks = Time_Trend['time_hour']
#plt.xticks(count_code.index, count_code['code'], rotation=90,y='count')
	plt.xticks(x, my_xticks)
#plt.plot(x,y)
#plt.xticks(rotation=70)
	plt.plot(x,y)
	plt.title('Average traffic per hour everyday')
	plt.ylabel('Hours')
	plt.xlabel('Count')
	plt.savefig(os.path.join('Part2','TimeSeries.png'),dpi=100)
#droppingcolumn fintime
	plt.show()
	plt.clf()
	del k2['fintime']
	del k2['time_hour']
	
except:
	msg=str(now)+"    error plotting 6th graph"
	logging.info(msg)
##----------------------------------------------------------------------##
try:
	k2.boxplot(column='Size',by='idx',vert=True,sym='',whis=10,showfliers=False)
	plt.xticks(rotation=70)
	plt.title('Anomalies in File Size by Index Page')
	plt.ylabel('File Size')
	plt.xlabel('Count')

	plt.savefig(os.path.join('Part2','FileSizebyIndex.png'),dpi=100)
	plt.show()
#BoxPlot Size by Date
	k2.boxplot(column='Size',by='date',vert=True,sym='',whis=10,showfliers=False)
	plt.xticks(rotation=70)
	plt.title('Anomalies in File Size by Date')
	plt.ylabel('FileSize')
	plt.xlabel('Date')
	plt.savefig(os.path.join('Part2','FileSizebyDate.png'),dpi=100)
	plt.show()
#BoxPlot Anomalies in FileSize
	print("last boxplot")
	k2.boxplot(column='Size',vert=True,sym='',whis=10,showfliers=False)
	plt.xticks(rotation=70)
	plt.title('Anomalies in File Size')
	plt.ylabel('FileSize')

	plt.savefig(os.path.join('Part2','AnomaliesinFileSize.png'),dpi=100)
	plt.show()
	print("lastboxplotcomplete")
except:
	msg=str(now)+"    error plotting boxplots"
	logging.info(msg)

print(k2.describe())
print(k2.info())


def zipdir(path, ziph):
	ziph.write(os.path.join('Part2', str(years)+'Summaries.csv'))
	ziph.write(os.path.join('Part2.log'))
	ziph.write(os.path.join('Part2','Top5CIKbyCount.png'))
	ziph.write(os.path.join('Part2','NumberofHitsperIP.png'))
	ziph.write(os.path.join('Part2','NumberofHitsPerDate.png'))
	ziph.write(os.path.join('Part2','AvgFilebyDate.png'))
	ziph.write(os.path.join('Part2','CIKvsSize.png'))
	ziph.write(os.path.join('Part2','TimeSeries.png'))
	ziph.write(os.path.join('Part2','FileSizebyDate.png'))
	ziph.write(os.path.join('Part2','FileSizebyIndex.png'))
	ziph.write(os.path.join('Part2','AnomaliesinFileSize.png'))
	ziph.write(os.path.join('Part2',str(years)+'Compileddata.csv'))
zipf = zipfile.ZipFile('Assignment1Part2.zip', 'w', zipfile.ZIP_DEFLATED)
zipdir('/', zipf)
zipf.close()
logging.info('csv and log file zipped')

#msg=str(now)+"    error zipping he files"
#logging.info(msg)
#print("error encountered while zipping the file")
#sys.exit(0)





	
	
	

try:
	fin2=now1.replace(":","")
	fin3=fin2.replace("-","")
	fin=fin3.replace(" ","")
	buckname="assignmenttablesteamfive"+fin
	client = boto3.client('s3',s3loc,aws_access_key_id=akey,aws_secret_access_key=skey)
	client.create_bucket(Bucket=buckname,CreateBucketConfiguration={'LocationConstraint':s3loc})
	client.upload_file("Assignment1Part2.zip", buckname, "Assignment1Part2.zip")
except:
	logging.warning("error upload to s3")
	print("error uploading to s3 choose a different location or check your keys")
import argparse
import pandas as pd
import html5lib
import logging
import datetime
import sys
from bs4 import BeautifulSoup
import urllib3
import numpy as np
import urllib.request
import csv
import zipfile
import os
import boto3
now=datetime.datetime.now() 
parser = argparse.ArgumentParser()
parser.add_argument("--cik",help="put CIK")
parser.add_argument("--acn",help="put accession number")
parser.add_argument("--akey",help="put your amazon access keys")
parser.add_argument("--skey",help="put your amazon secret access key")
parser.add_argument("--s3loc",help="put the region you want to select for amazon s3")
args=parser.parse_args()

now1= str(now)
logging.basicConfig(filename="Part2.log",level=logging.DEBUG)

cik=None
accessionNumber=None
akey=None
skey=None
s3loc=None
if args.cik == "1" or args.acn == "1":
	print("please put in the CIK and the Accession Number to begin")
	msg=str(now)+"  cik or the accession key not present"
	logging.warning(msg)
	sys.exit(0)
else:
	msg=str(now)+"   cik and the accession number found"
	logging.debug(msg)
	cik=args.cik
	accessionNumber=args.acn

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
print(akey,skey)

url_pre = "https://www.sec.gov/Archives/edgar/data/"
msg=str(now)+"   Removing 0's from CIK for url"
logging.info(msg)
cik_striped = cik.lstrip("0")
msg=str(now)+"   Removing - from accession number for url"
logging.info(msg)
accno_striped = accessionNumber.replace("-","")
msg=str(now)+"   Creating the first url"
logging.info(msg)
url1 = url_pre + cik_striped + "/" + accno_striped + "/" + accessionNumber + "-index.html"        
print(url1)
url2=''
try:
	page = urllib.request.urlopen(url1)
	soup = BeautifulSoup(page,"lxml")  
	form = soup.find(id='formName').get_text() 
	formname = form[6:10]
	formtype = soup.findAll('td', text = formname)[0]
	all_links = soup.find_all('a')
	for link in all_links:
		href=link.get("href")
		if "10q.htm" in href:
			url2 = str("https://www.sec.gov/"+ href)
			msg=str(now)+"   url found and created for the 10q file"
			logging.warning(msg)
			break;
		else:
			url2=""
            
            
	if url2 is "":
		msg=str(now)+"   Invalid URL!!! or 10q not found for the given cik or accession number"
		logging.warning(msg)
		print("Invalid URL!!! or 10q not found for the given cik or accession number")
		exit()  


	
except urllib.error.HTTPError as err:
	msg=str(now)+"   Invalid cik or accession number"
	logging.warning(msg)
	print("Invalid CIK or AccNo")
	exit()

msg=str(now)+"   Checking if a directory exisist for saving the tables if not then creating one"
logging.info(msg)
if not os.path.exists('Tables'):
	msg=str(now)+"    Creating directory for saving tables"
	logging.info(msg)
	os.makedirs('Tables')
try:	
	pandu=pd.read_html(url2)
except:
	logging.warning("Error encountered while connecting to the 10-q file url")
count=0
for i in pandu:
	try:
		msg=str(now)+"   got the table now checking if it has $ or % in it"
		logging.info(msg)
		x=None
		flag=0
		t=i.shape
		for j in range(0,t[0]):
			if flag==1:
				break
			for m in range(0,t[1]):
				if i[m][j]=="$" or i[m][j]=="%":
					flag=1
					x=i
					break
					
		
		if len(i.columns)>3:
			msg=str(now)+"   only taking tables where there are more than 3 columns and cleaning the data"
			logging.info(msg)
			exah=x.replace(r'\n',"", regex=True)
			msg=str(now)+"   removing \n from table"
			logging.info(msg)
			example3=exah.dropna(axis=1,how="all")
			example4=example3.dropna(axis=0,how="all")
			msg=str(now)+"   removed all columns or rows with all nan values"
			logging.info(msg)
			exa=example4.reset_index(drop=True)
			example6=exa.replace(r'\n',"", regex=True)
			sh=example6.shape
			l=list(range(0,sh[1]))
			example6.columns=l
			msg=str(now)+"   reindexing and merging the $ and numeric values which were misplaced"
			logging.info(msg)
			
			for s in range(0,sh[0]):
				for k in range(0,sh[1]):        
					if example6[k][s] =="$":
						for p in range(k+1,sh[1]):
							if isinstance(example6[p][s],float) or isinstance(example6[p][s],np.float64) or isinstance(example6[p][s],np.str):
								example6[k][s]=str("$"+str(example6[p][s]))
								example6[p][s]=None
								break
			example7=example6.replace(r'\(','',regex=True)#currently removed number pattern as it was removing the number as well
			msg=str(now)+"   replacing ) ( % $ % nans where not appropriate"
			logging.info(msg)
			examji=example7.replace(r'\)','',regex=True)
			example8=examji.replace(')',np.nan)
			example9=example8.replace(r'\)%','',regex=True)
			example10=example9.replace(r'^\s*$', np.nan, regex=True)
			example13=example10.replace(r'%',np.nan,regex=True)
			exa2=example13.replace("\xa0","")
			#example14=example13.replace(r'NaN',None,regex=True)
			example11=exa2.dropna(axis=1,how="all")
			example12=example11.reset_index(drop=True)
			sh1=example12.shape
			l1=list(range(0,sh1[1]))
			example12.columns=l1
			msg=str(now)+"   checking for null in the begining and realigning rows"
			logging.info(msg)
			for s in range(0,sh1[0]): 
				for k in range(0,sh1[1]):
					if pd.isnull(example12[k][s]):
						for j in range(k+1,sh1[1]):
							if pd.isnull(example12[j][s]):
								continue
							else:
								example12[k][s]=example12[j][s]
								example12[j][s]=None
								break
			example13=example12.dropna(axis=1,how="all")
			example14=example13.dropna(axis=0,how="all")
			example15=example14.reset_index(drop=True)
			sh2=example15.shape
			l2=list(range(0,sh2[1]))
			example15.columns=l2
			counter2=0
			msg=str(now)+"   moving data where only one nan found to the right"
			for s in range(0,sh2[0]):
				for k in range(0,sh2[1]):
					if pd.isnull(example15[k][s]):
						counter2+=1
					if counter2==2:
						break
				if counter2==1:
					for l in range((sh2[1]-1),-1,-1):
						if l >0:
							example15[l][s]=example15[l-1][s]
						else:
							example15[0][s]=None

			count+=1
			example16=example15.replace(np.nan," ")
			msg=str(now)+"   joining paths for creating tables"
			logging.info(msg)
			filename=os.path.join('Tables' , str(count) + '.csv')
			msg=str(now)+"   creating csv"
			logging.info(msg)
			example16.to_csv(filename,index=False)
			
	except:
		msg=str(now)+"   The table is corrupt so it cannot be extracted"
		logging.warning(msg)
print(count)

def zipdir(path, ziph):
	for c in range(1,count+1):
		ziph.write(os.path.join('Tables', str(c)+'.csv'))
	ziph.write(os.path.join('Part2.log'))   

zipf = zipfile.ZipFile('Assignment1Part1.zip', 'w', zipfile.ZIP_DEFLATED)
zipdir('/', zipf)
zipf.close()
logging.info('csv and log file zipped')
print(akey)
print(skey)
print(s3loc)
try:
	fin2=now1.replace(":","")
	fin3=fin2.replace("-","")
	fin=fin3.replace(" ","")
	buckname="assignmenttablesteamfive"+fin
	client = boto3.client('s3',s3loc,aws_access_key_id=akey,aws_secret_access_key=skey)
	client.create_bucket(Bucket=buckname,CreateBucketConfiguration={'LocationConstraint':s3loc})
	client.upload_file("Assignment1Part1.zip", buckname, "Assignment1Part1.zip")
except:
	logging.warning("error upload to s3")
	print("error uploading to s3 choose a different location or check your keys")
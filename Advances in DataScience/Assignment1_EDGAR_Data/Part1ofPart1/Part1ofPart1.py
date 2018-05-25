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

parser = argparse.ArgumentParser()
parser.add_argument("--cik",help="put CIK")
parser.add_argument("--acn",help="put accession number")

args=parser.parse_args()
cik=None
accessionNumber=None
if args.cik == None or args.acn == None:
	print("please put in the CIK and the Accession Number to begin")
	sys.exit(0)
else:
	cik=args.cik
	accessionNumber=args.acn
print("CIK=",cik)
print("Accession Number=",accessionNumber)

url_pre = "https://www.sec.gov/Archives/edgar/data/"
cik_striped = cik.lstrip("0")
accno_striped = accessionNumber.replace("-","")
url1 = url_pre + cik_striped + "/" + accno_striped + "/" + accessionNumber + "-index.html"        
url2=''
try:
    page = urllib.request.urlopen(url1)
    soup = BeautifulSoup(page,"lxml") # parse the page and save it in soup format 
    form = soup.find(id='formName').get_text() # find the form name according to accession no
    formname = form[6:10]
    formtype = soup.findAll('td', text = formname)[0]
    all_links = soup.find_all('a')
    for link in all_links:
        href=link.get("href")
        if "10q.htm" in href:
            url2 = "https://www.sec.gov/" + href
            break;
        else:
            url2=""
            
            
    if url2 is "":
        print("Invalid URL!!! or 10q not found for the given cik or accession number")
        exit()  


	
except urllib.error.HTTPError as err:
    print("Invalid CIK or AccNo")
    exit()

if not os.path.exists('extracted_csvs'):
    os.makedirs('extracted_csvs')
	
pandu=pd.read_html(url2)

count=0
for i in pandu:
	try:
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
			exah=x.replace(r'\n',"", regex=True)
			example3=exah.dropna(axis=1,how="all")
			example4=example3.dropna(axis=0,how="all")
			exa=example4.reset_index(drop=True)
			example6=exa.replace(r'\n',"", regex=True)
			sh=example6.shape
			l=list(range(0,sh[1]))
			example6.columns=l
			for s in range(0,sh[0]):
				for k in range(0,sh[1]):        
					if example6[k][s] =="$":
						for p in range(k+1,sh[1]):
							if isinstance(example6[p][s],float) or isinstance(example6[p][s],np.float64) or isinstance(example6[p][s],np.str):
								example6[k][s]=str("$"+str(example6[p][s]))
								example6[p][s]=None
								break
			example7=example6.replace(r'\(','',regex=True)#currently removed number pattern as it was removing the number as well
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
			filename=os.path.join('extracted_csvs' , str(count) + '.csv')
			print(filename)
			example16.to_csv(filename,index=False)
			print(example16)
	except:
		pass
print(count)

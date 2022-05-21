import shutil
import pandas as pd
from datetime import datetime
import requests
import os
from pathlib import Path
import random
import streamlit as st

st.title("MarktStraat")
c1 = st.container()
def isUrlValid(url):
    try:
        requests.get(url, timeout = 5)
    except Exception as e:
        return False
    else:
        return True

def brainy(from_date,to_date):  

   
    txt = st.empty()
    
   
    dt = pd.date_range(start=from_date, end=to_date, freq='B')
    
    for tday in dt:
        
        try:
            dmyformat = datetime.strftime(tday,'%d%m%Y')
            print("processing "+ dmyformat)
            
            dMMyFormatUpperCase = datetime.strftime(tday,'%d%b%Y').upper()
            filenamedate = datetime.strftime(tday,'%m%d%Y').upper()
            monthUppercase = datetime.strftime(tday,'%b').upper()
            year = datetime.strftime(tday,'%Y')
            
            url_dlvry = 'https://archives.nseindia.com/archives/equities/mto/MTO_'+ dmyformat +'.DAT'
            if not isUrlValid(url_dlvry):
                print("maybeholiday" + dmyformat)
                continue
        
            print(url_dlvry)
            
            data1 = pd.read_csv(url_dlvry,skiprows=3) 
            data1 = data1.rename(columns={"Name of Security":"NS"})
            data1 = data1.query('NS == "EQ"  or NS == "BE"')            
            data1 = data1.rename(columns={"Sr No": "SYMBOL"})
            
         
        
            url_bhav = 'https://archives.nseindia.com/content/historical/EQUITIES/'+ year + '/' + monthUppercase +'/cm' +dMMyFormatUpperCase+'bhav.csv.zip'
            print(url_bhav)
            data2 = pd.read_csv(url_bhav) 
            
            
            df = data2.query('SERIES == "EQ"  or SERIES == "BE"')
            
            
            result = df            
            result = result[['SYMBOL','TIMESTAMP','OPEN','HIGH','LOW','CLOSE','TOTTRDQTY','TOTALTRADES',]]

            filename = filenamedate + '_NSE.txt'
            #change download path as per your systemhttps://archives.nseindia.com/content/indices/ind_close_all_13052022.csv
            p = Path('C:\\Trading Stuff\\bhavcopy\\fno\\')
            p.mkdir(exist_ok=True)
            #result.to_csv('C:\\Trading Stuff\\bhavcopy\\fno\\' + filename, header =False,index = False )
            index_bhav = 'https://archives.nseindia.com/content/indices/ind_close_all_'+dmyformat+'.csv'
            print(index_bhav)
            ib = pd.read_csv(index_bhav)
            ib.rename(columns={'Index Name':'SYMBOL','Index Date':'TIMESTAMP','Open Index Value':'OPEN','High Index Value':'HIGH','High Index Value':'HIGH',
            'Low Index Value':'LOW','Closing Index Value':'CLOSE','Volume':'TOTTRDQTY','P/B':'TOTALTRADES',}, inplace=True)
           
            ib = ib[['SYMBOL','TIMESTAMP','OPEN','HIGH','LOW','CLOSE','TOTTRDQTY','TOTALTRADES',]]
            ib['TIMESTAMP'] = pd.to_datetime(ib['TIMESTAMP'], dayfirst=True,infer_datetime_format=True).dt.strftime('%d-%b-%Y')
            ib.drop(labels=8,axis=0,inplace=True)
            ib=ib.head(26)
            result = pd.concat([result,ib],axis = 0)
            result.to_csv('C:\\Trading Stuff\\bhavcopy\\fno\\' + filename, header =False,index = False )
           
            txt.write("Data Successfully writen for 👉 " + dMMyFormatUpperCase)
            
            
            
            #st.write("Data Successfully writen for " + dMMyFormatUpperCase)
        except Exception as e:
            st.write("Oops!  Error in " , e  )
            pass
    return 0

#def import2ami():
    
with st.sidebar:
    from_date = st.date_input("From")
    to_date = st.date_input("To")
    result = st.button("Download")
    if result:
       r= brainy(from_date, to_date)
       with c1:
           #s = import2ami()
        st.write(" job complete @ " + datetime.strftime(datetime.now(),'%m%d%Y').upper() )


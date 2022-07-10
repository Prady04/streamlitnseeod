from multiprocessing import connection
import shutil
from time import sleep
import pandas as pd
from datetime import datetime
import requests
import os
from pathlib import Path
import random
import streamlit as st
from sqlite3 import connect
import csv
import numpy as np
from ami2py import AmiDataBase, SymbolData, SymbolEntry
import os
import win32com.client
import pythoncom
import glob
from win32com.client import Dispatch
import logging

from screener_scrapper import Scrapper



logging.basicConfig(filename='./st.log', encoding='utf-8', level=logging.DEBUG)


imp_tbl = [
    {'db': "C:\\Program Files\\AmiBroker\\Databases\\stockD",
    'data': "C:\\tradedb\\*.txt",
    'format': "nsepy.format"},]
    
def import_data(ab, lst):
    ab.Visible = True
    for l in lst:
        logging.debug("Loading database {}".format(os.path.split(l['db'])[1]))
        print("Loading database {}".format(os.path.split(l['db'])[1]))
        print(ab.LoadDatabase(l['db']))
        f_lst = sorted(set(glob.glob(l['data'])))
        for f in f_lst:
            try:
                print("Importing datafile {}, using format {}".format(f, l['format']))
                ab.Import(0, f, l['format'])               
               
            except e:
                print("Error importing datafile {}".format(f))
            else:
                (newpath, filename) = os.path.split(f)
                try:
                    dest = os.path.join(newpath, "archive", filename)
                    if(os.path.exists(dest)):
                        os.remove(dest)
                    os.rename(f, os.path.join(newpath, "archive", filename))
                    print("Import complete")
                except Exception as e:
                    print(r'Errror archiving datafile {}'.format(e)) 
                    pass


        print("Saving Db")        
        ab.SaveDatabase()
        ab.RefreshAll()
        ab.Quit()
        print("Done..")

def connect2db():
    con = None
    try: 
        con = connect('./stocks.db')
    except Exception as e:
        print(e)
    return con

st.title("MarktStraat")
c1 = st.container()
c2 = st.container()
with c1:
    st.image("./mb.png")
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
        
           
            
            data1 = pd.read_csv(url_dlvry,skiprows=3) 
            data1 = data1.rename(columns={"Name of Security":"NS"})
            data1 = data1.query('NS == "EQ"  or NS == "BE"')            
            data1 = data1.rename(columns={"Sr No": "SYMBOL"})
            
         
        
            url_bhav = 'https://archives.nseindia.com/content/historical/EQUITIES/'+ year + '/' + monthUppercase +'/cm' +dMMyFormatUpperCase+'bhav.csv.zip'
            
            data2 = pd.read_csv(url_bhav) 
            
            
            df = data2.query('SERIES == "EQ"  or SERIES == "BE"')
            
            
            result = df            
            result = result[['SYMBOL','TIMESTAMP','OPEN','HIGH','LOW','CLOSE','TOTTRDQTY','TOTALTRADES',]]

            filename = filenamedate + '_NSE.txt'
            #change download path as per your systemhttps://archives.nseindia.com/content/indices/ind_close_all_13052022.csv
            p = Path('C:\\TradeDb\\')
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
            result.to_csv("C:\\Tradedb\\"+ filename, header =False,index = False )
            
            insert = "INSERT INTO DATA('symbol','timestamp','open','high','low','close','volume','trades') VALUES (?,?,?,?,?,?,?,?)"
            con = connect2db()
            cur = con.cursor()
            
            
            #result[['SYMBOL','TIMESTAMP','OPEN','HIGH','LOW','CLOSE','TOTTRDQTY','TOTALTRADES',]]
            result['OPEN'] = pd.to_numeric(result['OPEN'], errors='coerce')
            result['HIGH'] = pd.to_numeric(result['HIGH'], errors='coerce')
            result['LOW'] = pd.to_numeric(result['LOW'], errors='coerce')
            result['CLOSE'] = pd.to_numeric(result['CLOSE'], errors='coerce')
            result['TOTTRDQTY'] = pd.to_numeric(result['TOTTRDQTY'], errors='coerce')
            result['TOTALTRADES'] = pd.to_numeric(result['TOTALTRADES'], errors='coerce')
          
            for index, row in result.iterrows():
                cur.execute(insert,(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))
                
            con.commit()
            con.close()   
 

           
            txt.write("Data Successfully writen for 👉 " + dMMyFormatUpperCase)

        except Exception as e:
            con.close()
            st.write("Oops!  Error in " , e  )
            pass
        
    return 0

def screen_stocks():
    scrapper = Scrapper('https://www.screener.in/screens/732464/eps-gainers/')
    
    df = scrapper.process() 
    with c2:         
        st.dataframe(df)

    

    
with st.sidebar:
    from_date = st.date_input("From")
    to_date = st.date_input("To")
    result = st.button("Download")
    if result:
       r= brainy(from_date, to_date)
      
       
              
       with c1:
        st.write("preparing to import to amibroker")
        ab = win32com.client.Dispatch('Broker.Application', pythoncom.CoInitialize())
        success = import_data(ab, imp_tbl)
        st.write("completed {}".format(success))
        st.write(" job complete @ " + datetime.strftime         (datetime.now(),'%m%d%Y').upper() )

    funda = st.button('Screen high EPS Stocks')
    if funda:
        screen_stocks()

#importing required module -------------------------------------------------------------

import requests 
from bs4 import BeautifulSoup as bs 
import re 
import pandas
from datetime import datetime
import argparse

dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

class Scrapper:
  def __init__(self, lnk):
    self.data = lnk
      
    
      

  #main driver code ----------------------------------------------------------------------

  #if ?page=0 is present in the url it will be removed 
  def page_attr_remover(self,url):
      pattern = re.compile(r'\?page.*')
      match = list(pattern.finditer(url))
      if match:
          end_of_url = list(match)[0].span()[0]
          url = url[:end_of_url]
      return url


#extracting and cleaning link got from the post request 


  def link_extractor(self,input_string):
      dirty_links = input_string.split('\n')
      dirty_links = [link.strip() for link in dirty_links]
      cleaned_links = []
      pattern = re.compile(r'https://www.screener.in/screens/\d*/.\w*')
      for link in dirty_links:
          temp = list(pattern.finditer(link))
          len_temp = len(temp)
          if temp:
              if len_temp>=2:
                  split_points = [ele.span()[0] for ele in temp]
                  for num in range(1,len_temp):
                      page_removed_url = self.page_attr_remover(link[split_points[num-1]:split_points[num]])
                      cleaned_links.append(page_removed_url)
                  page_removed_url = self.page_attr_remover(link[split_points[-1]:])
                  cleaned_links.append(page_removed_url)
              else:
                  page_removed_url = self.page_attr_remover(link)
                  cleaned_links.append(page_removed_url)
      cleaned_links = [link for link in cleaned_links if link.startswith('https://')]
      return cleaned_links

  
  #fetching the number of pages on the link
  def page_range(self,page):
      string = ''

      for i in page.find_all(class_='sub'):
          string += i.text

      search = re.compile(r'Page [1-9] of [1-9].') 

      matches = search.findall(string)

      return matches[0][-2]



  def fetch_data(self,data, data_available, data_not_available):
      #correct links 
      data_links = data

      #specific page url
      page_url = "?page={}"

      #empty DataFrame
      data_file_0 = pandas.DataFrame()

      for current_url in data_links:
          
          page = bs(requests.get(current_url).content, 'html.parser')

          #error detection
          string1 = re.compile('Error 404')

          txt = page.title.get_text()

          if string1.findall(txt):
              data_not_available.append(current_url)
              continue
          else:
              if not page.find_all('tr'):
                  data_not_available.append(current_url)
                  continue
              else:
                  data_available.append(current_url)


          #page range 
          limit = int(self.page_range(page))
          
          #parsing data from individual links
          for value in range(1,limit+1):
              #data collector list
              data_collector = []
              #column names
              atr_name  = []

              #constructing temporary url for fetching data
              temp_url = current_url + page_url.format(value)

              #fetch the web page
              page = requests.get(temp_url)

              #data on the page
              page = page.content

              #parsing object

              soup = bs(page, 'html.parser')

              #list to collect the data
              fetched_current_table = []


              #find all row entry
              for rows in soup.find_all('tr'):
                  fetched_current_table.append(rows)


              for cols in fetched_current_table[0].find_all('th'):
                  atr_name.append(cols.get('data-tooltip'))

              #adjusting the attribute of column 1 and 2
              atr_name[0] = 'Data URL'
              atr_name[1] = 'Names'



              #Fetching the individual rows
              for _ in range(1, len(fetched_current_table)):


                  #try block to handel the empty
                  try:
                      temp = []
                      for i in fetched_current_table[_].find_all('td'):
                          temp.append(i.text)

                      #removing the '\n' and ' ' from the name string
                      temp[1] = temp[1].split('\n')[2].strip()

                      #inserting the url
                      temp[0] = temp_url

                      data_collector.append(temp)
                  except:
                      pass

              data_file_1 = pandas.DataFrame(data_collector, columns=atr_name) 
              data_file_1.drop('Data URL', axis = 1, inplace=True)
              data_file_0 = pandas.concat([data_file_0, data_file_1], ignore_index=True)
      #final data
      if not  data_file_0.empty:
          return data_file_0, data_available, data_not_available
      else:
          return False , data_available, data_not_available




  #process code ---------------------------------------------------

  def  process(self):
      #validating the input data 
      validity = self.link_extractor(self.data)
      number_of_links = len(validity)

      
      if not self.link_extractor(self.data):
          return "Enter the valid url !"
      else:
          self.data = validity

      #fetching data
      data_available = []
      data_not_available = []
      final_data_frame, data_a, data_b = self.fetch_data(self.data, data_available, data_not_available)

      if not final_data_frame.empty:

          #exporting the file in the microsoft excel fromat
          #final_data_frame.to_excel(f"out_{dt_string}.xlsx", index=False)
          return(final_data_frame)
          '''
          print(f"\nNumber of valid url entered : {number_of_links}")
          print(f"\nTotal processed url : {len(data_a)}")
          print(f'\nNumber of invalid url : {len(data_b)}')
          if data_b:
              print("\n Invalid url list : ")
              for url in data_b:
                  print (url)
          print(f"\n\nFile is saves with the name out_{dt_string}.xlsx")
      else:
          print("\nNone of the urls have the data available !!")


#RUN the program  
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="flag to specify the links are put in data.txt file", action="store_true")
    args = parser.parse_args()
    if args.file:
        with open('data.txt', 'r') as fd:
            data = fd.read()
    else:
        data = input("Enter the link => ")
    process(data)
  '''
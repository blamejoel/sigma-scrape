# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 17:17:45 2016
@author: Arnaud Devie

Modified on Wed Oct 12
@author Joel Gomez
"""

#%% Data mining from Sigma Aldrich website
# Search URL by CAS number:
# http://www.sigmaaldrich.com/catalog/search?interface=CAS%20No.&term=1314-62-1&N=0&lang=en&region=US&focus=product&mode=mode+matchall
# On product page, Safety Information table, with H-statements, P-statements and PPE type

#==============================================================================
# Libraries
#==============================================================================
import re
import os
import sys
import time
import urllib
from bs4 import BeautifulSoup
from selenium import webdriver

#==============================================================================
# Functions
#==============================================================================
def deblank(text):
    # Remove leading and trailing empty spaces
    return text.rstrip().lstrip()

def fixencoding(text):
    # Make string compatible with cp437 characters set (Windows console)
    return text.encode(encoding="cp437", errors="ignore").decode(encoding="utf-8", errors="ignore")

def striphtml(text):
    # remove HTML tags from string (from: http://stackoverflow.com/a/3398894, John Howard)
    p = re.compile(r'<.*?>')
    return p.sub('', text)

def clean(text):
    # Deblank, fix encoding and strip HTML tags at once
    return striphtml(fixencoding(deblank(text)))

#==============================================================================
# Input
#==============================================================================
# Looking for info about chemical identified by CAS number ...
CASlist = list()
textfile = open('CAS-list.txt','r')
for line in textfile:
    CASlist.append(deblank(line.replace('\n','')))

textfile.close()

# Drop duplicates
CASlist = set(CASlist)

# Clean up
if '' in CASlist:
    CASlist.remove('')

# Override
#CASlist=['1120-71-4']

#%%
#==============================================================================
# Data mining Sigma Aldrich website
#==============================================================================

# Start Chrome instance
chromeOptions = webdriver.ChromeOptions()

if "SDS" not in os.listdir('.'):
    os.mkdir("SDS")

prefs = {"download.default_directory" : os.path.join(os.getcwd(),"SDS"),
         "download.prompt_for_download" : False,
         "download.directory_upgrade" : True,
         "plugins.plugins_disabled" : ["Chrome PDF Viewer"]}
chromeOptions.add_experimental_option("prefs",prefs)
chromeOptions.add_argument("--disable-extensions")

if 'win' in sys.platform: # Windows
    chromedriver = os.path.join(os.getcwd(),'chromedriver','win32','chromedriver.exe')
elif 'darwin' in sys.platform: # Mac OS
    chromedriver = os.path.join(os.getcwd(),'chromedriver','mac32','chromedriver')
elif 'linux' in sys.platform: # Linux
    if sys.maxsize > 2**32: # 64-bit
        chromedriver = os.path.join(os.getcwd(),'chromedriver','linux64','chromedriver')
    else: # 32-bit
        chromedriver = os.path.join(os.getcwd(),'chromedriver','linux32','chromedriver')

driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)
driver.set_window_position(-2000, 0)

# Initialize
chemicals=list()
CASdict = dict()
badCAS = list()

for CAS in CASlist:

    chemical = dict()
    URL = dict()
    Name = ''

    # Store CAS #
    chemical['CAS'] = CAS
    print(CAS)

    try:
        # Webscraping search page
        searchURL = r'http://www.sigmaaldrich.com/catalog/search?interface=CAS%20No.&term=[INSERT-HERE]&N=0&lang=en&region=US&focus=product&mode=mode+matchall'.replace('[INSERT-HERE]',CAS)
        webpage = urllib.request.urlopen(searchURL).read()
        soup = BeautifulSoup(webpage, "html.parser")
        product = soup.find("li", class_='productNumberValue')
        productSubURL = product.a.decode().split('"')[1]
        sds = soup.find("li", class_='msdsValue')
        pattern = '\'(\w*)\'' # any string between ''
        [country, language, productNumber, brand] = re.findall(pattern, sds.a.get('href'))
        properties = soup.find("ul", class_="nonSynonymProperties")
        formula = striphtml(properties.span.decode_contents())

        # Webscraping product page
        productURL = 'http://www.sigmaaldrich.com[INSERT-HERE]'.replace('[INSERT-HERE]', productSubURL)
        webpage2 = urllib.request.urlopen(productURL).read()
        soup2 = BeautifulSoup(webpage2, "html.parser")

        # Store URLs
        chemical['SearchURL'] = searchURL
        chemical['ProductURL'] = productURL
        chemical['ProductNumber'] = productNumber
        chemical['Brand'] = brand
        chemical['Formula'] = formula

        # Name (compatible with cp437 characters set)
        Name = clean(soup2.find("h1", itemprop="name").decode_contents().split('\n')[1])
        chemical['Name'] = Name
        CASdict[CAS] = Name
        print(Name)

        # Download SDS as PDF file
        sdsName = Name + " - SDS.pdf"
        sdsURL = os.path.join("SDS", sdsName)
        chemical['SDSfile'] = sdsURL

        if sdsName not in os.listdir('SDS'):

            driver.get("http://www.sigmaaldrich.com/MSDS/MSDS/DisplayMSDSPage.do?country=%s&language=en&productNumber=%s&brand=%s" %(country, productNumber, brand));
            # print("Downloading SDS file", end='')
            print("Downloading SDS file")

            timedout = False
            timeout = time.time()
            while ("PrintMSDSAction.pdf" not in os.listdir('SDS')) and not timedout:
                # print(".", end='')
                print(".")
                timeout = time.time() - timeout
                timedout = (timeout>30)
                time.sleep(1)

            if timedout:
                print(" Timed Out! Could not get the file")
            else:
                print(" Done.")
                os.rename(os.path.join("SDS","PrintMSDSAction.pdf"), sdsURL)

        # Store chemical
        chemicals.append(chemical)

    except:
        badCAS.append(CAS)
        print('Could not process %s - %s' % (CAS, Name))
        e = sys.exc_info()[0]

# Close Chrome instance
driver.quit()

# Display
print('Processed %d chemicals out of %d CAS numbers received' % (len(chemicals),len(CASlist)))

if len(badCAS) > 0:
    print('Unable to process the following CAS numbers:')
    for cas in badCAS: print(cas)


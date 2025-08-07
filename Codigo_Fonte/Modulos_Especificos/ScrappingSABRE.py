##### instalações

import requests
import io, re, string, os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep

##### bloco que irá enganar o cvs no site
#path = os.pathabspath(r"C:\Users\Ricardo\.wdm\drivers\chromedriver\win64\116.0.5845.188")
# path = (r"C:\Users\Ricardo\.wdm\drivers\chromedriver\win64\116.0.5845.188") # retirado temporariamente
# replacement = "ask_roepstdlwoeprolPOweos".encode()

options = Options() # sempre é utilizado
options.headless = False # executar de forma oculta ou visivel
navegador = webdriver.Chrome(options=options)
#options.add_argument('window-size=480,800')
link = "http://cae.voeazul.com.br/"

navegador.get(url=link)
sleep(2)

selectLogin = navegador.find_element(by=By.XPATH, value="/html/body/div/div/section/div[3]/div/div/div/div/section/div/div[1]/div/div/div/a")
selectLogin.click()
sleep(2)

selectLogin2 = navegador.find_element()



site = BeautifulSoup(navegador.page_source, 'html.parser')
print(site.prettify())

##### FUNCIONA VAMOS FAZER OUTROS TESTES
# link = "http://cae.voeazul.com.br/"
# headers = {"user-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"}
#
# requisição = requests.get(link, headers=headers)
# print(requisição)
# #print(requisição.text)
#
# site = BeautifulSoup(requisição.text, "html.parser")
# print(site.prettify())
#
# site.find()
from flask import Flask, request, render_template, url_for
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config.from_object(__name__)

def fifetyfive_get_shows(soup, date):
  ldate = date.split('-')
  date = ldate[1]+'/'+ldate[2]+'/'+ldate[0][-2:]
  print date
  tables = soup.findAll('table')[:-1]
  tables = [tables[i] for i in range(len(tables)) if (date in tables[i].text and i%3==0)]
  show_list = []
  for table in tables:
    time = table.findAll('font')[0].text
    time = ''.join([i for i in time if i.isdigit()])
    fin = table.findAll('font')[1].text.split('\n')
    fin = [i for i in fin if not i.isspace() and i]
    if len(fin)==0:
      group='TBA'
      musicians='TBA'
    if len(fin)==1:
      group = fin[0]
      musicians = 'TBA'
    if len(fin)>1:
      group = fin[0]
      musicians = fin[1]
      show_list.append((date,time,group,musicians))
  return show_list

@app.route('/')
def front_page():
  return render_template('front.html')

@app.route('/<date>')
def shows(date):
  ff = requests.get('http://www.55bar.com/cgi-bin/webdata_playinPrint.pl?cgifunction=Search&GigDate=%3E%3D10/17/2015')
  ff = BeautifulSoup(ff.text, 'html.parser')  
  show_list = fifetyfive_get_shows(ff, date)
  return render_template('cal.html', show_list=show_list)

if __name__ == '__main__':
  app.run(debug=True)

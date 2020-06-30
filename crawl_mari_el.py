#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request    
import os
import datetime 
from os import path
from datetime import date
from html.parser import HTMLParser
import re
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

start_date = date(2020, 4, 1)
work_dir = "mari_el"
stc = "stopcorona"

class daily_stats:
    def __init__(self, total):
        self.total = total
        self.confirmed = -1
    def __str__(self):
        return "{} {}".format(self.total, self.confirmed)

def dump_page(url, name, work_dir):
    try:
        urllib.request.urlretrieve(url, os.path.join(work_dir,name)+".html")
        print ("{} found!".format(name))
    except:
        print ("{} not found!".format(name))

def create_mari_name(date, id):
    res = '{:%Y%m%d}_{}'.format(date,str(id)) 
    return res

def create_mari_url(date, id):
    prefix = "http://mari-el.gov.ru/minzdrav/Pages/"
    res = prefix + '{:%y%m%d}_{}.aspx'.format(date,str(id)) 
    return res

def download_mari_el(start_date): 
    curdate = start_date
    if not path.isdir(work_dir):
        os.mkdir (work_dir)
    while curdate < date.today():
        print (curdate)     
#        exit()
        curdate = curdate + datetime.timedelta(1)
        for id in range (1, 10):
            name = create_mari_name (curdate, id)
            url = create_mari_url (curdate, id)
            dump_page(url, name, work_dir)
#urllib.request.urlretrieve("http://mari-el.gov.ru/minzdrav/Pages/200619_1.aspx", "test.txt")
#run_mari_el()
class MyHTMLParser(HTMLParser):    
    res = []
    def handle_data(self, data):
        self.res.append(data)

    def clear(self):
        self.res = []

def parse_active():
    res = {}
    for f in ['infected.tsv', 'died.tsv', 'recovered.tsv']:
        lines = open(path.join(stc,f), "r").readlines()
        spl = []
        for line in lines:
            spl.append(line.split('\t'))
        datex = spl[0][1].split('.')
#        curdate = date.strptime(spl[0][1], "%d.%m.%Y")
        curdate = date(int(datex[2]), int(datex[1]), int(datex[0]))
        for i in range (0, len(spl)):
            if (spl[i][0] == "Республика Марий Эл"):
                for j in range(1, len(spl[i])):
                    if f == "infected.tsv":
                        res[curdate] = int(spl[i][j])
                    else:
                        res[curdate] -= int (spl[i][j])
                    curdate = curdate -datetime.timedelta(1)         
                    if curdate < start_date:
                        break
    return res
def parse_mari_el():
    parsed_by_date = {}
    curdate = start_date
    parser = MyHTMLParser()

    for f in os.listdir (work_dir):       
        parser.clear()
        fdate = f.split("_")[0]
        parser.feed(open(os.path.join(work_dir,f), "r").read())            
        parsed = False

        test = re.compile("Всего в инфекционных стационарах республики ")
        for line in parser.res:            
            if test.search(line):
                numbers = re.findall('\d+', line)
                st = daily_stats(numbers[0])
                shift = 0
                if (line.find("пневмо"))!= -1:
                    shift += 1
                st.confirmed = numbers[1+shift]
                st.heavy = numbers[2 + shift]
                st.medium = numbers[3 + shift]
                st.light = numbers[4 + shift]
                parsed = True
                parsed_by_date[fdate] = st
#IVL oxigen
        if parsed:
            continue
#        test = re.compile("в инфекционных стационарах республики  с коронавирусной инфекцией и с подозрением на коронавирусную инфекцию находится \d+ человек.")
        test = re.compile("в инфекционных стационарах республики  с")
#        test = re.compile("с подтвержденной")        
#На утро 20  июня  в инфекционных стационарах республики  с коронавирусной инфекцией и с подозрением на коронавирусную инфекцию находится 632 человека.  В тяжелом состоянии – 162 пациента, в состоянии средней степени тяжести – 467, легкой степени тяжести – 3. На искусственной вентиляции легких - 18. В кислородной поддержке  нуждаются 242.
        for line in parser.res:            
            if test.search(line):
                                
                numbers = re.findall('\d+', line)
                st = daily_stats(numbers[1])
#                print (numbers)
                st.heavy = numbers[2]
                st.medium = numbers[3]
                st.light = numbers[4]

                if len(numbers) == 7:
                    st.ivl = numbers[5]
                    st.oxygen = numbers[6]
                parsed_by_date[fdate] = st
        if parsed:
            continue
        test = re.compile ("сего .* стационарах республики .* \d+ пациентов")
        for line in parser.res:            
            if test.search(line):
                print(line)
        test = re.compile("- леч.тся в инфекционных стационарах республики")
        for line in parser.res:            
            if test.search(line):
                st = daily_stats(re.findall('\d+', line)[0])
                parsed_by_date[fdate] = st
#260 - с подтвержденной коронавирусной инфекцией;
        test = re.compile("\d+ - с подтвержденной коронавирусной инфекцией;")
        for line in parser.res:  
          
            if test.search(line):
                if fdate in parsed_by_date:
                    parsed_by_date[fdate].confirmed = re.findall('\d+', line)[0]
                else:
                    print (line)
                    print (fdate)
                    exit()
       
#                print (line)
    active = parse_active()
    x=[]
    xk = []
    y=[]
    confirmed = []
    while curdate < date.today():
        date_str = '{:%Y%m%d}'.format(curdate)
        if date_str not in parsed_by_date:
            curdate = curdate
#            print (date_str)
#            print (parsed_by_date[date_str])
#            print (re.findall('\d+', parsed[date_str]))
        else:
            x.append(curdate)
            y.append(int(parsed_by_date[date_str].total))
            if parsed_by_date[date_str].confirmed != -1:
                xk.append(curdate)
                confirmed.append(int(parsed_by_date[date_str].confirmed))
            print ('{} {} {}'.format(date_str, parsed_by_date[date_str], active[curdate]))
        curdate = curdate + datetime.timedelta(1)
#    plt.yticks(np.arange(0, 700, 50)) 
#    plt.xticks(np.arange(x[0], x[-1], datetime.timedelta(5))) 
    active_to_graph = []
    active_dates = []
    curdate = x[0]
    while curdate <= date.today():
        active_to_graph.append(active[curdate])
        active_dates.append(curdate)
        curdate = curdate + datetime.timedelta(1)
    ticks_to_use = x[::10]
    labels = [ i.strftime("%d.%m") for i in ticks_to_use ]
    ax = plt.gca()
    ax.set_xticks(ticks_to_use)
    ax.set_yticks(np.arange(0, 701, 50))
    ax.set_xticklabels(labels)
    ax.set_ylim(bottom=0)
    plt.plot(x, y)
    plt.plot(xk, confirmed)
    plt.plot(active_dates, active_to_graph)
    blue_patch = mpatches.Patch(color='blue', label='В ковидных больницах')
    orange_patch = mpatches.Patch(color='orange', label='из них с подтвержденным ковидом')
    green_patch = mpatches.Patch(color='green', label='Активных случаев\nпо роспотребнадзору')
    plt.legend(handles=[blue_patch,orange_patch,green_patch])
    plt.title("Коронавирус в Марий Эл")
#    plt.legend()
    plt.show()
    return parsed_by_date
#download_mari_el(date.today() - datetime.timedelta(5))        
parse_mari_el()
'''
    if line.find('пневмо')!= -1:
        print(line)
'''

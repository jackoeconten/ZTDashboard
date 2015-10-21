#!/usr/bin/env python
# coding: utf8
#---------------------------------------------------------------------------------
from couchdbkit import *
from bs4 import BeautifulSoup
from dateutil.parser import parser as dateutil_parser
import datetime
import feedparser
import html2text
#---------------------------------------------------------------------------------
feedRSS = ""
dbName = "feeds"
urlfeedrss = list()
urlCatFeedrss = list()
fluxRSS = list()

compteurfeedRSS = 0
cptfeedRSSrestant = 1
#---------------------------------------------------------------------------------
def get_href(links, _type='text/html'):
    filtered = filter(lambda ln: ln.get('type') == _type, links)
    return len(filtered) and filtered[0].get('href') or None

parse_date = dateutil_parser().parse

def coerce_date_str(date_str):
    parsed = parse_date(date_str)
    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")
#---------------------------------------------------------------------------------
# server object
server = Server()
# create database
db = server.get_or_create_db(dbName)
# #---------------------------------------------------------------------------------
#                                 Lecture fichier OPML
# #---------------------------------------------------------------------------------
soup = BeautifulSoup(open("/home/jackoeconten/ZTDashboard/feedlist.opml"), "xml")

for link in soup.find_all('outline'):
    if link.get('type') == "folder":
        catfeedrss = link.get('title')
    if link.get('type') == "rss":
        feedRSS = link.get('xmlUrl')
        urlfeedrss.append(feedRSS)
        urlCatFeedrss.append(catfeedrss + ' : ' + feedRSS)
        compteurfeedRSS += 1
# #---------------------------------------------------------------------------------
#                     Traitement sur les flux RSS
# #---------------------------------------------------------------------------------
#for feed in urlfeedrss:
        traitement = 1
        try:
            blobRSS = feedparser.parse(feedRSS)
        except:
            print("erreur sur le flux : " + feedRSS + '----------------------------------------------------------')
            traitement = 0

        print(str(cptfeedRSSrestant) + ' / ' + str(compteurfeedRSS))

        cptfeedRSSrestant += 1

        if traitement == 1:
            for post in blobRSS.entries:
                try:
                    content = post.content[0].get('value')
                except:
                    content = post.summary_detail.get('value')
                doc = {'title':     hasattr(post, 'title') and post.title or '',
                        'href':         hasattr(post, 'links') and get_href(post.links) or '',
                        'updated':      hasattr(post, 'title') and post.updated,
                        'date':         coerce_date_str(post.updated),
                        'author':       hasattr(post, 'author') and post.author or '',
                        'content':      content,
                        'feedCategory': catfeedrss}

                db.save_doc(doc)

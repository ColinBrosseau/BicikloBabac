# -*- coding: utf-8 -*-
#
# Copyright © 2011 Colin-Nadeau Brosseau
# GNU General Public License version 2
# (see Licence.txt for details)

"""
Created on Apr 27 2012

Developped and maintained by Colin-N. Brosseau

Copyright © 2012 Colin-Nadeau Brosseau
GNU General Public License version 2
(see Licence.txt for details)
"""


#temps total travaillé
# 7:00


from bs4 import BeautifulSoup
import urllib
import urllib2

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

base_url = 'http://cyclebabac.com'

class BabacItem:
    """
    Represente un item de Babac
    """
    def __init__ (self, soup):
        self.soup = soup
        self.categorie = self.get_category()
        self.no_babac = self.get_no_babac()
        self.title = self.get_title()
        self.description1 = self.get_description1()
        self.description2 = self.get_description2()

    def __str__ (self):
        desc_longue = ''.join(self.description2)

        return 'Categorie: %s \n'% self.categorie + \
            '# Babac: %s \n' % self.no_babac + \
            'Nom: %s \n'% self.title + \
            'Description: %s \n' % self.description1 + \
            'Description longue:%s' % desc_longue
               #'Description: %s \n' % (unicode(self.description1).encode('utf-8')) + \
        # return 'Categorie: %s \n'% self.categorie.encode('ascii', 'ignore') + '# Babac: %s \n' % self.no_babac + \
        #        'Nom: %s \n'% self.title.encode('ascii', 'ignore') + \
        #        'Description: %s \n' % self.description1.encode('ascii', 'ignore') + \
        #        'Description longue:%s' % desc_longue.encode('ascii', 'ignore')
    
    def get_title(self):
        """
        Nom de la piece
        """
        title = []
        title.append(self.soup.title.string)
        #print(title)
        return title[0]
        #print(soup.head.meta)

    def get_description1(self):
        """
        Description courte
        """
        description = ""
        for i in self.soup.find_all('meta'):
            if i.has_key('name'):
                if i['name'] == 'description':
                    #print i
                    #print ''.join(i['content'].split())
                    #description.append(i['content'].replace('\n', '').replace('* ', ''))
                    description += i['content'].replace('\n', '').replace('* ', '')
                    #description.append(''.join(i['content'].split()))
        #print "description"
        #print description
        #print unicode(description).encode('utf-8')
        return description

    def get_no_babac(self):
        """
        Numero de pièce Babac
        """
        l =  self.soup.find_all('td', style='text-align:left; padding-left: 10px; padding-bottom:5px; font-size: 12px;')
        k = []
        for i in l:
            #print i.attrs #for testing
            for s in i.strings:
                #print s.find('Ref.: ')
                if s.find('Ref.: ') >= 0:
                    #print s
                    #print ' & '
                    k.append((''.join(s.split())).replace('Ref.:', ''))
        #print k
        try: 
            return k[0]
        except: # ce cas se presente quand une categorie est vide (exemple pour les speciaux)
            pass

    def get_category(self):
        """
        Categorie de piece
        """
        categorie = []
        j = 0
        for i in self.soup.find_all('a'):
            if i.has_key('class'):
                if i['class'] == ['pathway']:
                    j += 1
                    if j == 3:
                        #print i
                        #print i.attrs
                        #print i.string
                        categorie.append(i.string)
        #print categorie
        try:
            return categorie[0]
        except: # ce cas se presente quand une categorie est vide (exemple pour les speciaux)
            pass

    def get_description2(self):
        """
        Description longue
        """
        k = []
        for i in self.soup.find_all('div', style='border:1px solid #BBBBBB; margin-bottom: 1em; padding: 10px'):
            k = []
            for s in i.strings:
                k.append(s)
        Desc_fr = []
        previous = False
        anglais = True
        for i in k:
            #print i
            current = (i[0] == '*')
            if not(current) and previous and anglais:
                anglais = False

            if not(anglais) and current:
                Desc_fr.append(i.replace('* ', ''))

            previous =  current
        #print Desc_fr
        return Desc_fr

def scan_categorie(url): 
    values = {'name' : 'Biciklo',
          'location' : 'Montreal',
          'language' : 'fr' }

    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    page = response.read()
    SOUP = BeautifulSoup(page)

    #print(SOUP)

    print('+-+-+-+-+-+-+-+')


#    url = 'http://cyclebabac.com/index.php?option=com_virtuemart&page=shop.browse&category_id=33&Treeid=40&Itemid=59&vmcchk=1&Itemid=53' 
#    url = 'http://cyclebabac.com/index.php?option=com_virtuemart&page=shop.browse&category_id=67&Treeid=63&Itemid=53&vmcchk=1&Itemid=53'
#    req = urllib2.Request(url, data)
#    response = urllib2.urlopen(req)
#    page = response.read()
#    SOUP = BeautifulSoup(page)

    #l =  SOUP.find_all('h3', class = 'browseProductTitle')
    l =  SOUP.find_all('h3')
    for i in l:
        if i.has_key('class'):
            if i['class'] == ['browseProductTitle']:
                #print i
                #print i['href']
                #print i.attrs
                #print i.string
                for j in i.find_all('a'):
                    #print j
                    #print j.attrs
                    #print j.string
                    #print j['href']
                    url = base_url + j['href'].replace('en','fr').replace('our-store','magasin')
                    #print url
                    req = urllib2.Request(url, data)
                    response = urllib2.urlopen(req)
                    page = response.read()
                    SOUP = BeautifulSoup(page)
                    print BabacItem(SOUP)
                    print '--'

def scan_front_page():
    url = base_url + '/'
    values = {'name' : 'Biciklo',
          'location' : 'Montreal',
          'language' : 'fr' }
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    page = response.read()
    SOUP = BeautifulSoup(page)

    l =  SOUP.find_all('script')
    for i in l:
        a = str(i.string)
        if a.find('var TREE_ITEMS') >= 0:
            #print a
            for i in a.splitlines():
                to_find = 'href='
                j = i.find(to_find)
                if j >= 0:
                    #print  i[j+len(to_find)+2:-3]
                    url_categorie = url + i[j+len(to_find)+2:-3] + '&limitstart=0&limit=1000'
                    #print url_categorie
                    scan_categorie(url_categorie)
    
if __name__ == "__main__":

    #url = 'http://cyclebabac.com/index.php?option=com_virtuemart&page=shop.browse&category_id=67&Treeid=63&Itemid=53&vmcchk=1&Itemid=53'
    #                              index.php?option=com_virtuemart&page=shop.browse&category_id=3&Treeid=1&Itemid=1

    #scan_categorie(url)
                    
    scan_front_page()

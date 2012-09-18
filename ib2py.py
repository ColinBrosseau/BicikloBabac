# -*- coding: utf-8 -*-
#
# Copyright © 2011 Colin-Nadeau Brosseau
# GNU General Public License version 2
# (see Licence.txt for details)

"""
Created on Sep 2011
Developped and maintained by Colin-N. Brosseau

Copyright © 2011 Colin-Nadeau Brosseau
BSD Licence
(see LICENCE.txt for details)
"""

#Pour la comptabilite du temps de travail pour Biciklo
#temps total travaillé
# 6:30

#limites de lecture: un peu crapy mais ca fonctionne A ADAPTER A CHAQUE FOIS
max_line_PIECES = 535
max_line_CAISSE = 910
max_item = 9450

import sys
import datetime


import xlrd #pour lire le fichier excel
import xlwt #pour ecrire dans le fichier excel
import xlutils.copy

import numpy as np

#represente un objet de l'atelier
class item(object):
    """
    Defini un objet de l'atelier: numero, caracteristiques, nombre en inventaire, etc.	
    """
    def __init__(self,numero,section,piece,reference,caracteristique,metal,quantite_neuf,prix_neuf,quantite_usage,prix_usage,remarques,no_babac):
        if numero is None:
            pass
        else:
            self.numero = np.int(numero)
            self.section = section.encode('utf8')
            self.piece = piece.encode('utf8')
            self.reference = reference.encode('utf8')
            try:
                self.caracteristique = caracteristique.encode('utf8')
            except AttributeError:
                self.caracteristique = str(caracteristique)
            self.metal = metal.encode('utf8')
            self.quantite_neuf = np.float(quantite_neuf)
            try:
                self.prix_neuf = np.float(prix_neuf)
            except ValueError:
                self.prix_neuf = 0
                
            self.quantite_usage = np.float(quantite_usage)
            try:
                self.prix_usage = np.float(prix_usage)
            except ValueError:
                self.prix_usage = 0
            self.remarques = remarques.encode('utf8')
            try:
                self.no_babac = no_babac.encode('utf8')
            except AttributeError:
                self.no_babac = ''
            self.ventes_neuf = 0
            self.ventes_usage = 0
            self.calcul_ratio()

    #compte une vente de l'objet neuf
    def add_vente_neuf(self,ajout=0):
        try:
            self.ventes_neuf += ajout
            self.calcul_ratio()
        except TypeError:
            pass

    #compte une vente de l'objet usage
    def add_vente_usage(self,ajout=0):
        try:
            self.ventes_usage += ajout
            self.calcul_ratio()
        except TypeError:
            pass

    #calcul des ratios vente/inventaire pour neuf et usage
    def calcul_ratio(self):
        try:
            self.ratio_neuf = self.ventes_neuf / self.quantite_neuf
        except ZeroDivisionError:
            self.ratio_neuf = self.ventes_neuf
 
        try:
            self.ratio_usage = self.ventes_usage / self.quantite_usage
        except ZeroDivisionError:
            self.ratio_usage = self.ventes_usage  

    #utile pour print(self)
    def __str__(self):
      	#return 'R:%.1f;'%self.ratio_neuf  + '  ' + 'V:%.0f;%.0f;'%(self.ventes_neuf,self.ventes_usage,)  + '  '  + 'I:%.0f;%.0f;'%(self.quantite_neuf,self.quantite_usage,) + '\t' + '%2.2f;$'%self.prix_neuf   + '\t' +  str(self.numero) + ';\t' +  'Ba:' + str(self.no_babac) + ';\t'  + str(self.section) + ';\t' + self.piece + ';\t' + self.reference + ';\t' + self.caracteristique + ';\t' + self.metal + ';\t'  + str(self.remarques) + ';'
    	return '%.1f;'%self.ratio_neuf  + '%.0f;%.0f;'%(self.ventes_neuf,self.ventes_usage,)  + '%.0f;%.0f;'%(self.quantite_neuf,self.quantite_usage,) + '%2.2f;'%self.prix_neuf   +  str(self.numero) + ';' +  str(self.no_babac) + ';'  + str(self.section) + ';' + self.piece + ';' + self.reference + ';' + self.caracteristique + ';' + self.metal + ';'  + str(self.remarques) + ';'

    def __repr__(self):
        return str(self.numero) + '\t' + self.piece + '\t' + str(self.prix_neuf) + '$'   + '\t'  + str(self.ratio_neuf)

    
#lit la feuille des ventes
#regarder comment on traite le temps
def lire_caisse(wb):
    CAISSE = wb.sheet_by_name(u'CAISSE')
    
    #indice maximum pieces
    c0CAISSE = np.array(CAISSE.col_values(0,1,max_line_CAISSE))
    #c8CAISSE = np.array(CAISSE.col_values(8,1,max_line_CAISSE))
    c8CAISSE = CAISSE.col_values(8,1,max_line_CAISSE)
    c2CAISSE = CAISSE.col_values(2,1,max_line_CAISSE)
    
    #converti en bonnes unitees de temps
    for i in range(len(c8CAISSE)):
        print(i)
        year, month, day, hour, minute, second = xlrd.xldate_as_tuple(c8CAISSE[i],1)
        c8CAISSE[i] = date2num(datetime.datetime(year, month, day, hour, minute,second))
      
    return c0CAISSE, c8CAISSE, c2CAISSE
    
def classe_caisse(c0,c8):
    n1 = np.empty((12,max_item+1))
    for i in range(len(c0)):
        objet = c0[i]
        date = num2date(c8[i])
        print objet, date
        if date:
            n1[date.month-1,objet] += 1
        else:
            print "Ligne %d sans date. Ignorée..." % i
    
    return n1
    
def plot_item(n,d,item=100):
    from matplotlib.dates import YearLocator, MonthLocator, WeekdayLocator, DateFormatter
    from matplotlib.dates import epoch2num, date2num, num2date
    import matplotlib.pyplot as plt #pour les graphiques

    hist = list(n[:,item])
    bin_edges = np.empty(12+1)
    for i in range(0,12):
        bin_edges[i] = date2num(datetime.date( 2011, i+1, 1 ))
    bin_edges[12] = date2num(datetime.date( 2012, 1, 1 ))
    #(hist, bin_edges) = numpy.histogram(dates, bins)
        
    
    width = bin_edges[1] - bin_edges[0]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(bin_edges[:-1], hist , width=width)
    #ax.bar(bin_edges[:-1], hist / width, width=width)
    
    date_debut = datetime.date( 2011, 1, 1 )
    date_fin = datetime.date( 2011, 12, 31 )
    ax.set_xlim(date_debut, date_fin)
    #ax.set_xlim(bin_edges[0], num_now())
    
    
    # set x-ticks in date
    # see: http://matplotlib.sourceforge.net/examples/api/date_demo.html
    ax.xaxis.set_major_locator(MonthLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%b'))
    ax.xaxis.set_minor_locator(WeekdayLocator())
    # format the coords message box
    ax.format_xdata = DateFormatter('%Y-%m-%d')
    ax.grid(True)
    
    ax.set_title(d[item])
    fig.autofmt_xdate()
    plt.show()
    
def gros_vendeur(n):
    #    #classe les items en ordre des ventes decroissantes
    total_ventes = sum(n);
    return total_ventes.argsort()

def num_now():
    """
    Return the current date in matplotlib representation
    """
    return date2num(datetime.datetime.now())


def get_limit(past):
    """
    Get the date `past` time ago as the matplotlib representation
    """
    return num_now() - float(past) * 365


def read_dates(limit, stream=sys.stdin):
    """
    Read newline-separated unix time from stream
    """
    dates = []
    for line in stream:
        num = epoch2num(float(line.strip()))
        print num
        dates.append(num)
        if num < limit:
            break
    stream.close()
    return dates

def plot_datehist(dates, bins, title=None):
    (hist, bin_edges) = np.histogram(dates, bins)
    print bin_edges
    width = bin_edges[1] - bin_edges[0]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(bin_edges[:-1], hist , width=width)
    #ax.bar(bin_edges[:-1], hist / width, width=width)
    
    date_debut = datetime.date( 2011, 1, 1 )
    date_fin = datetime.date( 2011, 12, 31 )
    ax.set_xlim(date_debut, date_fin)
    #ax.set_xlim(bin_edges[0], num_now())
    
    #ax.set_ylabel('Events [1/day]')
    if title:
        ax.set_title(title)

    
    # set x-ticks in date
    # see: http://matplotlib.sourceforge.net/examples/api/date_demo.html
    #ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_major_locator(MonthLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%b'))
    ax.xaxis.set_minor_locator(MonthLocator())
    # format the coords message box
    ax.format_xdata = DateFormatter('%Y-%m-%d')
    ax.grid(True)

    fig.autofmt_xdate()
    return fig

def lire_inventaire(PIECES):
    inventaire = {}
    #parcour le fichier inventaire pour creer toutes les pieces
    for i in range(1,max_line_PIECES):
        numero = PIECES.cell(rowx=i,colx=0).value
        section = PIECES.cell(rowx=i,colx=1).value
        piece = PIECES.cell(rowx=i,colx=2).value
        reference = PIECES.cell(rowx=i,colx=3).value
        caracteristique = PIECES.cell(rowx=i,colx=4).value
        metal = PIECES.cell(rowx=i,colx=5).value
        prix_neuf = PIECES.cell(rowx=i,colx=6).value
        #prix_neuf = 0.0
        quantite_neuf = PIECES.cell(rowx=i,colx=7).value
        quantite_usage = PIECES.cell(rowx=i,colx=9).value
        prix_usage = PIECES.cell(rowx=i,colx=10).value
        remarques = PIECES.cell(rowx=i,colx=11).value
        no_babac = PIECES.cell(rowx=i,colx=13).value

        a = item(numero,section,piece,reference,caracteristique,metal,quantite_neuf,prix_neuf,quantite_usage,prix_usage,remarques,no_babac)
        print(a)

        inventaire[numero] = a
    return inventaire

def compile_ventes(inventaire,CAISSE):
    #parcour le fichier caisse pour compiler les ventes
    for i in range(1,max_line_CAISSE):
        #i = 1
        numero = CAISSE.cell(rowx=i,colx=0).value   
        #print inventaire[numero]
        qte_neuf = CAISSE.cell(rowx=i,colx=2).value    
        qte_usage = CAISSE.cell(rowx=i,colx=4).value
        inventaire[numero].add_vente_neuf(qte_neuf)
        inventaire[numero].add_vente_usage(qte_usage)
        #print inventaire[numero]

    return inventaire


#rb    open_workbook('source.xls',formatting_info=True)
#rs    rb.sheet_by_index(0)                            
#wb    copy(rb)                                        
#ws    wb.get_sheet(0)                                 


if __name__ == "__main__":
    
    #lit la feuille
    #-------------------------------------------
    # LIGNE A CHANGER A CHAQUE FOIS
    #-------------------------------------------
    rb = xlrd.open_workbook('INVENTAIRE_2012.xls')

    PIECES = rb.sheet_by_name(u'PIÈCES')
    inventaire = lire_inventaire(PIECES)
 
    CAISSE = rb.sheet_by_name(u'CAISSE')
    inventaire = compile_ventes(inventaire,CAISSE)

    #classe les items en ordre croissant du ratio vente/inventaire
    for key in sorted(inventaire, key = lambda numero: inventaire[numero].ratio_neuf):
        print inventaire[key]
    
    #parcours le fichier inventaire pour y ecrire le ratio vente/inventaire
    #for i in range(1,max_line_PIECES):
    #ws.write(1,12,'test123')


  
#    from optparse import OptionParser
#    parser = OptionParser(usage='PRINT_UNIX_TIME | %prog [options]')
#    parser.add_option("-p", "--past", default="1",
#                      help="how many years to plot histogram. (default: 3)")
#    parser.add_option("-o", "--out", default=None,
#                      help="output file. open gui if not specified.")
#    parser.add_option("-b", "--bins", default=30, type=int,
#                      help="number of bins for histogram. (default: 30)")
#    parser.add_option("-t", "--title")
#    parser.add_option("-d", "--doc", default=False, action="store_true",
#                      help="print document")
#    (opts, args) = parser.parse_args()
#
#    if opts.doc:
#        print __doc__
#
#    #dates = list(epoch2num(c8))
#    dates = list(c8)
#    fig = plot_datehist(dates, opts.bins, title=opts.title)
#    pyplot.show()

    
#    d, n1 = charger()
#    
#    #totaux des ventes pour chaque item
#    total_ventes = sum(n1);
#    #
#    #classe les items en ordre des ventes decroissantes
#    I = total_ventes.argsort()
#            
#    #determine l'objet le plus vendu
#    gros_vendeur = I[-1]
#    
#    #plot du gros vendeur
#    x = np.arange(12)+1
#    for i in range(-10,-20,-1):
#        print i, n1[:,I[i]], d[I[i]]
#        plt.plot(x,n1[:,I[i]],'o:', label=d[I[i]])
#    plt.xlabel('mois')
#    plt.title("Biciklo")
#    plt.legend()
#    plt.show()
#    
    
    
# #ancienne fonction servant a lire l'inventaire existant   
# def lire_pieces(wb):
#     PIECES = wb.sheet_by_index(0)
    
#     #indice maximum pieces
#     first_column = PIECES.col_values(0,1,max_line_PIECES)
    
#     #max_item = max(first_column)
#     #max_item = 9450

#     #construit un dictionnaire liant le numero de l'item et sa description
#     d = {100:'ABONNEMENT_1 MOIS'}
#     for rownum in range(max_line_PIECES):
#         print PIECES.cell(rowx=rownum+1,colx=0).value
#         #vérifie si les champs sont valides
#         a1 = PIECES.cell(rowx=rownum+1,colx=2).value
#         if a1:        
#             if isinstance(a1,int):
#                 a1 = str(a1)
#             print a1
#         else:
#             a1 = ""
#         a2 = PIECES.cell(rowx=rownum+1,colx=3).value
#         if a2:        
#             if isinstance(a2,int):
#                 a2 = str(a2)
#             print a2
#         else:
#             a2 = ""
#         a3 = PIECES.cell(rowx=rownum+1,colx=4).value
#         if a3:        
#             if isinstance(a3,(int,float)):
#                 a3 = str(a3)
#             print a3
#         else:
#             a3 = ""
#         print a3.__class__
#         a4 = PIECES.cell(rowx=rownum+1,colx=5).value
#         if a4:        
#             if isinstance(a4,int):
#                 a4 = str(a4)
#             print a4
#         else:
#             a4 = ""
#         d[PIECES.cell(rowx=rownum+1,colx=0).value] = a1 + " " + a2 + " " + a3 + " " + a4

#         print ' '
#     return d
    
    

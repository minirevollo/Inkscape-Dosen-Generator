#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: mini@revollo.de
member of the erfindergarden

Inkscape Erweiterung - Dosen Generator
13.01.2019

Danke an neon22    https://github.com/Neon22/inkscape_extension_template
Nach seiner Anleitung konnte ich dieses Programm erstellen.

'''

import inkex       # Required
import simplestyle # will be needed here for styles support
from random import randint 
from math import *


__version__ = '0.2'

inkex.localize()

def points_to_svgd(p, close = True):
    """ convert list of points (x,y) pairs
        into a closed SVG path list
    """
    f = p[0]
    p = p[1:]
    svgd = 'M %.2f,%.2f ' % f
    for x in p:
        svgd += ' %.4f,%.4f' % x
    if close:
        svgd += 'z'
    return svgd
   
def punkte_erstellen(punkte, x, y):
    ###Schreibt die aktuellen Koordinaten in die Punkteliste
    
    punkte.append((x, y))



### Your main function subclasses the inkex.Effect class

class Dose(inkex.Effect): 
    ###Erstellt die Dose.
    
    def __init__(self):
        " define how the options are mapped from the inx file "
        inkex.Effect.__init__(self) # initialize the super class
        
            
        # Define your list of parameters defined in the .inx file
        self.OptionParser.add_option("", "--hoehe",
                                     action="store", type="int",
                                     dest="hoehe", default = 50,
                                     help="Höhe der Dose")
        
        self.OptionParser.add_option("", "--ueberstand",
                                     action="store", type="int",
                                     dest="ueberstand", default = 40,
                                     help="Überstand des Deckels")
        
        
        self.OptionParser.add_option("", "--durchmesser",
                                     action="store", type="int",
                                     dest="durchmesser", default = 40,
                                     help="Durchmesser der Dose")
        
        self.OptionParser.add_option("", "--winkel",
                                     action="store", type="float", 
                                     dest="winkel", default = 22.5,
                                     help="Winkel der Segmente")
        
        self.OptionParser.add_option("", "--material",
                                     action="store", type="float", 
                                     dest="material", default = 3.6,
                                     help="Materialstärke")
        
        self.OptionParser.add_option("", "--boden",
                                     action="store", type="inkbool", 
                                     dest="boden", default = False,
                                     help="Deckel und Boden?")
        
        # here so we can have tabs - but we do not use it directly - else error
        self.OptionParser.add_option("", "--active-tab",
                                     action="store", type="string",
                                     dest="active_tab", default='title', # use a legitmate default
                                     help="Active tab.")
        
        
        self.deckel_punkte = []
        self.deckel_pfad = []
        self.seite_punkte = []
        self.seite_pfad = []
        self.ausschnitt_punkte = []
        self.ausschnitt_pfad = []
        self.ausschnitt_nummer = 0
        self.einschnitt_punkte = []
        self.einschnitt_pfad = []
        self.einschnitt_nummer = 0
        self.einschnitt_breite = 0.2 #Abstand zwischen den beiden Einschnittlinien
    
   
        
    def pfad_erstellen(self, pfad, punkte):        
        # Die gesammelten x und y Koordinaten der Punkte werden in Pfade (d) umgewandelt.  
        
        pfad.append(points_to_svgd(punkte))
        del punkte[:]
    
    def pfade_schreiben(self):
        ###Schreibt alle Pfade nacheinander in die Szene
         
        path_stroke = '#101010'  # Farbe für die Dose
        path_fill   = 'none'     # keine Füllung, nur eine Linie
        path_stroke_width  = '0.4' # can also be in form '0.6mm'
        
        for nummer in range(len(self.pfade)):
            # define style using basic dictionary
            pfad_attribute = {'id': "pfad%d"%nummer, 'stroke': path_stroke,
                              'fill': path_fill, 'stroke-width': path_stroke_width,
                              'd': self.pfade[nummer]}
            # add path to scene                
            pfad = inkex.etree.SubElement(self.topgroup, inkex.addNS('path','svg'), pfad_attribute )
    
    def deckel_erstellen(self):
        ###Erstellt alle Punkte für den Aussenkreis des Deckels.
        winkel = self.winkel
        
        segmente = int(360 / winkel)
        for segment_nr in range(segmente + 1):
            #y berechnen = Gegenkathete
            y = sin(radians(winkel)) * self.radius_mit_ueberstand * -1
            #Innenwinkel berechnen
            beta = 180 - 90 - winkel
            #Ankathete berechnen
            b = sin(radians(beta)) * self.radius_mit_ueberstand
            #x berechnen
            x = self.radius_mit_ueberstand - b - self.ueberstand
            punkte_erstellen(self.deckel_punkte, x, y)
            winkel += self.winkel
        self.deckel_schreiben()
    
    def deckel_schreiben(self):
        ###Schreibt den Deckel ohne Ausschnitte in die Szene
         
        path_stroke = '#0000ff'  # Farbe für den Rand
        path_fill   = 'none'     # keine Füllung, nur eine Linie
        path_stroke_width  = '0.6' # can also be in form '0.6mm'
        #Punkte zu Pfad umwandeln
        self.deckel_pfad = points_to_svgd(self.deckel_punkte, False)
        
        # define style using basic dictionary
        deckel_attribute = {'id': "rand", 'stroke': path_stroke, 'fill': path_fill,
                          'stroke-width': path_stroke_width , 'x': '0', 'y': '0', 'd': self.deckel_pfad}
        # add path to scene                
        deckel = inkex.etree.SubElement(self.topgroup, inkex.addNS('path','svg'), deckel_attribute )
    
    def ausschnitt_erstellen(self):
        ###Erstellt alle Punkte für den Aussenkreis des Deckels.
        
        winkel = self.winkel
        
        for segment_nr in range(self.segmente):
            
            ###Punkt 1 wird berechnet
            #y berechnen = Gegenkathete
            y = sin(radians(winkel)) * self.radius * -1
            #Innenwinkel berechnen
            beta = 180 - 90 - winkel
            #Ankathete berechnen
            b = sin(radians(beta)) * self.radius
            #x berechnen
            x = self.radius - b 
            punkte_erstellen(self.ausschnitt_punkte, x, y)
            winkel += self.winkel
              
            ###Punkt 2 wird berechnet
            #y berechnen = Gegenkathete
            y = sin(radians(winkel)) * self.radius * -1
            #Innenwinkel berechnen
            beta = 180 - 90 - winkel
            #Ankathete berechnen
            b = sin(radians(beta)) * self.radius
            #x berechnen
            x = self.radius - b 
           
            punkte_erstellen(self.ausschnitt_punkte, x, y)            
                       
            ###Punkt 3 wird berechnet
            
            alpha = winkel - (self.winkel / 2)
            beta = 180 - 90 - alpha
            y += sin(radians(alpha)) * self.material
            x += sin(radians(beta)) * self.material
            winkel += self.winkel
            punkte_erstellen(self.ausschnitt_punkte, x, y)  
            
            ### Punkt 4 wird berechnet
            alpha = 180 - alpha
            beta = 180 - 90 - alpha
            x -= sin(radians(alpha)) * self.ausschnitt_breite
            y -= sin(radians(beta)) * self.ausschnitt_breite
            punkte_erstellen(self.ausschnitt_punkte, x, y)
            #
            self.ausschnitt_schreiben()
            del self.ausschnitt_punkte[:]
            
    def ausschnitt_schreiben(self):
        ###Schreibt den  Ausschnitte in die Szene
         
        path_stroke = '#ff0000'  # Farbe für den Rand
        path_fill   = 'none'     # keine Füllung, nur eine Linie
        path_stroke_width  = '0.6' # can also be in form '0.6mm'
        #Punkte zu Pfad umwandeln
        self.ausschnitt_pfad = points_to_svgd(self.ausschnitt_punkte, True)       
        
        # define style using basic dictionary
        ausschnitt_attribute = {'id': "ausschnitt_%s"%self.ausschnitt_nummer, 'stroke': path_stroke, 'fill': path_fill,
                          'stroke-width': path_stroke_width , 'x': '0', 'y': '0', 'd': self.ausschnitt_pfad}
        self.ausschnitt_nummer += 1
        # add path to scene                
        ausschnitt = inkex.etree.SubElement(self.topgroup, inkex.addNS('path','svg'), ausschnitt_attribute )   
    
        
    def seite_erstellen(self):
        ###Erstellt die Seite der Dose mit den Zinken und den Einschnitten###

        x = 0
        y = self.radius_mit_ueberstand + 10
        punkte_erstellen(self.seite_punkte, x, y)
        for item in range(self.segmente / 2):
            y -= self.material
            punkte_erstellen(self.seite_punkte, x, y)      
            x += self.ausschnitt_breite
            punkte_erstellen(self.seite_punkte, x, y)
            y += self.material
            punkte_erstellen(self.seite_punkte, x, y)
            x += self.ausschnitt_breite
            punkte_erstellen(self.seite_punkte, x, y) 
        if self.boden == False:            
            y += self.hoehe - self.material
            punkte_erstellen(self.seite_punkte, x, y)  
            x -= self.segmente * self.ausschnitt_breite
            punkte_erstellen(self.seite_punkte, x, y)    
            y -= self.hoehe - self.material
            punkte_erstellen(self.seite_punkte, x, y)  
        else:
            y += self.hoehe - self.material - self.material
            punkte_erstellen(self.seite_punkte, x, y)
            for item in range(self.segmente / 2):
                x -= self.ausschnitt_breite
                punkte_erstellen(self.seite_punkte, x, y)
                y += self.material
                punkte_erstellen(self.seite_punkte, x, y)
                x -= self.ausschnitt_breite
                punkte_erstellen(self.seite_punkte, x, y)
                y -= self.material
                punkte_erstellen(self.seite_punkte, x, y)      
            y -= self.hoehe
            punkte_erstellen(self.seite_punkte, x, y)
                
                 
            
            
            
        self.seite_schreiben()
             
    def seite_schreiben(self):
        ###Schreibt die Seite in die Szene
         
        path_stroke = '#0000ff'  # Farbe für den Rand
        path_fill   = 'none'     # keine Füllung, nur eine Linie
        path_stroke_width  = '0.6' # can also be in form '0.6mm'
        #Punkte zu Pfad umwandeln
        self.seite_pfad = points_to_svgd(self.seite_punkte, True)
        
        # define style using basic dictionary
        seite_attribute = {'id': "seite", 'stroke': path_stroke, 'fill': path_fill,
                          'stroke-width': path_stroke_width , 'x': '0', 'y': '0', 'd': self.seite_pfad}
        # add path to scene                
        seite = inkex.etree.SubElement(self.topgroup, inkex.addNS('path','svg'), seite_attribute )
       
    def einschnitte_erstellen(self):
        ###Erstellt die Einschnitte in die Seite
        
        x = self.einschnitt_breite / -2
        y = self.radius_mit_ueberstand + 10 - self.material
        
        for segment_nr in range(self.segmente - 1):
            
            ###Punkt 1 wird berechnet
            x += self.ausschnitt_breite
            punkte_erstellen(self.einschnitt_punkte, x, y)   
            ###Punkt 2 wird berechnet
            x += self.einschnitt_breite
            punkte_erstellen(self.einschnitt_punkte, x, y)            
            ###Punkt 3 wird berechnet
            y += self.hoehe
            punkte_erstellen(self.einschnitt_punkte, x, y)    
            ### Punkt 4 wird berechnet
            x -= self.einschnitt_breite
            punkte_erstellen(self.einschnitt_punkte, x, y) 
            y -= self.hoehe
            
            self.einschnitte_schreiben()
            del self.einschnitt_punkte[:]
        
        
        
    def einschnitte_schreiben(self):
        ###Schreibt die Einschnitte in die Seite
         
        path_stroke = '#00ff00'  # Farbe für die Einschnitte
        path_fill   = 'none'     # keine Füllung, nur eine Linie
        path_stroke_width  = '0.6' # can also be in form '0.6mm'
        #Punkte zu Pfad umwandeln
        self.einschnitt_pfad = points_to_svgd(self.einschnitt_punkte, True)       
        
        # define style using basic dictionary
        einschnitt_attribute = {'id': "einschnitt_%s"%self.einschnitt_nummer, 'stroke': path_stroke, 'fill': path_fill,
                          'stroke-width': path_stroke_width , 'x': '0', 'y': '0', 'd': self.einschnitt_pfad}
        self.einschnitt_nummer += 1
        # add path to scene                
        einschnitt = inkex.etree.SubElement(self.undergroup, inkex.addNS('path','svg'), einschnitt_attribute ) 
        
### -------------------------------------------------------------------
### This is your main function and is called when the extension is run.
    
    def effect(self):
        ###Hauptprogramm
        
        
        # holt die Parameter aus Inkscape
        self.hoehe = self.options.hoehe
        self.durchmesser = self.options.durchmesser
        self.ueberstand = self.options.ueberstand
        self.radius = self.durchmesser / 2
        self.radius_mit_ueberstand = self.radius + self.ueberstand
        self.winkel = self.options.winkel
        self.boden = self.options.boden
        self.material = self.options.material
        self.segmente = int(360 / self.winkel)
        #Ausschnittbreite errechnen
        y = sin(radians(self.winkel)) * self.radius
        beta = 180 - 90 - self.winkel
        b = sin(radians(beta)) * self.radius
        x = self.radius - b 
        self.ausschnitt_breite = sqrt((x * x) + (y * y))
        # what page are we on
        page_id = self.options.active_tab # sometimes wrong the very first time

        #Eigenschaften der SVG auslesen und die Größe der Dose anpassen
        svg = self.document.getroot()
        #viewbox_size = '0 0 ' + str(self.breite) + ' ' + str(self.hoehe)
        #svg.set('viewBox', viewbox_size)
        #svg.set('height', str(self.hoehe))
        #svg.set('width', str(self.breite))
        
        # Embed the path in a group to make animation easier:
        # Be sure to examine the internal structure by looking in the xml editor inside inkscape
        
        # Make a nice useful name
        g_attribs = { inkex.addNS('label','inkscape'): 'dosen-gruppe', 'id': "dose",}
        # add the group to the document's current layer
        self.topgroup = inkex.etree.SubElement(self.current_layer, 'g', g_attribs )
        # Create SVG Path under this top level group
        # Make a nice useful name
        g_attribs = { inkex.addNS('label','inkscape'): 'einschnitt-gruppe', 'id': "einschnitte",}
        # add the group to the document's current layer
        self.undergroup = inkex.etree.SubElement(self.current_layer, 'g', g_attribs )
        # Create SVG Path under this top level group
        
        self.deckel_erstellen()
        self.ausschnitt_erstellen()
        self.seite_erstellen()
        self.einschnitte_erstellen()
        
        
        # Make a nice useful name
        text_g_attribs = { inkex.addNS('label','inkscape'): 'dosen-gruppe', 'id': "Branding",}
        # add the group to the document's current layer
        textgroup = inkex.etree.SubElement(self.current_layer, 'g', text_g_attribs )

        line_style = {'font-size': '10px', 'font-style':'normal', 'font-weight': 'normal',
                     'fill': '#ff0000', 'font-family': 'Consolas',
                     'text-anchor': 'start'}
        branding_line_attribs = {inkex.addNS('label','inkscape'): 'branding-text',
                       'id': 'front text',
                       'style': simplestyle.formatStyle(line_style),
                       'x': str(0),
                       'y': str(0)
                       }
        
        branding_line = inkex.etree.SubElement(textgroup, inkex.addNS('text','svg'), branding_line_attribs)
        branding_line.text = 'dosen-generator by mini revollo member of the erfindergarden'

         # Make a nice useful name
        einschnitt_text_g_attribs = { inkex.addNS('label','inkscape'): 'einschnitt-gruppe', 'id': "Einschnitte_Text",}
        # add the group to the document's current layer
        textgroup = inkex.etree.SubElement(self.current_layer, 'g', einschnitt_text_g_attribs )

        line_style = {'font-size': '5px', 'font-style':'normal', 'font-weight': 'normal',
                     'fill': '#00ff00', 'font-family': 'Consolas',
                     'text-anchor': 'start'}
        einschnitt_line_attribs = {inkex.addNS('label','inkscape'): 'Einschnitte_text',
                       'id': 'front text',
                       'style': simplestyle.formatStyle(line_style),
                       'x': str(0),
                       'y': str(self.radius_mit_ueberstand + self.hoehe / 2)
                       }
        
        branding_line = inkex.etree.SubElement(textgroup, inkex.addNS('text','svg'), einschnitt_line_attribs)
        branding_line.text = 'Die Einschnitte nur zu 70 Prozent in das Material lasern'
        
        
if __name__ == '__main__':
    dose = Dose()
    dose.affect()

# Notes


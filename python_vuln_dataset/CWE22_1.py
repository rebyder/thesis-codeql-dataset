# repo: sighill/shade_app
# path: apis/raw/005_raw/005_cleaner.py

# 005_cleaner.py
#####################################################################

##################################
# Import des modules et ajout du path de travail pour import relatif
import sys
sys.path.insert(0 , 'C:/Users/WILLROS/Perso/Shade/scripts/LocalWC-Shade-App/apis/')
from voca import AddLog , StringFormatter , OutFileCreate , OdditiesFinder

##################################
# Init des paths et noms de fichiers
missionName = '005'
AddLog('title' , '{} : Début du nettoyage du fichier'.format(missionName))
work_dir = 'C:/Users/WILLROS/Perso/Shade/scripts/LocalWC-Shade-App/apis/raw/{}_raw/'.format(missionName)
# Nom du fichier source
raw_file = 'src'

##################################
# retreiving raw string
raw_string_with_tabs = open(work_dir + raw_file , 'r').read()
# replacing tabs with carriage return
raw_string_with_cr = raw_string_with_tabs.replace( '\t', '\n' )
# turning the string into a list
raw_list = raw_string_with_cr.splitlines()
# going through oddities finder
AddLog('subtitle' , 'Début de la fonction OdditiesFinder')
list_without_oddities = OdditiesFinder( raw_list )
# going through string formatter
ref_list = []
AddLog('subtitle' , 'Début de la fonction StringFormatter')
for line in list_without_oddities:
	ref_list.append( StringFormatter( line ) )

##################################
# Enregistrement des fichiers sortie
AddLog('subtitle' , 'Début de la fonction OutFileCreate')
OutFileCreate('C:/Users/WILLROS/Perso/Shade/scripts/LocalWC-Shade-App/apis/out/','{}_src'.format(missionName),ref_list,'prenoms masculins italiens')

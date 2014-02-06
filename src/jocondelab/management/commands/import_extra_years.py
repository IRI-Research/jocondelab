# -*- coding: utf-8 -*-
#
# Copyright Institut de Recherche et d'Innovation © 2014
#
# contact@iri.centrepompidou.fr
#
# Ce code a été développé pour un premier usage dans JocondeLab, projet du 
# ministère de la culture et de la communication visant à expérimenter la
# recherche sémantique dans la base Joconde
# (http://jocondelab.iri-research.org/).
#
# Ce logiciel est régi par la licence CeCILL-C soumise au droit français et
# respectant les principes de diffusion des logiciels libres. Vous pouvez
# utiliser, modifier et/ou redistribuer ce programme sous les conditions
# de la licence CeCILL-C telle que diffusée par le CEA, le CNRS et l'INRIA 
# sur le site "http://www.cecill.info".
#
# En contrepartie de l'accessibilité au code source et des droits de copie,
# de modification et de redistribution accordés par cette licence, il n'est
# offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
# seule une responsabilité restreinte pèse sur l'auteur du programme,  le
# titulaire des droits patrimoniaux et les concédants successifs.
#
# A cet égard  l'attention de l'utilisateur est attirée sur les risques
# associés au chargement,  à l'utilisation,  à la modification et/ou au
# développement et à la reproduction du logiciel par l'utilisateur étant 
# donné sa spécificité de logiciel libre, qui peut le rendre complexe à 
# manipuler et qui le réserve donc à des développeurs et des professionnels
# avertis possédant  des  connaissances  informatiques approfondies.  Les
# utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
# logiciel à leurs besoins dans des conditions permettant d'assurer la
# sécurité de leurs systèmes et ou de leurs données et, plus généralement, 
# à l'utiliser et l'exploiter dans les mêmes conditions de sécurité. 
#
# Le fait que vous puissiez accéder à cet en-tête signifie que vous avez 
# pris connaissance de la licence CeCILL-C, et que vous en avez accepté les
# termes.
#
'''
Created on Sep 19, 2013

@author: rvelt
'''

from core.models import Term
from jocondelab.models import DbpediaYears
from django.core.management import BaseCommand
import csv
import os

class Command(BaseCommand):

    args = "csv_file"
    
    help = "Import csv file containing dbpedia uris and years"
    
    def handle(self, *args, **options):
        
        filepath = os.path.abspath(args[0])
        self.stdout.write("Importing %s" % filepath)
        
        with open(filepath,'rb') as csv_file:
            dialect = csv.Sniffer().sniff(csv_file.read(1024))
            csv_file.seek(0)
            reader = csv.DictReader(csv_file, dialect=dialect)
            for row in reader:
                print row
                if row.get('start_year', None) is not None and row.get('end_year', None) is not None:
                    start_year = int(row['start_year'])
                    end_year = int(row['end_year'])
                    dbpedia_uri = row.get('dbpedia_uri',None)
                    term_label = row.get('term_label',None)
                    ts = None
                    if dbpedia_uri is not None:
                        ts = Term.objects.filter(dbpedia_uri = dbpedia_uri)  # @UndefinedVariable
                    elif term_label is not None:
                        ts = Term.objects.filter(label = term_label)  # @UndefinedVariable
                    if ts is not None:
                        for t in ts:
                            dyobj, created = DbpediaYears.objects.get_or_create(term=t, defaults={'start_year': start_year, 'end_year': end_year})
                            if not created:
                                dyobj.start_year = start_year
                                dyobj.end_year = end_year
                                dyobj.save()
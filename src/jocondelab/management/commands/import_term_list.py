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
Created on Jul 31, 2013

@author: ymh
'''

from core.models import Term
from jocondelab.models import ContributableTerm, TagcloudTerm
from django.core.management.base import BaseCommand
from optparse import make_option

class Command(BaseCommand):
    
    help = "Import a list of term for inclusion in the tagcloud or available contributable terms"
    
    option_list = BaseCommand.option_list + (
        make_option('-c', '--clear',
            dest= 'clear',
            action= 'store_true',
            default= False,
            help= 'Clear table' 
        ),
        make_option('-t', '--tagcloud',
            dest= 'tagcloud',
            action= 'store_true',
            default= False,
            help= 'Store in TagCloud table instead of ' 
        ),
        make_option('-l','--lang',
            dest= 'language_code',
            default= None,
            help= 'Language Code. If not provided, the labels in the Term table will be used' 
        ),
        make_option('-f','--file',
            dest= 'file_name',
            default= None,
            help= 'Extract keywords from a text file instead of from command line args'
        ),
    )
    
    def handle(self, *args, **options):
        
        terms_to_add = None
        
        if args:
            terms_to_add = args
        
        file_name = options.get('file_name', None)
        if file_name:
            try:
                f = open(file_name, 'r')
                terms_to_add = [l.strip() for l in f.readlines()]
                f.close()
            except:
                print "Can't open file %s"%file_name
                
        if not terms_to_add:
            print "No terms to add"
            return
        
        is_tagcloud = options.get('tagcloud', False)
        DestinationModel = TagcloudTerm if is_tagcloud else ContributableTerm
        
        print "Target model is %s"%DestinationModel.__name__
                
        if options.get('clear', False):
            print "Clearing table"
            DestinationModel.objects.all().delete()
        
        language_code = options.get('language_code', None)
        
        for t in terms_to_add:
            if t:
                tt = t.split("|")
                label = tt[0]
                ts = Term.objects  # @UndefinedVariable
                if language_code:
                    ts = ts.filter(dbpedia_fields__label=label,dbpedia_fields__language_code=language_code)
                else:
                    ts = ts.filter(label=label)
                if len(tt) > 1:
                    thesaurus = tt[1]
                    ts = ts.filter(thesaurus__label=thesaurus)
                print "%d term(s) found for label '%s'"%(ts.count(),t)
                for to in ts:
                    DestinationModel.objects.get_or_create(term=to)

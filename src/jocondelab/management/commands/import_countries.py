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
Created on Jun 11, 2013

@author: ymh
'''

from SPARQLWrapper import SPARQLWrapper2
from django.core.management.base import NoArgsCommand
from django.db import transaction, reset_queries
from jocondelab.models import Country
from core.models import Notice
from core.utils import show_progress
from django.utils.http import urlquote
from optparse import make_option


class Command(NoArgsCommand):

    help = "Import countries from dbpedia"
    
    option_list = NoArgsCommand.option_list + (
        make_option('-b', '--batch-size',
            dest= 'batch_size',
            type='int',
            default= 50,
            help= 'number of object to import in bulk operations' 
        ),                                               
    )
    
    def handle_noargs(self, **options):
        
        def count_notices(uri):
            return Notice.objects.filter(noticeterm__term__dbpedia_uri=uri).count()
        
        def add_country(dbpedia_uri, iso_code_3, iso_code_2):
            nb_notices = count_notices(dbpedia_uri)
            countryobj, created = Country.objects.get_or_create(
                            dbpedia_uri = dbpedia_uri,
                            defaults = {
                                    'iso_code_3': iso_code_3,
                                    'iso_code_2': iso_code_2,
                                    'nb_notices': nb_notices
                                }
                            )
            if not created:
                countryobj.iso_code_3 = iso_code_3
                countryobj.iso_code_2 = iso_code_2
                countryobj.nb_notices = nb_notices
                countryobj.save()
        
        writer = None
        resource_prefix = u'http://fr.dbpedia.org/resource/'
        batch_size = options.get('batch_size', 50)
        
        transaction.enter_transaction_management()
        transaction.managed()

        endpoint = SPARQLWrapper2("http://fr.dbpedia.org/sparql")
        sparql = """
        select distinct ?pays ?code where {
                    ?pays rdf:type dbpedia-owl:Country .
                    ?pays prop-fr:iso ?code
                } LIMIT 300
        """
        endpoint.setQuery(sparql)
        results = endpoint.query()
        
        count = len(results.bindings)
        
        substitutions = [
                 (u'R%C3%A9publique_populaire_de_Chine', u'Chine')
                 ]
        
        for i,binding in enumerate(results.bindings):
            if binding[u"code"].type == 'literal':
                resource_suffix = urlquote(binding[u"pays"].value.replace(resource_prefix,""))
                for s in substitutions:
                    if resource_suffix == s[0]:
                        resource_suffix = s[1]
                        break
                dbpedia_uri = u'%s%s'%(resource_prefix, resource_suffix)
                writer = show_progress(i+1, count, dbpedia_uri, 50, writer)
                iso_codes = binding[u"code"].value.split(", ")
                if (len(iso_codes) > 1):
                    add_country(dbpedia_uri, iso_codes[0], iso_codes[1])

            if not ((i+1) % batch_size):
                transaction.commit()
                reset_queries()

        # insert code for Maurice and Antarctica
        extra_countries = [
                           (u'%sMaurice_(pays)'%resource_prefix, "MUS", "MU"),
                           (u'%sAntarctique'%resource_prefix, "ATA", "AQ")
                           ]
        for c in extra_countries:
            add_country(*c)
        
        transaction.commit()
        reset_queries()
        transaction.leave_transaction_management()
            
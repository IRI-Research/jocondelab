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
Created on Aug 08, 2013

@author: rvelt
'''

import math
import re
import sys
import traceback

from SPARQLWrapper import SPARQLWrapper2
from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.db import transaction
from django.utils.http import urlunquote

from core.models import Term
from core.utils import show_progress
from core.wp_utils import get_dbpedia_lang
from jocondelab.models import DbpediaYears, DbpediaGeo


class Command(NoArgsCommand):
    
    help = "Import tag metadata from dbpedia"
    
    
    def handle_noargs(self, **options):
        
        endpoints = {}
        qs = Term.objects.exclude(dbpedia_uri=None).order_by('-nb_notice')  # @UndefinedVariable
        count = qs.count()
        writer = None
        
        yearre = re.compile("^-?\d+")
        sylbls = [  "birthdate", "startyear" ]
        eylbls = [ "deathdate", "endyear" ]
        
        for i,obj in enumerate(qs):
            writer = show_progress(i+1, count, obj.dbpedia_uri, 50, writer)
            dbp_lang = get_dbpedia_lang(obj.dbpedia_uri)
            if dbp_lang is None:
                print("Lang unknown for %s, continue" % obj.dbpedia_uri)
                continue
            endpoint = endpoints.get(dbp_lang, None)
            if endpoint is None:
                dbpedia_sparql_url = settings.WIKIPEDIA_URLS.get(dbp_lang,{}).get('dbpedia_sparql_url', None)
                if dbpedia_sparql_url is None:
                    print("Lang unknown for %s, continue" % obj.dbpedia_uri)
                    continue
                endpoint = endpoints.setdefault(dbp_lang, SPARQLWrapper2(dbpedia_sparql_url))
            try:
                with transaction.commit_on_success():
                    uri = urlunquote(obj.dbpedia_uri)
                    sparql = u"""
    select distinct * where {
        OPTIONAL {
          <%s> dbpedia-owl:activeYearsStartYear ?startyear .
          <%s> dbpedia-owl:activeYearsEndYear ?endyear .
        }
        OPTIONAL {
          <%s> dbpedia-owl:birthDate ?birthdate .
          <%s> dbpedia-owl:deathDate ?deathdate .
        }
        OPTIONAL {
          <%s> geo:lat ?latitude .
          <%s> geo:long ?longitude .
        }
    }
                    """%(6*(uri,))
                    endpoint.setQuery(sparql)
                    results = endpoint.query()
                    
                    if len(results.bindings):
                        binding = results.bindings[0]
                        syv = None
                        eyv = None
                        for lbl in sylbls:
                            if lbl in binding:
                                syv = yearre.findall(binding[lbl].value)
                                break
                        for lbl in eylbls:
                            if lbl in binding:
                                eyv = yearre.findall(binding[lbl].value)
                                break
                        if syv and eyv:
                            sy = syv[0]
                            ey = eyv[0]
                            dbyr, created = DbpediaYears.objects.get_or_create(term = obj, defaults={'start_year': sy, 'end_year': ey})
                            if not created:
                                dbyr.start_year = sy
                                dbyr.end_year = ey
                                dbyr.save()
                        
                        lat = float(binding["latitude"].value) if "latitude" in binding else None
                        lng = float(binding["longitude"].value) if "longitude" in binding else None
                        
                        if (lat is not None) and (not math.isnan(lat)) and (lng is not None) and (not math.isnan(lng)):
                            dbgeo, created = DbpediaGeo.objects.get_or_create(term = obj, defaults={'latitude': lat, 'longitude': lng})
                            if not created:
                                dbgeo.latitude = lat
                                dbgeo.longitude = lng
                                dbgeo.save()
                        
            except Exception as e:
                print "\nError processing resource %s : %s" %(obj.dbpedia_uri,unicode(e))
                traceback.print_exception(type(e), e, sys.exc_info()[2])
                
        
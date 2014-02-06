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
from optparse import make_option
import sys
import traceback
import urllib2

from SPARQLWrapper.Wrapper import RDF, SPARQLWrapper
from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.db import reset_queries, transaction
from django.db.models.aggregates import Count
from django.utils.http import urlunquote
from rdflib.term import URIRef

from core.models import Term
from core.utils import show_progress
from core.wp_utils import get_dbpedia_lang
from jocondelab.models.data import TermLinks, DbpediaFields
from django.core.management import call_command

class Command(NoArgsCommand):
    '''
    query and update wikipedia for tag title.
    '''
    options = ''
    help = """query and update wikipedia for tag title."""
    
    option_list = NoArgsCommand.option_list + (
        make_option('--all',
            action='store_true',
            dest='all',
            default=False,
            help='force all tags to be updated, not only those not yet processed'),
        make_option('--force',
            action='store_true',
            dest='force',
            default=False,
            help='ask no questions'),
        make_option('--validated',
            action='store_true',
            dest='validated',
            default=False,
            help='query only validated terms'),
        make_option('--random',
            action='store_true',
            dest='random',
            default=False,
            help='randomize query on tags'),
        make_option('--limit',
            action='store',
            type='int',
            dest='limit',
            default= -1,
            help='number of tag to process'),
        make_option('--start',
            action='store',
            type='int',
            dest='start',
            default=0,
            help='number of tag to ignore'),
        make_option('--term',
            action='append',
            dest='terms',
            type='string',
            default=[],
            help='the tag to query'),
    )
    
    def handle_noargs(self, **options):

        self.interactive = options.get('interactive', True)
        self.verbosity = int(options.get('verbosity', '1'))        
        self.all = options.get('all', False)
        self.force = options.get('force', False)        
        self.limit = options.get("limit", -1)
        self.start = options.get("start", 0)        
        self.random = options.get('random', False)
        self.term_list = options.get("terms", []);
        self.validated = options.get("validated", False);
        
        if self.verbosity > 2:
            print "option passed : " + repr(options)


        qs = Term.objects.exclude(dbpedia_uri= None)  # @UndefinedVariable
        
        if self.validated:
            qs = qs.filter(validated=True)
        
        if self.term_list:
            qs = qs.filter(label__in = self.term_list)
            
        if not self.all:
            qs = qs.annotate(dbfc=Count('dbpedia_fields')).filter(dbfc = 0)
            
        if self.random:
            qs = qs.order_by('?')
        else:
            qs = qs.order_by('label')
        
        if self.limit >= 0:
            qs = qs[self.start:self.limit]
        elif self.start > 0:
            qs = qs[self.start:]

        if self.verbosity > 2 :
            print("Term Query is %s" % (qs.query))

        count = qs.count()
        
        if count == 0:
            print("No tag to query : exit.")
            return

        if not self.force and self.interactive:
            confirm = raw_input("You have requested to query and replace the dbpedia information for %d terms.\n Are you sure you want to do this? \nType 'yes' to continue, or 'no' to cancel: " % (count))
        else:
            confirm = 'yes'
            
        if confirm != "yes":
            print "dbpedia query cancelled"
            return

        endpoints = {}
        
        writer = None
        transaction.enter_transaction_management()
        for i,aterm in enumerate(qs):
            writer = show_progress(i+1, count, aterm.label, 50, writer)
            reset_queries()
            
            try :
                abstracts = {}
                labels = {}
                thumbnail = None
                dbp_lang = get_dbpedia_lang(aterm.dbpedia_uri)
                if dbp_lang is None:
                    print("Lang unknown for %s, continue" % aterm.dbpedia_uri)
                    continue
                endpoint = endpoints.get(dbp_lang, None)
                if endpoint is None:
                    dbpedia_sparql_url = settings.WIKIPEDIA_URLS.get(dbp_lang,{}).get('dbpedia_sparql_url', None)
                    if dbpedia_sparql_url is None:
                        print("Lang unknown for %s, continue" % aterm.dbpedia_uri)
                        continue
                    endpoint = endpoints.setdefault(dbp_lang, SPARQLWrapper(dbpedia_sparql_url, returnFormat=RDF))
                

                dbpedia_uri = urlunquote(aterm.dbpedia_uri)

                endpoint.setQuery(u"select distinct ?y where {<%s>  <http://dbpedia.org/ontology/abstract> ?y}" % (dbpedia_uri))
                
                res_abstracts = endpoint.queryAndConvert()
                for _,_,o in res_abstracts.triples((None, URIRef('http://www.w3.org/2005/sparql-results#value'), None)):
                    abstracts[o.language] = unicode(o)


                endpoint.setQuery(u"select distinct ?y where {<%s>  <http://www.w3.org/2000/01/rdf-schema#label> ?y}" % (dbpedia_uri))
                res_labels = endpoint.queryAndConvert()
                for _,_,o in res_labels.triples((None, URIRef('http://www.w3.org/2005/sparql-results#value'), None)):
                    labels[o.language] = unicode(o)
                        
                endpoint.setQuery(u"select distinct ?y where {<%s>  <http://dbpedia.org/ontology/thumbnail> ?y} limit 1" % (dbpedia_uri))
                res_thumbnails = endpoint.queryAndConvert()
                for _,_,o in res_thumbnails.triples((None, URIRef('http://www.w3.org/2005/sparql-results#value'), None)):
                    thumbnail = unicode(o)

                endpoint.setQuery(u'select distinct ?y where { <%s> ?p ?y . FILTER regex(?y, "^http://dbpedia.org/resource")}' % (dbpedia_uri))
                res_links = endpoint.queryAndConvert()
                for _,_,o in res_links.triples((None, URIRef('http://www.w3.org/2005/sparql-results#value'), None)):
                    termqs = Term.objects.filter(dbpedia_uri= urllib2.quote(unicode(o).encode("utf8")))  # @UndefinedVariable
                    if len(termqs):
                        TermLinks.objects.get_or_create(subject=aterm, object=termqs[0])                        
                
                language_set = set(labels.keys()) | set(abstracts.keys())

                for lang in language_set:
                    dbfield , created = DbpediaFields.objects.get_or_create(dbpedia_uri=aterm.dbpedia_uri, language_code=lang, term=aterm, defaults={'abstract':abstracts.get(lang, None), 'thumbnail':thumbnail, 'label':labels.get(lang, None)}) #@UndefinedVariable
                    if not created:
                        dbfield.abstract = abstracts.get(lang, None)
                        dbfield.thumbnail = thumbnail
                        dbfield.label = labels.get(lang, None)
                        dbfield.save()
                    
                transaction.commit()
            except Exception as e:
                print "\nError processing resource %s : %s" %(aterm.dbpedia_uri,unicode(e))
                traceback.print_exception(type(e), e, sys.exc_info()[2])
                transaction.rollback()

        transaction.leave_transaction_management()
        print("Ddpedia fields imported. launching index recreation, no questions asked.")
        call_command("rebuild_index", interactive=False)


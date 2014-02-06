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

from core.models import Term, Thesaurus
from core.models.term import TermLabel
from core.rdf_models import graph
from core.settings import (AUTR_CONTEXT, DOMN_CONTEXT, ECOL_CONTEXT, EPOQ_CONTEXT, 
    LIEUX_CONTEXT, PERI_CONTEXT, REPR_CONTEXT, SREP_CONTEXT)
from core.wp_utils import get_or_create_term, switch_case_group
from django.core.management.base import NoArgsCommand
from django.db import transaction, reset_queries
from optparse import make_option
from rdflib.term import URIRef

THESAURUS_DEFS = [
    {'label':'AUTR' ,'uri':AUTR_CONTEXT},
    {'label':'DOMN' ,'uri':DOMN_CONTEXT},
    {'label':'ECOL' ,'uri':ECOL_CONTEXT},
    {'label':'EPOQ' ,'uri':EPOQ_CONTEXT},
    {'label':'LIEUX','uri':LIEUX_CONTEXT},
    {'label':'PERI' ,'uri':PERI_CONTEXT},
    {'label':'REPR' ,'uri':REPR_CONTEXT},
    {'label':'SREP' ,'uri':SREP_CONTEXT},
]

THESAURUS_LABEL_TRANSFORM = {
    'AUTR' : switch_case_group,
    'DOMN' : lambda l:l,
    'ECOL' : lambda l:l,
    'EPOQ' : lambda l:l,
    'LIEUX': lambda l:l,
    'PERI' : lambda l:l,
    'REPR' : lambda l:l,
    'SREP' : lambda l:l,
}


class Command(NoArgsCommand):

    help = "Import graph terms in relational database, to be run after import_skos"
    
    option_list = NoArgsCommand.option_list + (
        make_option('-b', '--batch-size',
            dest= 'batch_size',
            type='int',
            default= 50,
            help= 'number of object to import in bulk operations' 
        ),
        make_option('-s','--skip-wp',
            dest= 'skip_wp_query',
            action= 'store_true',
            default= False,
            help= 'skip wikipedia query' 
        ),
        make_option('-l','--lang',
            dest= 'wp_lang',
            default= 'fr',
            help= 'wikipedia language' 
        ),
                                               
    )

    
    def handle_noargs(self, **options):
        
        batch_size = options.get('batch_size', 50)
        skip_wp_query = options.get('skip_wp_query', False)
        wp_lang = options.get('wp_lang', 'fr')
        
        transaction.enter_transaction_management()
        transaction.managed()

        
        # create all thesaurus        
        for t_def in THESAURUS_DEFS:
            if not Thesaurus.objects.filter(uri=t_def['uri']).exists():
                Thesaurus.objects.create(**t_def)
        transaction.commit()
        reset_queries()
        
        for thes in Thesaurus.objects.all():
            self.stdout.write("Processing Thesaurus %s" % thes.label)
            for _,p,o in graph.triples((URIRef(thes.uri), None, None)):
                if p == URIRef("http://purl.org/dc/elements/1.1/title"):
                    thes.title = unicode(o)
                elif p == URIRef("http://purl.org/dc/elements/1.1/description"):
                    thes.description = unicode(o)
            thes.save()
            transaction.commit()
            reset_queries()
            context = graph.get_context(URIRef(thes.uri))
            for i,(s,_,o) in enumerate(graph.triples((None, URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"), None), context=context)):
                self.stdout.write("%d - Thesaurus %s term pref label %s" % (i+1,thes.label, repr(o)))                
                lang = getattr(o, 'language', None)
                get_or_create_term(
                    term_label=unicode(o).strip(),
                    term_uri=unicode(s),
                    term_lang=lang,
                    thesaurus = thes,
                    lang = wp_lang,
                    wp_label_transform = THESAURUS_LABEL_TRANSFORM.get(thes.label,lambda l:l),
                    skip_wp_query=skip_wp_query
                )
                
                if not ((i+1) % batch_size):
                    transaction.commit()
                    reset_queries()
            transaction.commit()
            reset_queries()
            
            for i,(s,_,o) in enumerate(graph.triples((None, URIRef("http://www.w3.org/2004/02/skos/core#altLabel"), None), context=context)):
                self.stdout.write("%d - Thesaurus %s term alt label %s for %s" % (i+1, thes.label, repr(o), repr(s)))
                try:
                    term = Term.objects.get(uri=unicode(s))  # @UndefinedVariable
                    alt_label = unicode(o).strip()
                    lang = getattr(o, 'language', None)
                    if not TermLabel.objects.filter(label=alt_label, term=term).exists():
                        TermLabel.objects.create(label=alt_label, term=term, lang=lang)
                except Term.DoesNotExist:  # @UndefinedVariable
                    self.stdout.write("Thesaurus %s term alt label %s for %s does not exists" % (thes.label, repr(o), repr(s)))
                if not ((i+1) % batch_size):
                    transaction.commit()
                    reset_queries()

            transaction.commit()
            reset_queries()
        transaction.leave_transaction_management()
            
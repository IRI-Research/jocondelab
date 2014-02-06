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
from core.wp_utils import normalize_term
from django.core.management.base import NoArgsCommand
from django.db import transaction, reset_queries
from optparse import make_option
from rdflib.term import URIRef


class Command(NoArgsCommand):

    help = "Import graph terms in relational database, to be run after import_skos"
    
    option_list = NoArgsCommand.option_list + (
        make_option('-b', '--batch-size',
            dest= 'batch_size',
            type='int',
            default= 50,
            help= 'number of object to import in bulk operations' 
        ),                                               
    )

    
    def handle_noargs(self, **options):
        
        batch_size = options.get('batch_size', 50)
        
        transaction.enter_transaction_management()
        transaction.managed()

                
        for thes in Thesaurus.objects.all():
            context = graph.get_context(URIRef(thes.uri))
            for i,(s,_,o) in enumerate(graph.triples((None, URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"), None), context=context)):
                self.stdout.write("%d - Thesaurus %s term pref label %s" % (i+1,thes.label, repr(o)))
                try:                
                    term = Term.objects.get(uri=unicode(s))  # @UndefinedVariable
                    lang = getattr(o, 'language', None)
                    pref_label = unicode(o).strip()
                    if term.label != pref_label:
                        term.label = pref_label
                        term.normalized_label = normalize_term(pref_label)
                        term.save()

                    if not TermLabel.objects.filter(label=pref_label, term=term, lang=lang).exists():
                        TermLabel.objects.create(label=pref_label, term=term, lang=lang)
                except Term.DoesNotExist:  # @UndefinedVariable
                    self.stdout.write("Thesaurus %s term pref label %s for %s does not exists" % (thes.label, repr(o), repr(s)))                
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
                    if not TermLabel.objects.filter(label=alt_label, term=term, lang=lang).exists():
                        TermLabel.objects.create(label=alt_label, term=term, lang=lang)
                except Term.DoesNotExist:  # @UndefinedVariable
                    self.stdout.write("Thesaurus %s term alt label %s for %s does not exists" % (thes.label, repr(o), repr(s)))
                if not ((i+1) % batch_size):
                    transaction.commit()
                    reset_queries()

            transaction.commit()
            reset_queries()
        transaction.leave_transaction_management()
            
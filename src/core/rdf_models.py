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

from rdflib import plugin, ConjunctiveGraph, URIRef, Literal
from rdflib.store import Store
from django.db import connections

class TermGraph(ConjunctiveGraph):
    
    def __init__(self, do_open=False, create=False):
        identifier = "jocondelab"        
        store = plugin.get("SQLAlchemy", Store)(identifier=identifier)
        ConjunctiveGraph.__init__(self, store=store, identifier=identifier)
        if do_open:
            self.open(create)

    def open(self, create=False):
        db_settings = connections['default'].settings_dict
        sa_db_settings = {
            'engine': 'postgresql+psycopg2' if db_settings['ENGINE'] == "django.db.backends.postgresql_psycopg2" else db_settings['ENGINE'],
            'user': db_settings['USER'],
            'password': db_settings['PASSWORD'],
            'port': db_settings['PORT'] if db_settings['PORT'] else "5432",
            'host': db_settings['HOST'] if db_settings['HOST'] else "localhost",
            'name': db_settings['NAME']             
        } 
        connect_config = "%(engine)s://%(user)s:%(password)s@%(host)s:%(port)s/%(name)s"%sa_db_settings 

        return ConjunctiveGraph.open(self, connect_config, create=create)

    def get_uri_for_term(self, term, context):
        c = self.get_context(URIRef(context))
        tl = Literal(term)
        
        for s,p,_ in self.triples((None, None, tl), context=c):
            if p in [URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"), URIRef("http://www.w3.org/2004/02/skos/core#alternateLabel")]:
                return unicode(s)
        return None

graph = TermGraph(do_open=True, create=False)
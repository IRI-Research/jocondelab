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
Created on Jun 10, 2013

@author: ymh
'''

from django.conf import settings

JOCONDE_IMAGE_BASE_URL = getattr(settings, 'JOCONDE_IMAGE_BASE_URL', '')

AUTR_CONTEXT  = getattr(settings,'AUTR_CONTEXT' , 'http://data.culture.fr/thesaurus/resource/ark:/67717/T513')
DOMN_CONTEXT  = getattr(settings,'DOMN_CONTEXT' , 'http://data.culture.fr/thesaurus/resource/ark:/67717/T51')
ECOL_CONTEXT  = getattr(settings,'ECOL_CONTEXT' , 'http://data.culture.fr/thesaurus/resource/ark:/67717/T517')
EPOQ_CONTEXT  = getattr(settings,'EPOQ_CONTEXT' , 'http://data.culture.fr/thesaurus/resource/ark:/67717/T93')
LIEUX_CONTEXT = getattr(settings,'LIEUX_CONTEXT', 'http://data.culture.fr/thesaurus/resource/ark:/67717/T84')
PERI_CONTEXT  = getattr(settings,'LIEUX_CONTEXT', 'http://data.culture.fr/thesaurus/resource/ark:/67717/T521')
REPR_CONTEXT  = getattr(settings,'REPR_CONTEXT' , 'http://data.culture.fr/thesaurus/resource/ark:/67717/T523')
SREP_CONTEXT  = getattr(settings,'SREP_CONTEXT' , 'http://data.culture.fr/thesaurus/resource/ark:/67717/T507')


WIKIPEDIA_URLS = getattr(settings, "WIKIPEDIA_URLS", {
    'fr': {
        'base_url': "http://fr.wikipedia.org",
        'page_url': "http://fr.wikipedia.org/wiki",
        'api_url': "http://fr.wikipedia.org/w/api.php",
        'permalink_tmpl': "http://fr.wikipedia.org/w/index.php?oldid=%s",
        'dbpedia_base_url' : "http://fr.dbpedia.org",
        'dbpedia_uri' : "http://fr.dbpedia.org/resource/%s",
        'dbpedia_sparql_url' : "http://fr.dbpedia.org/sparql",
        'dbpedia_sparql_use_proxy': False,
        'disambiguation_cat' : u'Catégorie:Homonymie',
    },
    'en': {
        'base_url': "http://en.wikipedia.org",
        'page_url': "http://en.wikipedia.org/wiki",
        'api_url': "http://en.wikipedia.org/w/api.php",
        'permalink_tmpl': "http://en.wikipedia.org/w/index.php?oldid=%s",
        'dbpedia_base_url' : "http://dbpedia.org",
        'dbpedia_uri' : "http://dbpedia.org/resource/%s",
        'dbpedia_sparql_url' : "http://dbpedia.org/sparql",
        'dbpedia_sparql_use_proxy': False,
        'disambiguation_cat' : u'Category:Disambiguation pages',
    },
    'it': {
        'base_url': "http://it.wikipedia.org",
        'page_url': "http://it.wikipedia.org/wiki",
        'api_url': "http://it.wikipedia.org/w/api.php",
        'permalink_tmpl': "http://it.wikipedia.org/w/index.php?oldid=%s",
        'dbpedia_base_url' : "http://it.dbpedia.org",
        'dbpedia_uri' : "http://it.dbpedia.org/resource/%s",
        'dbpedia_sparql_url' : "http://it.dbpedia.org/sparql",
        'dbpedia_sparql_use_proxy': True,
        'disambiguation_cat' : u'Categoria:Disambigua',
    },
    'de': {
        'base_url': "http://de.wikipedia.org",
        'page_url': "http://de.wikipedia.org/wiki",
        'api_url': "http://de.wikipedia.org/w/api.php",
        'permalink_tmpl': "http://de.wikipedia.org/w/index.php?oldid=%s",
        'dbpedia_base_url' : "http://de.dbpedia.org",
        'dbpedia_uri' : "http://de.dbpedia.org/resource/%s",
        'dbpedia_sparql_url' : "http://de.dbpedia.org/sparql",
        'dbpedia_sparql_use_proxy': True,
        'disambiguation_cat' : u'Kategorie:Begriffsklärung',
    },
    'ja': {
        'base_url': "http://ja.wikipedia.org",
        'page_url': "http://ja.wikipedia.org/wiki",
        'api_url': "http://ja.wikipedia.org/w/api.php",
        'permalink_tmpl': "http://ja.wikipedia.org/w/index.php?oldid=%s",
        'dbpedia_base_url' : "http://ja.dbpedia.org",
        'dbpedia_uri' : "http://ja.dbpedia.org/resource/%s",
        'dbpedia_sparql_url' : "http://ja.dbpedia.org/sparql",
        'dbpedia_sparql_use_proxy': False,
        'disambiguation_cat' : u'カテゴリ:同名の地名',
    },
})



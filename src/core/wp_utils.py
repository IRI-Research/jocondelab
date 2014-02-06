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
from .models import Term, TermLabel, TERM_URL_STATUS_DICT
from core.models.term import TERM_WK_LINK_SEMANTIC_LEVEL_DICT
from django.conf import settings
from django.utils.http import urlquote
from urlparse import urlparse
from wikitools import api, wiki
import logging
import urllib2

logger = logging.getLogger(__name__)
sites = {}

def __get_site(lang):
    site = sites.get(lang, None)
    if site is None:
        site = wiki.Wiki(settings.WIKIPEDIA_URLS[lang]['api_url'])  # @UndefinedVariable
        sites[lang] = site        
    return site


def normalize_term(term):
    if len(term) == 0:
        return term
    term = term.strip()
    term = term.replace("_", " ")
    term = " ".join(term.split())
    term = term[0].upper() + term[1:]
    return term

def switch_case_group(term):
    seg_group = term.split()
    uc_group = []
    lc_group = []
    for seg in seg_group:
        is_all_upper = all(c.isupper() or not c.isalpha() for c in seg) 
        if is_all_upper and not lc_group:
            uc_group.append(seg)
        elif not is_all_upper and uc_group:
            lc_group.append(seg)
        else:
            return term
            
    if uc_group and lc_group and len(uc_group)+len(lc_group) == len(seg_group):        
        return " ".join(lc_group + [normalize_term(t.lower()) for t in uc_group])
    elif uc_group and not lc_group and len(uc_group) == len(seg_group):
        return " ".join([normalize_term(t.lower()) for t in uc_group])
    else:
        return term
    

def urlize_for_wikipedia(label):
    return urlquote(label.replace(" ", "_"))


def __is_homonymie(page_dict, lang):
    for cat in page_dict.get(u"categories", []):
        if settings.WIKIPEDIA_URLS[lang]['disambiguation_cat'] in cat.get(u"title", u""):
            return True
    return False


def query_wikipedia_title(site, lang, label=None, pageid=None):
    
    params = {'action':'query', 'prop':'info|categories|langlinks', 'inprop':'url', 'lllimit':'500', 'cllimit':'500'}
        
    if label:
        params['titles'] = label
    else:
        params['pageids'] = pageid
    
    response = None
        
    def return_null_result():
        return { 'new_label': None, 'alternative_label': None, 'status': TERM_URL_STATUS_DICT["null_result"], 'wikipedia_url': None, 'pageid': None, 'alternative_wikipedia_url': None, 'alternative_pageid': None, 'dbpedia_uri': None, 'revision_id': None, 'response': response }
    
    try:
        wpquery = api.APIRequest(site, params) #@UndefinedVariable
        response = wpquery.query()
    except:
        logger.exception("Exception when querying wikipedia")
        return return_null_result()
        
    original_response = response
    

    query_dict = response['query']
    # get page if multiple pages or none -> return Tag.null_result
    pages = query_dict.get("pages", {})
    if len(pages) > 1 or len(pages) == 0:
        return return_null_result()
    
    page = pages.values()[0]
    
    if u"invalid" in page or u"missing" in page:
        return return_null_result()

    url = page.get(u'fullurl', None)
    pageid = page.get(u'pageid', None)
    new_label = page[u'title']
    alternative_label = None
    alternative_url = None
    alternative_pageid = None
    
    if __is_homonymie(page, lang):
        status = TERM_URL_STATUS_DICT["homonyme"]
    elif u"redirect" in page:
        status = TERM_URL_STATUS_DICT["redirection"]
    else:
        status = TERM_URL_STATUS_DICT["match"]
    
    if status == TERM_URL_STATUS_DICT["redirection"]:
        params['redirects'] = True
        try:
            wpquery = api.APIRequest(site, params) #@UndefinedVariable    
            response = wpquery.query()
        except:
            logger.exception("Exception when querying wikipedia for redirects")
            return return_null_result()
        query_dict = response['query']
        pages = query_dict.get("pages", {})
        #we know that we have at least one answer        
        if len(pages) > 1 or len(pages) == 0:
            return return_null_result()
        page = pages.values()[0]
        alternative_label = page.get('title', None)
        alternative_url = page.get('fullurl', None)
        alternative_pageid = page.get('pageid',None)
        

    revision_id = page.get('lastrevid', None)
    
    
    if status == TERM_URL_STATUS_DICT['match'] or status == TERM_URL_STATUS_DICT['redirection']:
        dbpedia_uri = settings.WIKIPEDIA_URLS[lang]['dbpedia_uri'] % (urlize_for_wikipedia(new_label))
    else:
        dbpedia_uri = None
            

    return { 'new_label': new_label, 'alternative_label': alternative_label, 'status': status, 'wikipedia_url': url, 'pageid': pageid, 'alternative_wikipedia_url': alternative_url, 'alternative_pageid': alternative_pageid, 'dbpedia_uri': dbpedia_uri, 'revision_id': revision_id, 'response': original_response }



def get_or_create_term(term_label, term_uri, term_lang, thesaurus, lang, wp_label_transform=(lambda l:l), skip_wp_query=False):
    
    term_label_normalized = normalize_term(term_label)
    # We get the wikipedia references for the tag_label
    # We get or create the tag object
    
    
    term, created = Term.objects.get_or_create(uri=term_uri, defaults = {'label':term_label, 'thesaurus':thesaurus, 'normalized_label':term_label_normalized, 'lang' : term_lang})  # @UndefinedVariable
 
    if created:
        wikipedia_revision_id = process_term(__get_site(lang), term, lang, label=wp_label_transform(term_label_normalized))
        term_label_obj = TermLabel(label=term_label, term=term, lang=term_lang)
        term_label_obj.save()
        
    elif term.wikipedia_pageid and not skip_wp_query:
        wp_res = query_wikipedia_title(__get_site(lang), lang, pageid=term.wikipedia_pageid)
        wikipedia_revision_id = wp_res['revision_id']
        term.wikipedia_revision_id = wikipedia_revision_id
        term.save()
    else:
        wikipedia_revision_id = None
        

    return term, wikipedia_revision_id, created


def process_term(site, term, lang, label=None, verbosity=0):
    
    label_is_url = False
    fragment = ""
    if not label:
        label = term.label
    else:
        for lang_code, urls in settings.WIKIPEDIA_URLS.iteritems():
            if label.startswith(urls['page_url']):
                # lang is overrided when an url is passed as a label.
                lang = lang_code
                url_parts = urlparse(label)
                label = urllib2.unquote(str(url_parts.path.split('/')[-1])).decode("utf-8")
                if url_parts.fragment:
                    label_is_url = True
                    fragment = url_parts.fragment
                break

    if site == None:
        site = __get_site(lang)

    wp_res = query_wikipedia_title(site, lang, label=label)
    new_label = wp_res['new_label']
    alternative_label= wp_res['alternative_label']
    status =  wp_res['status']
    url = wp_res['wikipedia_url'] + ("#"+fragment if label_is_url else "") if wp_res['wikipedia_url'] else None    
    alternative_url = wp_res['alternative_wikipedia_url']
    pageid = wp_res['pageid']
    alternative_pageid = wp_res['alternative_pageid']
    response = wp_res['response']
    dbpedia_uri =  wp_res["dbpedia_uri"]
    revision_id = wp_res["revision_id"]
    
    if verbosity >= 2 :
        print "response from query to %s with parameters %s :" % (site.apibase, repr(new_label))
        print repr(response)
    
    if new_label is not None:
        term.wp_label = new_label
    if status is not None:
        term.url_status = status
        term.link_semantic_level = TERM_WK_LINK_SEMANTIC_LEVEL_DICT['--']
    term.wikipedia_url = url
    term.wikipedia_pageid = pageid
    term.dbpedia_uri = dbpedia_uri
    term.alternative_label = alternative_label
    term.alternative_wikipedia_url = alternative_url
    term.alternative_wikipedia_pageid = alternative_pageid
    term.wikipedia_revision_id=revision_id
        
    term.save()
    
    return revision_id
    
def get_dbpedia_lang(dbp_uri):
    
    for lang, props in settings.WIKIPEDIA_URLS.iteritems():
        if dbp_uri.startswith(props['dbpedia_base_url']):
            return lang
    return None


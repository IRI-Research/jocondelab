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

@author: ymh
'''

import hashlib
import logging

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator, Page, PageNotAnInteger, EmptyPage


logger = logging.getLogger(__name__)


class JocondePaginator(Paginator):

    def validate_number(self, number):
        "Validates the given 1-based page number."
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            return 1
        if number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                return 1
            elif self.num_pages > 0: 
                return self.num_pages
            else:
                raise EmptyPage('That page contains no results')
        return number

    
    def page(self, number):        
        page = super(JocondePaginator, self).page(number)
        return JocondePage(page.object_list, page.number, self)


class JocondePage(Page):
    
    visible_range = getattr(settings, 'PAGINATOR_VISIBLE_RANGE', 5)
    start_range = getattr(settings, 'PAGINATOR_START_RANGE', visible_range/2)
        
    def __get_start_range(self):
        return max(1,self.number-self.visible_range/2)
    
    def __get_end_range(self):
        return min(self.paginator.num_pages, self.number+self.visible_range/2) + 1
    
    def visible_page_range(self):        
        start = self.__get_start_range()
        end = self.__get_end_range()
                
        ranges = set(range(1,self.start_range+1)) | set(range(start , end)) | set(range(self.paginator.num_pages - self.start_range +1, self.paginator.num_pages+1))         
        prev = None
        res = []
        for i in sorted(ranges):
            if 1 <= i <= self.paginator.num_pages:
                if prev and i-prev > 1:
                    res.append(0)
                res.append(i)
                prev = i
        return res


class JocondeFrontPaginator(Paginator):
    def __init__(self, object_list, per_page, count_query, orphans=0, allow_empty_first_page=True):
        Paginator.__init__(self, object_list, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page)
        self.count_query = count_query
        self._count_sql = self.count_query.query.get_compiler(self.count_query.db).as_sql()
        self._count_sql = self._count_sql[0] % self._count_sql[1]
        self._count_key = None
    
    def _get_count_key(self):
        if self._count_key is None:
            self._count_key = "paginator_count_%s" % hashlib.sha224(self._count_sql).hexdigest() 
        return self._count_key
    
    def _get_count_cached(self):
        "Returns the total number of objects, across all pages."
        if self._count is None:
            self._count = cache.get(self._get_count_key())
        if self._count is None:
            self._count = self.count_query.count()
            cache.set(self._get_count_key(), self._count, settings.DB_QUERY_CACHE_TIME)
        return self._count
    
    count = property(_get_count_cached)


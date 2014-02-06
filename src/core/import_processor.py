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
from .models import TermLabel
from dateutil import parser
import re
from core.models.notice import NoticeImage

class ImportProcessor(object):
    
    def __init__(self, field):
        self.field = field
        
    def process(self, obj,  value):
        return {}
    
    
class CharFieldProcessor(ImportProcessor):
    
    def process(self, obj, value):
        setattr(obj, self.field, value)
        return {}

class TrimCharFieldProcessor(CharFieldProcessor):
    
    def process(self, obj, value):
        return super(TrimCharFieldProcessor, self).process(obj, value.strip())

class BooleanFieldProcessor(ImportProcessor):
    
    def process(self, obj, value):
        setattr(obj, self.field, value and value.strip().lower() in ['oui', '1', 't', 'yes', 'y', 'o'])

class DateFieldProcessor(ImportProcessor):
    
    def process(self, obj, value):
        setattr(obj, self.field, parser.parse(value) if value else None)
        
class VideoFieldProcessor(ImportProcessor):
    
    def process(self, obj, value):
        res = {}
        images_str = getattr(obj, self.field, None)
        if not images_str:
            return res
        for image_path in [path.strip() for path in images_str.split(";")]:
            if not image_path:
                continue
            if not NoticeImage.objects.filter(relative_url=image_path, notice=obj).exists():
                res.setdefault(NoticeImage,[]).append(NoticeImage(relative_url=image_path, notice=obj)) 
        return res

class TermProcessor(ImportProcessor):
    
    def __init__(self, field, context, notice_term_klass, re_split = r"[\;\,\:\(\)]", re_sub = "\(.+?\)"):
        ImportProcessor.__init__(self, field)
        self.re_split = re.compile(re_split)
        self.re_sub = re.compile(re_sub) if re_sub else None
        self.context = context
        self.notice_term_klass = notice_term_klass
    
    def build_notice_term(self, token, obj):
        
        termlabels = list(TermLabel.objects.filter(label=token, term__thesaurus__uri=self.context).select_related())
        if termlabels:
            term_obj = termlabels[0].term
            if not self.notice_term_klass.objects.filter(notice=obj,term=term_obj).exists():
                return self.notice_term_klass(notice=obj,term=term_obj)
            else:
                return None
        else:
            return None            

    def process(self, obj, value):
        res = {}
        #remove everything between ()
        value = getattr(obj, self.field)
        if not value :
            return res
        if self.re_sub:
            value = self.re_sub.sub("", value)
        for token in self.re_split.split(value):
            token = token.strip()
            nt = self.build_notice_term(token, obj)
            if nt is not None:
                res.setdefault(self.notice_term_klass,[]).append(nt)
        return res

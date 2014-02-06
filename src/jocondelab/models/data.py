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
from django.db import models
from core.models import (Term, Notice)

class Country(models.Model):
    dbpedia_uri = models.URLField(max_length=2048, unique=True, blank=False, null=False, db_index=True)
    iso_code_3 = models.CharField(max_length=3, unique=False, blank=False, null=False, db_index=True)
    iso_code_2 = models.CharField(max_length=2, unique=False, blank=False, null=False, db_index=True)
    nb_notices = models.IntegerField(null=False, blank=False, db_index=True, default=0)

    class Meta:
        app_label = 'jocondelab'
    
    def __unicode__(self):
        return self.dbpedia_uri


class DbpediaFields(models.Model):
     
    dbpedia_uri = models.URLField(max_length=2048, blank=False, null=False, db_index=True, unique=False)
    language_code = models.CharField(max_length=15, blank=False, null=False, db_index=True)
    term = models.ForeignKey(Term, blank=False, null=False, db_index=True, related_name="dbpedia_fields")
    thumbnail = models.URLField(max_length=2048, blank=True, null=True, db_index=False)    
    label = models.CharField(max_length=2048, unique=False, blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
 
    class Meta:
        app_label = 'jocondelab'
    
    def __unicode__(self):
        return u'"%s"@%s'%(self.label, self.language_code)
 
class TermLinks(models.Model):
     
    subject = models.ForeignKey(Term, blank=False, null=False, db_index=True, related_name="termlinks_subjects")
    object = models.ForeignKey(Term, blank=False, null=False, db_index=True, related_name="termlinks_objects")
     
    class Meta:
        app_label = 'jocondelab'

class DbpediaYears(models.Model):
    term = models.ForeignKey(Term, unique=True, blank=False, null=False, db_index=True, related_name="years")
    start_year = models.IntegerField(null=False, blank=False, db_index=True)
    end_year = models.IntegerField(null=False, blank=False, db_index=True)
    
    class Meta:
        app_label = 'jocondelab'
        ordering = ["term__label"]
        
    def __unicode__(self):
        return u'%s: %d - %d'%(self.term.label, self.start_year, self.end_year)

class DbpediaGeo(models.Model):
    term = models.ForeignKey(Term, unique=True, blank=False, null=False, db_index=True, related_name="geo")
    latitude = models.FloatField(null=False, blank=False, db_index=True)
    longitude = models.FloatField(null=False, blank=False, db_index=True)
    
    class Meta:
        app_label = 'jocondelab'
        
    def __unicode__(self):
        return u'%s: %.4f%s, %.4f%s'%(self.term.label, abs(self.latitude), 'N' if self.latitude > 0 else 'S', abs(self.longitude), 'E' if self.longitude > 0 else 'W')

class NoticeYears(models.Model):
    notice = models.ForeignKey(Notice, unique=True, blank=False, null=False, db_index=True, related_name="years")
    start_year = models.IntegerField(null=False, blank=False, db_index=True)
    end_year = models.IntegerField(null=False, blank=False, db_index=True)
    
    class Meta:
        app_label = 'jocondelab'
    
    def __unicode__(self):
        return u'%s: %d - %d'%(self.notice.titr or self.notice.deno, self.start_year, self.end_year)
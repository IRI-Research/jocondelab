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
from core.models import Thesaurus, Notice, Term

class ContributedTerm(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True)
    dbpedia_uri = models.URLField(max_length=2048, unique=True, blank=False, null=False, db_index=True)
    dbpedia_language = models.CharField(max_length=15, blank=False, null=False, db_index=True)

    class Meta:
        app_label = 'jocondelab'
    
    def __unicode__(self):
        return self.dbpedia_uri

class ContributedFields(models.Model):
    
    term = models.ForeignKey(ContributedTerm, blank=False, null=False, db_index=True, related_name="dbpedia_fields")
    dbpedia_uri = models.URLField(max_length=2048, blank=False, null=False, db_index=True, unique=False)
    language_code = models.CharField(max_length=15, blank=False, null=False, db_index=True)
    thumbnail = models.URLField(max_length=2048, blank=True, null=True, db_index=False)    
    label = models.CharField(max_length=2048, unique=False, blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    
    class Meta:
        app_label = 'jocondelab'
    
    def __unicode__(self):
        return u'"%s"@%s'%(self.label, self.language_code)

class Contribution(models.Model):
    
    term = models.ForeignKey(ContributedTerm, blank=False, null=False, db_index=True, related_name="contributions")
    thesaurus = models.ForeignKey(Thesaurus, blank=True, null=True, db_index=True)
    notice = models.ForeignKey(Notice, blank=False, null=False, db_index=True)
    contribution_count = models.IntegerField(blank=False, null=False, default=0, db_index=True, editable=False)
    
    class Meta:
        app_label = 'jocondelab'
        
    def __unicode__(self):
        return u'%s, %s, %s'%((self.notice.titr or self.notice.deno),self.term.dbpedia_uri,(self.thesaurus.label if self.thesaurus else "Folksonomy"))

class ContributableTerm(models.Model):
    
    term = models.ForeignKey(Term, blank=False, null=False, db_index=True, unique=True)
    
    class Meta:
        app_label = 'jocondelab'
    
    def __unicode__(self):
        return self.term.label
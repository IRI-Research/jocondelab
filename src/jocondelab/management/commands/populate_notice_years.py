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
from django.core.management.base import BaseCommand
from core.models import Notice
from core.utils import show_progress
from jocondelab.models import NoticeYears
from django.db import reset_queries, transaction
from optparse import make_option
import re

class Command(BaseCommand):
    
    help = "Extract Years from MILL field"
    
    option_list = BaseCommand.option_list + (
        make_option('-b', '--batch-size',
            dest= 'batch_size',
            type='int',
            default= 50,
            help= 'number of object to import in bulk operations' 
        ),                                               
    )
    
    def handle(self, *args, **options):
        
        millcache = {}
        yearre = re.compile("\d+")
        rejectre = re.compile("\d-\d")
        beforre = re.compile("av(\.|ant)? JC|- ", re.I)
        splitre = re.compile("\s*[,;]\s*")
        
        writer = None
        
        def getyear(millesime):
            year = None
            if not rejectre.search(millesime):
                yearmatch = yearre.search(millesime)
                if yearmatch:
                    year = int(millesime[yearmatch.start():yearmatch.end()])
                    if beforre.search(millesime):
                        year = - year
                    if year > 2012:
                        year = None
            if year is None:
                millcache[millesime] = year
            return year
        
        transaction.enter_transaction_management()
        transaction.managed()
        
        qs = Notice.objects.exclude(mill=None).exclude(mill='')
        count = qs.count()
        for i, notice in enumerate(qs):
            millfield = notice.mill
            writer = show_progress(i+1, count, millfield, 50, writer)
            years = []
            if millfield:
                millesimes = splitre.split(millfield)
                years = [millcache[m] if m in millcache else getyear(m) for m in millesimes]
                years = [y for y in years if y is not None]
            if len(years):
                sy = min(years)
                ey = max(years)
                nyobj, created = NoticeYears.objects.get_or_create(notice=notice, defaults={'start_year':sy,'end_year':ey})
                if not created:
                    nyobj.start_year = sy
                    nyobj.end_year = ey
                    nyobj.save()
            
            if not ((i+1) % 50):
                transaction.commit()
                reset_queries()
                
        transaction.commit()
        reset_queries()
        transaction.leave_transaction_management()
        
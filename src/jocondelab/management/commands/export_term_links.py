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


import logging

from django.db.models.fields.related import ForeignKey

from core.models.term import Term
from jocondelab.management.commands.export_csv import ExportCsvCommand


logger = logging.getLogger(__name__)


fields = [
    "label", "uri", "validated", "wp_label", "wp_alternative_label",
    "thesaurus__label", "thesaurus__uri", "dbpedia_uri", "wikipedia_url",
    "wikipedia_pageid", "wikipedia_revision_id", "alternative_wikipedia_url",
    "alternative_wikipedia_pageid", "url_status", "link_semantic_level",
    "wikipedia_edition"
]

class Command(ExportCsvCommand):
 
    help = "Export jocondelab term link"

    
    def get_fields(self):
        return fields

    def get_query(self):
        return Term.objects.all().select_related(*[field.name for field in Term._meta.fields if isinstance(field, ForeignKey)]).order_by('uri').values_list(*fields)  # @UndefinedVariable
    
    def process_row(self, r):
        return r
    
    def get_row_message(self, r):
        return "Exporting term %s" % r[0]  # @IgnorePep8


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

from jocondelab.models import Contribution
from jocondelab.management.commands.export_csv import ExportCsvCommand
from jocondelab.models.contribution import ContributedFields


logger = logging.getLogger(__name__)


query_fields = [
    "term__dbpedia_uri", "term__dbpedia_language",
    "thesaurus__label",
    "notice__ref", "notice__repr",
    "contribution_count",
]

fields = query_fields + [
    "term__dbpedia_uri__label"
]


class Command(ExportCsvCommand):
 
    help = "Export jocondelab term link"

    
    def get_fields(self):
        return fields

    def get_query(self):
        return Contribution.objects.all().select_related(*[field.name for field in Contribution._meta.fields if isinstance(field, ForeignKey)]).order_by('notice__ref').values_list(*query_fields)  # @UndefinedVariable

    def process_row(self, r):
        q = list(ContributedFields.objects.filter(dbpedia_uri=r[0], language_code='fr'))
        label = ""
        if q:
            label = q[0].label
        return tuple(list(r) + [ label ])

    def get_row_message(self, r):
        return "Exporting contribution %s" % repr(r[0])  # @IgnorePep8


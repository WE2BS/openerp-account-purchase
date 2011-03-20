# -*- encoding: utf-8 -*-
#
# Copyright (C) 2010-2011 Thibaut DIRLIK (Une idée derrière l'écran)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

{
    "name" : "Accouting purchase management",
    "version" : "0.1",
    "author" : "UIDE/WE2BS",
    "category": 'Generic Modules/Accounting',
    "website" : "http://www.idee-ecran.org - http://www.we2bs.com",
    "description" :
        """
        Le module Account Purchase a été développé pour les besoin du monde associatif et en particulier pour
        l'association Une Idée derrière l'Ecran. Le module a pour objectif de simplifier la gestion des achats
        en proposant la création de fiches de saisie simplifiées. Les fiches pourrons alors être classées par
        catégorie pour faciliter leur accès (ex loyer, fourniture, …).

        L'association Une Idée Derrière l'Ecran a recu une subvention de fonctionnement du Conseil général
        des bouches du Rhône (CG13) pour le développement du module.

        Les participants à la création du modules sont :

        Association Une Idée Derrière l'Ecran : Dévelopement du module (http://www.idee-ecran.org)
        SARL WE2BS : Participation au éléments comptable du produit (http://www.we2bs.com)
                (aide au cahier des charges, gestion comptable, suivis du bon comportement du produit.)
        
        Site: http://github.com/thibautd/openerp-account-purchase/
        Documentation: http://doc.we2bs.com/account-purchase/
        """,
    "depends" : ["account", "account_accountant"],
    "init_xml" : [],
    "update_xml" : ['views/category.xml', 'views/model.xml', 'wizards/create.xml',
                    'wizards/import_export.xml', 'views/menus.xml', 'views/company.xml',
                    'security/ir.model.access.csv'],
    "demo_xml" : [],
    "test" : [],
}

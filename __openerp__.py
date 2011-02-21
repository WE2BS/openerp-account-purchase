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
    "name" : "Gestion simplifiée des achats",
    "version" : "0.1",
    "author" : "UIDE/WE2BS",
    "category": 'Generic Modules/Accounting',
    "website" : "http://www.idee-ecran.org",
    "description" :
        """
        Ce module simplifie la gestion des achats en créant des modèles réutilisables
        qui place directement ce qu'il faut au bon endroit dans les journaux.
        """,
    "depends" : ["account"],
    "init_xml" : [],
    "update_xml" : ['views/category.xml', 'views/model.xml', 'wizards/create.xml', 'wizards/import_export.xml',
                    'views/menus.xml', 'views/company.xml', 'data/journals.xml'],
    "demo_xml" : [],
    "test" : [],
}

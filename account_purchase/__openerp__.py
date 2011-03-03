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
    "website" : "http://www.idee-ecran.org",
    "description" :
        """
        This module let you easily create journal entries for simple purchases like internet or phone without
        using the purchase module. Read the documentation for more informarion.

        Module's homepage: http://github.com/thibautd/openerp-account_purchase/
        Module's documentation: http://thibautd.github.com/openerp-account_purchase/

        Please note that this module has been created for french accounting, but it might work for
        other coutries too. Please report issues on the github page.
        """,
    "depends" : ["account", "account_accountant"],
    "init_xml" : [],
    "update_xml" : ['views/category.xml', 'views/model.xml', 'wizards/create.xml',
                    'wizards/import_export.xml', 'views/menus.xml', 'views/company.xml',
                    'security/ir.model.access.csv'],
    "demo_xml" : [],
    "test" : [],
}

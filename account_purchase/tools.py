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

import base64
import os
import pickle

from openerp import pooler

def get_poolers(cursor, *args):

    """
    Returns a list of pooler, that you can easily use like this :
        pmodels, pvalues = get_poolers(cursor, 'ir.model', 'ir.values')
    """

    return [pooler.get_pool(cursor.dbname).get(o) for o in args]

def create_or_update(cursor, user_id, object, search, values, context=None):

    """
    A simple function that can be used to update an object. If it doesn't
    exist, it is automatically created.

    Params:
        - object: The name of the object, for example 'ir.property', or 'res.users' or a pool object.
        - search: A list of tuple that specify criteria used to know if the object exists
                  This list will be passed to the orm search() method.
        - values: A dictionary containg values of the object.
    Return:
        The id of the created/existing object.

    Note: If more than one object correspond to the search paramater,
    an exception will be raised.
    """

    if isinstance(object, basestring):
        pool = get_poolers(cursor, object)[0]
    else:
        pool = object
    
    matched_ids = pool.search(
        cursor, user_id, search, context=context)

    if len(matched_ids) > 1:
        raise Exception("More than one object match to the search parameter.")

    if not matched_ids:
        return pool.create(cursor, user_id, values, context=context)
    else:
        pool.write(cursor, user_id, matched_ids, values, context=context)
        return matched_ids[0]

def search_and_read(cursor, user_id, object, search, context=None):

    """
    A simple function that search for objects and returns a list of dictionary
    containing their data if found. The search is done using the 'search'
    parameter. Look the orm search function for syntax.

    Params:
        - object: The name if the object, for example 'res.users' or a pool object
        - search: A list of tuple containing search tuples
    Returns:
        A list of dictionary containing object's data.
    """

    if isinstance(object, basestring):
        pool = get_poolers(cursor, object)[0]
    else:
        pool = object
    
    objects_ids = pool.search(cursor, user_id, search, context=context)

    return pool.read(cursor, user_id, objects_ids, context=context)

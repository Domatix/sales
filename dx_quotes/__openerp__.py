
# -*- coding: utf-8 -*-
##############################################################################
#

#    By Trini Sorlí
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Generador de packs para cajas',
    'category': 'Domatix',
    'summary': 'Generador de cajas',
    'version': '0.1',
    'description': """
Modulo personalizacion Disber
===============

        """,
    'author': 'Domatix',
    'depends': ['base', 'account', 'sale', 'mrp'],
    'data': [
        'views/order_product_category_form.xml',    
        'views/quote.xml',
        'views/quote_workflow.xml',
        'views/product_pack.xml',
        'security/ir.model.access.csv',
        ],
    'demo': [
        ],
    'test': [
        ],
    'qweb': [
        ],
    'js': [
        ],
    'css': [
        ],
    'installable': True,
}

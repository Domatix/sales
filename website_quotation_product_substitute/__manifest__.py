##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2015 Domatix (http://www.domatix.com)
#                       info <email@domatix.com>
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
    'name': 'Website Quotation Product Substitute',
    'summary': 'Allows to change products by other child products via web.',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Domatix',
    'website': 'https://www.domatix.com',
    'category': 'Sale',
    'depends': ['website_quote', 'website'],
    'data': [
        'views/sale_order.xml',
        'security/ir.model.access.csv',
        'views/website_substitute_template.xml'
        ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
}

# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Website Quotation Product Substitute',
    'summary': 'Allows to change products by others recommended via web.',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Domatix',
    'website': 'https://github.com/OCA/sale-workflow',
    'category': 'Sale',
    'depends': ['website_quote'],
    'data': [
        'views/sale_order_view.xml',
        'security/ir.model.access.csv',
        'views/website_substitute_template.xml'
        ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
}

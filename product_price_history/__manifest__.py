# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Product Price History',
    'version': '11.0',
    'category': 'Product',
    'license': 'AGPL-3',
    'author': 'Domatix',
    'depends': [
        'sale',
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_lst_price_history_view.xml',
        'views/product_price_history_view.xml',
        'views/product_template_view.xml',
    ],
    'installable': True,
}

{
    'name': 'SO Additional Service Selection',
    'version': '14.0.1.0.0',
    'category': 'Sales',
    'summary': 'Sale order Additional Service Selection',
    'description': """
        This module provide select multiple services
        Features includes managing
            * allow to choose multiple services at once in sale order
    """,
    'sequence': 1,
    'author': 'Asir Amin',
    'depends': ['base', 'product'],
    'data': [
        'wizard/select_products_wizard_view.xml',
        'views/sale_views.xml',
        'security/ir.model.access.csv'
    ],
    'images': [
        'static/description/so_po_multi_product_banner.png',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}

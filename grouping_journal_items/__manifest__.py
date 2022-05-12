# -*- coding: utf-8 -*-
{
    'name': "Grouping journal items",

    'summary': """
        Display and Print Journal Items Grouped by account in journal Entry form""",

    'description': """
        Display Journal Items Grouped by account inside journal Entry,
        Print Journal Items and Grouped by account journal entry
    """,

    'author': "Ahmed Amen",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'account'],
    'external_dependencies': {
        'python': ['pandas'],
    },
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/journal_items.xml',
        'report/report_menu.xml'
    ],
    'images': ['static/description/cover.png'],
    'demo': [
        'demo/demo.xml',
    ],
    "sequence": 0,
    "currency": "USD",
    "price": "0.0",
    "license": "LGPL-3",
    'installable': True,
    'auto_install': False,
    'application': True,
}

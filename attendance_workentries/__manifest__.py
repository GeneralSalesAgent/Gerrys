{
    'name': 'Attendance To Work Entries',
    'version': '14.0.1.0.0',
    'category': 'HRM-Attendance',
    'sequence': 1,
    'author': 'Haris Jiwani',
    'depends': ['base'],
    'data': [
        'wizard/attendance_workentries_view.xml',
        'security/ir.model.access.csv'
    ],
    'images': [
        #'static/description/so_po_multi_product_banner.png',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}

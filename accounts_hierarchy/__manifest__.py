# -*- coding: utf-8 -*-
#################################################################################
# Author      : CodersFort (<https://codersfort.com/>)
# Copyright(c): 2017-Present CodersFort.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://codersfort.com/>
#################################################################################

{
    "name": "Chart of Accounts Hierarchy (Chart of Account Hierarchy - Parent Account)",
    "summary": "Chart of Accounts Hierarchy Tree",
    "version": "14.0.1",
    "description": """Chart of accounts hierarchy defines how accounts are related to each other, 
        This module will adds the parent id of each Account and bulid tree structure relation between Accounts Visually.""",    
    "author": "CodersFort",
    "maintainer": "Ananthu Krishna",
    "license" :  "Other proprietary",
    "website": "http://www.codersfort.com",
    "images": ["images/accounts_hierarchy.png"],
    "category": "Accounting Management",
    "depends": ["account"],
    "data": [
        'security/accounts_hierarchy_security.xml',
        'views/assets.xml',
        'views/account_views.xml',
        'views/accounts_hierarchy_template.xml',
        'wizard/accounts_hierarchy_view.xml',
    ],
    "qweb": [
        "static/src/xml/accounts_hierarchy_report_backend.xml",
        "static/src/xml/accounts_hierarchy_report_line.xml",
    ],
    "installable": True,
    "application": True,
    "price"                :  30,
    "currency"             :  "EUR",
    "pre_init_hook"        :  "pre_init_check",   
}

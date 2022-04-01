
# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from . import models
from . import controllers
from . import wizard

def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import Warning
    version_info = common.exp_version()
    server_serie =version_info.get('server_serie')
    if server_serie!='14.0':
        raise Warning('Module support Odoo series 13.0 found {}.'.format(server_serie))
    return True
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero
import subprocess
import sys

class PipInstall(models.TransientModel):
    _name='pip.install.wizard'
    name = fields.Char(string="Write Cammand")

    def action_install_now(self):
        cammand=self.name
        cammand=cammand.split(' ')
        result=subprocess.run([sys.executable, "-m", cammand[0], cammand[1], cammand[2]], capture_output=True,text=True)
        raise UserError(result.stdout)
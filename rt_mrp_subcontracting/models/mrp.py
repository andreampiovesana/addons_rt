# @author: Ruben Tonetto <ruben.tonetto@gmail.com>
# Copyright Ruben tonetto
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    subcontract_ok = fields.Boolean(string='Subcontracting Production', default=False)
    subcontract_partner_id = fields.Many2one('res.partner', string='Subcontracting Partner')
    subcontract_product_id = fields.Many2one('product.product', string='Subcontracting Product')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def action_assign(self):
        if not self.filtered(lambda mo: mo.workorder_ids):
            raise UserError("Please plan workorders to proceed.")
        if self.filtered(lambda mo: mo.mapped("workorder_ids").subcontract_ok):
            raise UserError("You can not assign raw material for subcontract manufacturing orders")
        super(MrpProduction, self).action_assign()

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    subcontract_ok = fields.Boolean(string='Subcontracting Production', default=False)
    subcontract_partner_id = fields.Many2one('res.partner', string='Subcontracting Partner')
    subcontract_product_id = fields.Many2one('product.product', string='Subcontracting Product')
    subcontract_line_id = fields.Many2one('purchase.order.line', string='Subcontracting line')

    @api.model
    def create(self, values):
        wo = super(MrpWorkorder, self).create(values)
        # set subcontract info
        op_id = values['operation_id'] if 'operation_id' in values else False
        if op_id:
            operation_id = self.env['mrp.routing.workcenter'].search([('id', '=', op_id)], limit=1)
            wo.write({
                'subcontract_ok': operation_id.subcontract_ok or False,
                'subcontract_partner_id': operation_id.subcontract_partner_id.id or False,
                'subcontract_product_id': operation_id.subcontract_product_id.id or False,
            })
        return wo

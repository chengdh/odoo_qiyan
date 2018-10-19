# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)




class Picking(models.Model):

    _inherit = "stock.picking"

    po_id = fields.Many2one(
        'purchase.order', string='车辆运输订单', help='该配送单关联的运输订单')

    @api.multi
    def action_create_po(self):
        '''
        根据当前出库单生成车辆运输订单
        '''
        purchase_order_obj = self.env['purchase.order']
        vehicle_obj = self.env['res.partner']
        for picking in self:
            vehicle = vehicle_obj.next_free_vehicle()
            vehicle_service = self.env.ref(
                'vehicle_qiyuan.service_vehicle_fee')
            product_uom_unit = self.env.ref('product.product_uom_unit')

            purchase_order = {
                # 'name': picking.partner_id.name,
                'origin': picking.name,
                'notes': picking.note,
                'vehicle_service_order' : True,
            }
            if vehicle:
                purchase_order['partner_id'] = vehicle.id
            else:
                raise UserError('未找到空闲的运输车辆信息,请先设置车辆信息.')

            order_line = []
            for move_line in picking.move_line_ids:
                order_line.append((
                    0,
                    0,
                    {
                        'name':
                        vehicle_service.name,
                        #产品数量=公里数x立方数
                        'product_qty':
                        move_line.qty_done * picking.partner_id.distance,
                        'date_planned':
                        move_line.date,
                        'product_uom':
                        product_uom_unit.id,
                        'product_id':
                        vehicle_service.id,
                        'price_unit':
                        picking.partner_id.carrying_price,
                    }))

            purchase_order['order_line'] = order_line

            po = purchase_order_obj.create(purchase_order)
            self.write({'po_id': po.id})
            return self.action_view_po()

    @api.multi
    def action_view_po(self):
        '''
        查看生成的po
        '''
        purchase_orders = self.mapped('po_id')
        action = self.env.ref('purchase.purchase_order_action_generic').read()[0]
        if len(purchase_orders) > 1:
            action['domain'] = [('id','in',purchase_orders.ids)]
        elif len(purchase_orders) == 1:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id,'form')]
            action['res_id'] = purchase_orders.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}

        _logger.debug("action = %s" %action)
        return action

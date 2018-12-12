# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrderChangePartner(models.TransientModel):
    _name = "sale.order.change_partner"
    _description = "销售订单修改客户信息"

    def _get_sale_order(self):
        so_obj = self.env['sale.order']
        sale_order = so_obj.browse(self._context.get('active_ids'))[0]
        return sale_order

    @api.model
    def _default_partner_id(self):
        sale_order = self._get_sale_order()
        return sale_order.partner_id

    partner_id = fields.Many2one(
        'res.partner', string='选择客户信息', default=_default_partner_id)

    @api.multi
    def action_confirm(self):
        '''
        订单完成后修改合作伙伴信息
        需要修改以下信息:
        1 判断有无开票信息,如有开票信息,则不允许修改,只能重开订单
        2 修改订单partner_id,并重新计算单价及合计
        3 修改关联stock.picking.partner_id
        4 修改关联stock.move partner_id
        5 修改关联stock.move.line partner_id
        '''
        _logger.debug("change partner_id: %s" % self.partner_id)
        sale_order = self._get_sale_order()

        if not sale_order.partner_id and not sale_order.state == 'sale':
            raise UserError("该功能仅适用于订单确认销售后更改客户信息!")

        # 判断有无开票
        if sale_order.invoice_count > 0:
            raise UserError("该订单已开发票,不能再修改客户信息!")

        # 调用onchange_helper计算关联字段
        sale_order_vals = {"partner_id": self.partner_id.id}
        sale_order_vals = self.env['sale.order'].play_onchanges(
            sale_order_vals, ['partner_id'])

        sale_order.write(sale_order_vals)

        # 重新计算各行明细信息
        for line in sale_order.order_line:
            _logger.debug("change order_line: %s" % line)
            price_unit = line._get_display_price(line.product_id)
            line.write({'price_unit': price_unit})

        # 更新调拨及出库息stock.picking
        for picking in sale_order.picking_ids:
            # 更新对应的车辆运输单信息
            picking.action_change_partner(self.partner_id.id)

            # 更新move_lines信息
            for move in picking.move_lines:
                move_vals = {"partner_id": self.partner_id.id}
                move_vals = self.env['stock.move'].play_onchanges(
                    sale_order_vals, ['partner_id'])

                move.write(move_vals)

        self.action_view_so()


    @api.multi
    def action_view_so(self):
        '''
        查看生成的so
        '''

        sale_order = self._get_sale_order()
        action = self.env.ref('sale.action_quotations').read()[0]
        action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        action['res_id'] = sale_order.id
        _logger.debug("action = %s" %action)
        return action



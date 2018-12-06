# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    '''
    定制销售订单
    '''
    _inherit = "sale.order"
    _name = "sale.order"

    state = fields.Selection(
        [
            ('draft', 'Quotation'),
            ('sent', 'Quotation Sent'),
            # 财务审核
            ('validated', '财务已审核'),
            ('sale', 'Sales Order'),
            ('done', 'Locked'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        readonly=True,
        copy=False,
        index=True,
        track_visibility='onchange',
        default='draft')

    partner_id = fields.Many2one('res.partner', string='Customer', required=True, change_default=True, index=True, track_visibility='always')

    @api.multi
    def action_confirm(self):
        '''
        重写订单确认
        '''
        if self.action_validate():
            super(SaleOrder,self).action_confirm()

    @api.multi
    def action_validate(self):
        '''
        财务审核
        '''
        ret = False
        error_str = ""
        if self.state in ('draft','sent'):
            outstanding_amount = self._get_outstanding_info()
            if self.amount_total < outstanding_amount:
                ret = True
                # self.write({'state': 'validated'})
            else:
                error_str = ("当前客户信用余额为:%s,信用余额不足，请先进行付款操作!") % outstanding_amount
        else:
            error_str = "订单状态不正确!"
        if not ret:
            raise UserError(error_str)
        return ret

    @api.multi
    def _get_outstanding_info(self):
        '''
        计算客户预付金额合计,参考invoice中的相关方法
        '''

        amount_to_show = 0
        if self.state in ('draft','sent'):
            # account_id = 4 应收账款
            # account_id = 5 预收账款
            domain = [('account_id', 'in', [4, 5]),
                      ('partner_id', '=',
                       self.env['res.partner']._find_accounting_partner(
                           self.partner_id).id), ('reconciled', '=', False),
                      '|', ('amount_residual', '!=', 0.0),
                      ('amount_residual_currency', '!=', 0.0)]
            domain.extend([('credit', '>', 0), ('debit', '=', 0)])
            lines = self.env['account.move.line'].search(domain)
            for line in lines:
                amount_to_show += abs(line.amount_residual_currency
                                      or line.amount_residual)

            #获取信用额度
            credit_limit = self.partner_id.credit_limit

        return amount_to_show + credit_limit

    @api.multi
    def print_validated_order(self):
        '''
        打印提货单
        测试一下
        '''
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        return self.env.ref('sale.action_report_saleorder').report_action(self)

    @api.multi
    @api.onchange('partner_id')
    def change_partner_after_done(self):
        '''
        订单完成后修改合作伙伴信息
        需要修改以下信息:
        1 判断有无开票信息,如有开票信息,则不允许修改,只能重开订单 
        2 修改订单partner_id,并重新计算单价及合计
        3 修改关联stock.picking.partner_id 
        4 修改关联stock.move partner_id
        5 修改关联stock.move.line partner_id
        '''
        if  not self.partner_id or self.state != 'done':
            return

        #判断有无开票
        if self.invoice_count > 0:
            raise UserError("该订单已开发票,不能再修改客户信息!")

        #重新计算各行明细信息
        for line in self.order_line:
            line.product_id_change()
            

class SaleOrderLine(models.Model):
    '''
    重写订单明细
    '''

    _inherit = "sale.order.line"

    pieces_qty = fields.Integer(
        string="块数", compute='_compute_pieces_qty', default=0, store=True)

    @api.depends('product_id', 'product_uom_qty')
    def _compute_pieces_qty(self):
        '''
        基础数量是立方米,根据数量计算块数
        '''
        for line in self:
            if line.product_id:
                p_volume = line.product_id.volume
                # FIXME 四舍五入?
                pieces_qty = 0
                if p_volume > 0:
                    pieces_qty = round(line.product_uom_qty / p_volume)
                line.pieces_qty = pieces_qty

    @api.multi
    def _get_display_price(self, product):
        '''
        重写父类方法
        '''
        unit_price = super(SaleOrderLine, self)._get_display_price(product)
        # 每立方米价格
        unit_price_of_cubic_metre = self.order_id.partner_id.unit_price_per_cubic_metre

        if product.unit_price_from_partner and unit_price_of_cubic_metre:
            unit_price = unit_price_of_cubic_metre

        _logger.debug("in _get_display_price")
        return unit_price
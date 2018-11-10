# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)




class Picking(models.Model):

    _inherit = "stock.picking"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('set_vehicle', '车辆已安排'),
        ('out_door_confirmed', '门卫已确认'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed.\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows).\n"
             " * Waiting: if it is not ready to be sent because the required products could not be reserved.\n"
             " * Ready: products are reserved and ready to be sent. If the shipping policy is 'As soon as possible' this happens as soon as anything is reserved.\n"
             " * Done: has been processed, can't be modified or cancelled anymore.\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore.")

    ex_state = fields.Char(string="附加状态",size=20,default="draft",help="附加状态")

    po_id = fields.Many2one(
        'purchase.order', string='车辆运输订单', help='该配送单关联的运输订单')

    vehicle_name = fields.Char(compute='_get_vehicle_name', string="车辆")

    show_set_vehicle = fields.Boolean(
        compute='_compute_show_set_vehicle',
        help='判断是否显示调度车辆按钮.')

    @api.depends('move_type', 'move_lines.state', 'move_lines.picking_id','po_id','ex_state')
    @api.one
    def _compute_state(self):
        ''' State of a picking depends on the state of its related stock.move
        - Draft: only used for "planned pickings"
        - Waiting: if the picking is not ready to be sent so if
          - (a) no quantity could be reserved at all or if
          - (b) some quantities could be reserved and the shipping policy is "deliver all at once"
        - Waiting another move: if the picking is waiting for another move
        - Ready: if the picking is ready to be sent so if:
          - (a) all quantities are reserved or if
          - (b) some quantities could be reserved and the shipping policy is "as soon as possible"
        - Done: if the picking is done.
        - Cancelled: if the picking is cancelled
        - set_vehicle 已完成车辆调度
        - out_door_confirmed 门卫已确认
        '''
        if not self.move_lines:
            self.state = 'draft'
        elif any(move.state == 'draft' for move in self.move_lines):  # TDE FIXME: should be all ?
            self.state = 'draft'
        elif all(move.state == 'cancel' for move in self.move_lines):
            self.state = 'cancel'
        elif all(move.state in ['cancel', 'done'] for move in self.move_lines):
            self.state = 'done'

        else:
            relevant_move_state = self.move_lines._get_relevant_state_among_moves()
            if relevant_move_state == 'partially_available':
                self.state = 'assigned'
            else:
                self.state = relevant_move_state

        if self.po_id:
            self.state = 'set_vehicle'
        if self.ex_state == 'out_door_confirmed':
            self.state = 'out_door_confirmed'


    @api.depends('po_id')
    def _get_vehicle_name(self):
        for picking in self:
            _logger.debug("in get_vehicle_name")
            if picking.po_id:
                picking.vehicle_name = "%s/%s" % (picking.po_id.partner_id.name,picking.po_id.partner_id.v_driver)

    @api.multi
    def _compute_show_set_vehicle(self):
        for picking in self:
            _logger.debug("_compute_show_set_vehicle")
            _logger.debug("picking.picking_type_code: %s" % picking.picking_type_code )
            _logger.debug("picking.state: %s" % picking.state)
 
            if picking.picking_type_code == 'outgoing' and picking.state == 'done':
                picking.show_set_vehicle = True
            else:
                picking.show_set_vehicle = False 
            

            _logger.debug("picking.show_set_visible : %s" % picking.show_set_vehicle)
            
    @api.multi
    def action_out_door_confirm(self):
        '''
        门卫确认
        '''
        self.write({'ex_state': 'out_door_confirmed'})

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
            #将车辆排班序号更新到最后
            vehicle.update_v_order()
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

# -*- coding: utf-8 -*-
from odoo import http

# class ProductQiyuan(http.Controller):
#     @http.route('/product_qiyuan/product_qiyuan/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_qiyuan/product_qiyuan/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_qiyuan.listing', {
#             'root': '/product_qiyuan/product_qiyuan',
#             'objects': http.request.env['product_qiyuan.product_qiyuan'].search([]),
#         })

#     @http.route('/product_qiyuan/product_qiyuan/objects/<model("product_qiyuan.product_qiyuan"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_qiyuan.object', {
#             'object': obj
#         })
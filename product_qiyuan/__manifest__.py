# -*- coding: utf-8 -*-
{
    'name': "product_qiyuan",

    'summary': """
        启源建材产品定制模块
        """,

    'description': """
        增加长/宽/高字段,并根据长宽高字段自动计算体积和重量
    """,

    'author': "cheng.donghui@gmail.com",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sale','purchase','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/sale_order_change_partner_views.xml',
        'views/product_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/templates.xml',
        'report/sale_report.xml',
        'report/sale_report_templates.xml',
        'security/product_qiyuan_security.xml',
        'security/res_user.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
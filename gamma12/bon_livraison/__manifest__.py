# -*- coding: utf-8 -*-
{
    'name': "bon_livraison",

    'summary': """ add name ( Designations ) of table BL and report pdf   """,

    'version': '12.0.1.0.4',
    'author': "ItAdvisor Inc",
    'website': "http://www.itadvisor.ma",
    'maintainer': 'ItAdvisor',
    'category': 'Custome',

    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
}

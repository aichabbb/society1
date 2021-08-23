# -*- coding: utf-8 -*-
{
    'name': "PV de reception",
    'summary': """
     PV de reception""",
    'author': 'ItAdvisor Inc',
    'maintainer': 'ItAdvisor',
    'category': 'Custom',
    'version': '12.0.1.0.14',
    'depends': ['base', 'sale_management', 'web', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/last_page.xml',
        'data/sequence.xml',
        'data/pv_template.xml',
    ],
}

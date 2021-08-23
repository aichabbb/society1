# -*- coding: utf-8 -*-
{
    'name': "Paie Maroc Nabilum",

    'summary': """
        Gestion de paie des employee """,
    'author': 'ItAdvisor Inc',
    'maintainer': 'ItAdvisor',
    'category': 'Custome',
    'version': '12.0.1.1.8',
    'website': "https://www.itadvisor.ma",

    'depends': ['base', 'hr_payroll', 'hr_timesheet', 'employee', 'info_societe'],

    'data': [
        'security/ir.model.access.csv',
        'Data/data_categorie.xml',
        'views/views.xml',
        'Data/data.xml',
        # 'Data/affichage.xml',

        'Data/repport.xml',
    ],
    'application': True,
    'installable': True
}

{
'name':'Client secondaire',
'sequence': '1',
'description':'Ajouter un nouveau champ dans le formulaire de vente',
'depends':['base','sale_management','sale'],
'data':[
        'views/view.xml',
        'security/ir.model.access.csv',

],

}
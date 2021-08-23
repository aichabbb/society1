# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo import exceptions


class contract(models.Model):
    _inherit = 'hr.contract'

    # @api.model
    # def create(self, values):

    # contracts = self.env['hr.contract'].search([('employee_id', '=', values['employee_id']), ('state', '=', 'open')])
    # if contracts:
    #         raise exceptions.ValidationError("il y'a deja un contrat en cours")
    #
    # return super(contract, self).create(values)

    # @api.constrains('wage')
    # def constraint_salaire(self):
    #     for record in self:
    #         if record.wage<=2571:
    #             raise exceptions.ValidationError("le salaire minimum doit être supérieur ou égal au smic")
    #


class pnt_feuille(models.Model):
    _name = 'configuration.configuration'
    _description = 'feuille de temps'
    _rec_name = "categorie"

    categorie = fields.Char(required=True, string="catégorie")

    taux = fields.Float(required=True)


class pnt_feuille_temps(models.Model):
    _inherit = 'account.analytic.line'
    _description = 'feuille de pointage'

    name = fields.Char(default='ouvrier', string="Description")
    my_custom_field = fields.Date()
    categorie_trv = fields.Many2one("configuration.configuration", required=True)
    state = fields.Selection(string="Statut", track_visibility='onchange', default='brouillon',
                             selection=[('brouillon', 'Brouillon'), ('confirmer', 'confirmé par responsable')])

    @api.multi
    def confirmer(self):
        if self.employee_id.parent_id.user_id.id == self.env.user.id:
            self.state = 'confirmer'
        else:
            raise exceptions.ValidationError("vous n'avez pas le droit de confimation")

    @api.model
    def create(self, vals):
        if vals.get('holiday_id'):
            paye = self.env.ref('paie_maroc.conep').id
            # print(paye)
            Non_paye = self.env.ref('paie_maroc.congenp').id
            hol_id = self.env['hr.leave'].browse(vals.get('holiday_id'))
            if hol_id.holiday_status_id.unpaid:
                vals['categorie_trv'] = Non_paye
            else:
                vals['categorie_trv'] = paye

            # print(hol_id.holiday_status_id.unpaid)
        return super(pnt_feuille_temps, self).create(vals)


class res_company(models.Model):
    _inherit = 'res.company'
    _name = 'res.company'

    plafond_secu = fields.Float(string="Plafond de la Securite Sociale", required=True, default=6000)
    nombre_employes = fields.Integer(string="Nombre d'employes")
    cotisation_prevoyance = fields.Float(string="Cotisation Patronale Prevoyance")
    org_ss = fields.Char(string="Organisme de sécurite sociale")
    conv_coll = fields.Char(string="Convention collective")


class hr_payslip_line(models.Model):
    _inherit = 'hr.payslip.line'

    def get_valeur(self):
        res = dict()
        res['presence'] = self.env.ref('paie_maroc.Presence').categorie
        res['absence'] = self.env.ref('paie_maroc.absence').categorie
        res['conge_non_paye'] = self.env.ref('paie_maroc.congenp').categorie
        res['conge_paye'] = self.env.ref('paie_maroc.conep').categorie
        res['jour_ferie'] = self.env.ref('paie_maroc.jourferie').categorie
        res['supp25'] = self.env.ref('paie_maroc.supp25').categorie
        res['supp50'] = self.env.ref('paie_maroc.supp50').categorie
        res['supp100'] = self.env.ref('paie_maroc.supp100').categorie

        return res


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'
    NET = fields.Float()

    payment_mode = fields.Char('Mode de paiement', required=False, )
    date_today = fields.Date(string="Date virement")

    # @api.model
    # def create(self, values):
    @api.multi
    def action_print_fiche(self):
        return self.env.ref('paie_maroc.report_paie_maroc19').report_action(self)

    @api.multi
    def compute_sheet(self):
        for payslip in self:
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()

            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or \
                           self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)

            payslip.compute_heure_supp_dict()
            payslip.brutfeuille()
            lines = [(0, 0, line) for line in self._get_payslip_lines(contract_ids, payslip.id)]

            # payslip.compute_heure_supp_dict_brut()
            payslip.write({'line_ids': lines, 'number': number})
            # rec = 0.0
            # rec2 = 0.0
            # # net2 = self.env['hr.payslip.line'].search([('category_id.code', '=', 'NET'), ('slip_id', '=', payslip.id)])
            # # for k in net2:
            # #     self.NET=k.total
            # sal = self.env['hr.payslip.line'].search([('category_id.code', '=', 'feuille'), ('slip_id', '=', payslip.id),('code','!=','Présence'),('code','!=','Congé payé')])
            # sal2 = self.env['hr.payslip.line'].search([('category_id.code', '=', 'BRUT'), ('slip_id', '=', payslip.id)])
            # for k in sal:
            #         print(k.code)
            #         rec += k.total
            # for line in sal2:
            #     rec2+= rec
            # line.total += rec2
            # line.amount+=rec2

        return True

    # def compute_heure_supp_dict_brut(self):
    #         req = "select sum(total)as total from hr_payslip_line where category_id=%d"%(1)
    #         print("req",req)
    #         self.env.cr.execute(req)
    #         res = self.env.cr.fetchone()
    #
    #         # sal2 = self.env['hr.payslip.line'].search([('category_id.code','=','BRUT'),('slip_id','=',self.id)])
    #         # sal = self.env['hr.payslip.line'].search([('category_id.code', '=', 'BRUT')])
    #         # print(sal.code,sal.total)
    #         sal = self.env['hr.payslip.line'].search([('category_id.code','=','BASE'),('slip_id','=',self.id)])
    #         sal2 = self.env['hr.payslip.line'].search([('category_id.code','=','BRUT'),('slip_id','=',self.id)])
    #         for k in sal2:
    #             print(k.code,k.total,'bruuuuuuuuuut')
    # sal2 = self.env['hr.payslip.line'].search([('slip_id','=',self.id)])
    # x=0
    # y=0
    # for line in sal:
    #         print(line.code,line.total)
    #         x+=line.total
    #         print(line.slip_id.id,self.id, 'slippppppppppp')
    #
    # print(x,'totaaaaaaaaaaaaaaaaal feuille')
    # for k in sal2:
    #     y=k.total
    # print(y,'totaaaaaaaaaaaaaaaaaaal brut')
    #
    # data_rule = self.env['hr.payslip'].search([('employee_id','=',pay.employee_id.id)])
    # for k in data_rule:

    # for k in data_rule:
    #     # x=np.array(k.total)
    #
    # x=np.array([(100,200,20)])
    # cumsum=np.cumsum(x)
    # print(cumsum,'cumsuùm')

    def brutfeuille(self):
        for pay in self:
            rec = 0.0  # sum de feuille de temps sans conje et presence
            rec2 = 0.0  # sum de brut
            # net2 = self.env['hr.payslip.line'].search([('category_id.code', '=', 'NET'), ('slip_id', '=', payslip.id)])
            # for k in net2:
            #     self.NET=k.total
            presence = self.env.ref('paie_maroc.Presence')
            conge_paye = self.env.ref('paie_maroc.conep')
            sal = self.env['hr.payslip.line'].search(
                [('category_id.code', '=', 'feuille'), ('slip_id', '=', pay.id), ('code', '!=', presence.categorie),
                 ('code', '!=', conge_paye.categorie)])
            sal2 = self.env['hr.payslip.line'].search([('category_id.code', '=', 'BRUT'), ('slip_id', '=', pay.id)])
            for k in sal:
                rec += k.total
                rec2 = rec
                pay.NET = rec2

    def compute_heure_supp_dict(self):
        for pay in self:
            heure_travaill = {}
            taux = {}
            heure_trv = []
            value = []
            # data_rule = self.env['hr.payslip'].search([('employee_id', '=', pay.employee_id.id)])
            contracts = self.env['hr.contract'].search(
                [('employee_id', '=', pay.employee_id.id), ('state', '=', 'open')])
            data = self.env['account.analytic.line'].search(
                [('employee_id', '=', pay.employee_id.id), ('state', '=', 'confirmer'), ('date', '>=', pay.date_from),
                 ('date', '<=', pay.date_to)])
            if data:
                categories = data.mapped('categorie_trv')
                for cat in categories:
                    qtys = data.search(
                        [('categorie_trv', '=', cat.id), ('employee_id', '=', pay.employee_id.id)]).mapped(
                        'unit_amount')
                    taux_data = data.search([('categorie_trv', '=', cat.id)]).mapped('categorie_trv.taux')

                    # taux[cat.taux]=(taux_data)
                    heure_travaill[cat.categorie] = sum(qtys)

                    code_cat = self.env['hr.salary.rule.category'].search([('code', '=', 'feuille')], limit=0)
                    code_cat_rule = self.env['hr.salary.rule'].search([('code', '=', 'feuille')], limit=0)
                    value = {'name': cat.categorie,
                             'code': cat.categorie,
                             'salary_rule_id': code_cat_rule.id,
                             'category_id': code_cat.id,
                             'quantity': sum(qtys),
                             'rate': taux_data[0] * 100,
                             'amount': contracts.wage / 191
                             }

                    self.line_ids = [(0, 0, value)]

            print(heure_travaill)


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.constrains('Frais_Trans')
    def constraint_salaire(self):
        for record in self:
            if record.Frais_Trans > 700:
                raise exceptions.ValidationError("le Frais de Transport à dépassé 700 dh ")
            if record.Frais_Trans < 0:
                raise exceptions.ValidationError(" le frais de Transport  inférieur de 0!!!!!")

    # cin = fields.Char(string="Numéro CIN", required=False)
    matricule_cimr = fields.Char(string="Numéro CIMR", required=False)
    matricule_mut = fields.Char(string="Numéro MUTUELLE", required=False)
    num_chezemployeur = fields.Integer(string="Matricule")
    # abs = fields.Integer(string="Absence en heures", default=0,compute="compute_heure_supp")
    # hs25 = fields.Integer(string="Heures sup à 25", default=0,compute="compute_heure_supp")
    # hs50 = fields.Integer(string="Heures sup à 50", default=0,compute="compute_heure_supp")
    # hs100 = fields.Integer(string="Heures sup à 100", default=0,compute="compute_heure_supp")
    # hsovr = fields.Integer(string="Heures sup", default=0,compute="compute_heure_supp")
    av_sal = fields.Integer(string="Avance sur Salaire", default=0)
    rem_mut = fields.Integer(string="Remboursement Mutuelle", default=0)
    Frais_Trans = fields.Integer(default=0, string="Frais de transport ")
    indimnite_de_represenation = fields.Integer(string="Indemnité de représentation")
    indimnite_de_represenation_compute = fields.Integer(string="Indemnité de représentation",
                                                        compute="compute_indimnite_de_represenation", store=True)
    indimnite_de_panier = fields.Integer(string="Prime de panier")
    indmnite_panier_compute = fields.Integer(string="Prime de panier", compute="_prime_panier", store=True)
    frais_deplacement = fields.Integer(string="Frais de déplacement", default=0)
    indimnite_de_vestimentaire = fields.Integer(string="Indimnité de vestimentaire", default=0)
    indimnite_de_lait = fields.Integer(string="Indemnité de lait", defaullt=0)
    prime_rendement = fields.Integer(string="primes de rendements", default=0)
    prime_anciente = fields.Integer(string="prime d'ancienneté")
    prime_anciente_compute = fields.Integer(string="Prime d'ancienneté", compute="prime_anciennte", store=True)
    date_aujourdhuit = fields.Date(default=fields.Date.today())
    date_from = fields.Date(default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(string='Date To', readonly=True, required=True,
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))

    bool_representation = fields.Boolean(string="prime represetaion")
    boolean_calcule_prime = fields.Boolean(string="Calculer les primes automatiquement")

    # calcule la prime d'anciennté
    @api.depends('boolean_calcule_prime')
    def prime_anciennte(self):
        year_today = datetime.now().date()
        for line in self:
            if line.boolean_calcule_prime:
                contracts = self.env['hr.contract'].search(
                    [('employee_id', '=', line.id if line.id else self._origin.id), ('state', '=', 'open')])
                for k in contracts:
                    date1 = datetime.strptime(str(k.date_start), "%Y-%m-%d")
                    date2 = datetime.strptime(str(year_today), "%Y-%m-%d")
                    years = date2.year - date1.year
                    if years < 2:
                        line.prime_anciente_compute = 0
                    elif years < 5:
                        line.prime_anciente_compute = k.wage * 0.05
                    elif years < 12:
                        line.prime_anciente_compute = k.wage * 0.10
                    elif years < 20:
                        line.prime_anciente_compute = k.wage * 0.15
                    elif years < 25:
                        line.prime_anciente_compute = k.wage * 0.20
                    elif years >= 25:
                        line.prime_anciente_compute = k.wage * 0.25
                    else:
                        line.prime_anciente_compute = 0

    # calcule prime de panier
    @api.onchange('boolean_calcule_prime')
    def _prime_panier(self):
        try:
            for line in self:

                rec = 0
                rec2 = 0
                prime_p = 520
                line.indmnite_panier_compute = 520
                absence = self.env.ref('paie_maroc.absence')
                conge_non_paye = self.env.ref('paie_maroc.congenp')
                conge_paye = self.env.ref('paie_maroc.conep')
                if absence and conge_non_paye and conge_paye:
                    data2 = self.env['account.analytic.line'].search(
                        [('employee_id', '=', line.id if line.id else self._origin.id), ('state', '=', 'confirmer'),
                         ('categorie_trv', 'in',
                          [absence.categorie if absence else False, conge_paye.categorie if conge_paye else False,
                           conge_non_paye.categorie if conge_non_paye else False]),
                         ('date', '>=', line.date_from), ('date', '<=', line.date_to)])

                    print(data2)
                    # data2=self.env['account.analytic.line'].search([('employee_id', '=', self.id),('state', '=','confirmer'),('categorie_trv', 'in', ['Absence','Congé Non payé','Congé payé']),('date', '>=', self.date_from),('date', '<=', self.date_to)])
                    if data2:
                        if line.boolean_calcule_prime:

                            for absence in data2:
                                rec += absence.unit_amount
                                # print(rec)
                                rec2 = (rec / 8)
                            print(prime_p)
                            line.indmnite_panier_compute = prime_p - (20 * rec2)
                            print(self.indmnite_panier_compute)
        except:
            print("_prime_panier err")

    @api.depends('boolean_calcule_prime')
    def compute_indimnite_de_represenation(self):
        for line in self:
            if line.boolean_calcule_prime:
                contracts = self.env['hr.contract'].search(
                    [('employee_id', '=', line.id if line.id else self._origin.id), ('state', '=', 'open')])
                print("contracts", contracts)
                if contracts:
                    for k in contracts:
                        line.indimnite_de_represenation_compute = k.wage * 0.1

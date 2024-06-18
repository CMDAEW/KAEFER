from datetime import date, timedelta
import logging, re
from flask import current_app
from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, StringField, SelectField, TelField, EmailField, SubmitField, DateField, FloatField, HiddenField, PasswordField, TextAreaField, RadioField, DecimalField
from wtforms.validators import DataRequired, Length, Email, ValidationError, EqualTo, Optional, NumberRange
from InvoicingApp.models import ArbeitsbeschKopfdaten, TblPartner, tblKraftwerk, TblBaustellen, Lohnsaetze, Lohnzulagen, ArbeitsbeschDetaildaten
from wtforms.widgets import NumberInput

from InvoicingApp.utils import get_auftragsnr_choices, get_auftragsnr_kaefer_choices, get_baustelle_choices, get_kraftwerk_choices, get_projekt_choices, get_rahmenvertragsnr_choices, validate_percentage

class ArbeitsbeschKopfdatenForm(FlaskForm):
    auftraggeber = SelectField('Auftraggeber', choices=[], validators=[DataRequired()])
    rahmenvertrags_nr = SelectField('RahmenvertragsNr', choices=[], validators=[DataRequired()])
    projekt = SelectField('Projekt', choices=[], validators=[DataRequired()])
    auftrags_nr_kaefer = SelectField('AuftragsNrKAEFER', choices=[], validators=[DataRequired()])
    baustelle = SelectField('Baustelle', choices=[], validators=[DataRequired()])
    kommisionsnummer = SelectField('Kommisionsnummer', choices=[], validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(ArbeitsbeschKopfdatenForm, self).__init__(*args, **kwargs)
        
        self.auftraggeber.choices = [(kw.name, kw.name) for kw in tblKraftwerk.query.all() if kw.name is not None]
        self.auftraggeber.choices.append(('new_entry', 'Neuer Eintrag'))

        rahmenvertrags_nr_choices = [
            (r.rahmenvertrags_nr, r.rahmenvertrags_nr) for r in ArbeitsbeschKopfdaten.query.group_by(ArbeitsbeschKopfdaten.rahmenvertrags_nr).all() if r is not None and r.rahmenvertrags_nr is not None
        ]
        rahmenvertrags_nr_choices.append(('new_entry', 'Neuer Eintrag'))
        self.rahmenvertrags_nr.choices = rahmenvertrags_nr_choices

        projekt_choices = [
            (p.projekt, p.projekt) for p in ArbeitsbeschKopfdaten.query.group_by(ArbeitsbeschKopfdaten.projekt).all() if p is not None and p.projekt is not None
        ]
        projekt_choices.append(('new_entry', 'Neuer Eintrag'))
        self.projekt.choices = projekt_choices

        kommisionsnummer_choices = [
            (k.kommisionsnummer, k.kommisionsnummer) for k in ArbeitsbeschKopfdaten.query.group_by(ArbeitsbeschKopfdaten.kommisionsnummer).all() if k is not None and k.kommisionsnummer is not None
        ]
        kommisionsnummer_choices.append(('new_entry', 'Neuer Eintrag'))
        self.kommisionsnummer.choices = kommisionsnummer_choices

        self.baustelle.choices = [(b.bezeichnung, b.bezeichnung) for b in TblBaustellen.query.all() if b is not None and b.bezeichnung is not None]
        self.baustelle.choices.append(('new_entry', 'Neuer Eintrag'))

        auftrags_nr_kaefer_choices = [
            (a.auftrags_nr_kaefer, a.auftrags_nr_kaefer) for a in ArbeitsbeschKopfdaten.query.group_by(ArbeitsbeschKopfdaten.auftrags_nr_kaefer).all() if a is not None and a.auftrags_nr_kaefer is not None
        ]
        auftrags_nr_kaefer_choices.append(('new_entry', 'Neuer Eintrag'))
        self.auftrags_nr_kaefer.choices = auftrags_nr_kaefer_choices
class ArbeitsbeschDetaildatenForm(FlaskForm):
    Benennung = SelectField('Benennung', choices=[], validators=[DataRequired()])
   # lohnart = SelectField('Lohnart', choices=[], validators=[DataRequired()])
    so = DecimalField('Sonntag', validators=[NumberRange(min=0, max=10)], default=0.0, places=2)
    mo = DecimalField('Montag', validators=[NumberRange(min=0, max=10)], default=0.0, places=2)
    di = DecimalField('Dienstag', validators=[NumberRange(min=0, max=10)], default=0.0, places=2)
    mi = DecimalField('Mittwoch', validators=[NumberRange(min=0, max=10)], default=0.0, places=2)
    do = DecimalField('Donnerstag', validators=[NumberRange(min=0, max=10)], default=0.0, places=2)
    fr = DecimalField('Freitag', validators=[NumberRange(min=0, max=10)], default=0.0, places=2)
    sa = DecimalField('Samstag', validators=[NumberRange(min=0, max=10)], default=0.0, places=2)
    gesamtpreis = FloatField('Gesamtpreis')
    gesamtstunden = FloatField('Gesamtstunden')
    zu_std2 = FloatField('Zulage Std 2', validators=[Optional()])
    zu_std4 = FloatField('Zulage Std 4', validators=[Optional()])
    zu_std5 = FloatField('Zulage Std 5', validators=[Optional()])
    zu_std6 = FloatField('Zulage Std 6', validators=[Optional()])
    ArbBeschNr = IntegerField('ArbBeschNr', validators=[DataRequired()], render_kw={'readonly': True})
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(ArbeitsbeschDetaildatenForm, self).__init__(*args, **kwargs)
        self.update_benennung_choices()
        self.update_lohnart_choices()

    def update_benennung_choices(self, kraftwerk_id=None):
        if kraftwerk_id:
            self.Benennung.choices = [(entry.Benennung, entry.Benennung) for entry in ArbeitsbeschDetaildaten.query.filter_by(kraftwerk_id=kraftwerk_id).distinct(ArbeitsbeschDetaildaten.Benennung).all()]
        else:
            self.Benennung.choices = [(entry.Benennung, entry.Benennung) for entry in ArbeitsbeschDetaildaten.query.distinct(ArbeitsbeschDetaildaten.Benennung).all()]
        self.Benennung.choices.append(('new_entry', 'New Entry'))

    def update_lohnart_choices(self, kraftwerk_id=None):
        if kraftwerk_id:
            self.lohnart.choices = [(entry.lohnart, entry.lohnart) for entry in Lohnsaetze.query.filter_by(kraftwerk_id=kraftwerk_id).distinct(Lohnsaetze.lohnart).all()]
        else:
            self.lohnart.choices = [(entry.lohnart, entry.lohnart) for entry in Lohnsaetze.query.distinct(Lohnsaetze.lohnart).all()]
        self.lohnart.choices.append(('new_entry', 'New Entry'))
class ProjectForm(FlaskForm):
    auftraggeber = SelectField('Auftraggeber', validators=[DataRequired()])
    new_kraftwerkname = StringField('New Kraftwerkname', validators=[Optional()])
    rahmenvertrags_nr = SelectField('rahmenvertrags_nr', validators=[Optional()])
    new_rahmenvertragsnr = StringField('New rahmenvertrags_nr', validators=[Optional()])
    projekt = SelectField('Projekt', validators=[Optional()])
    new_projekt = StringField('New Projekt', validators=[Optional()])
    auftrags_nr = SelectField('Auftrags-Nr', validators=[Optional()])
    new_auftrags_nr = StringField('New Auftrags-Nr', validators=[Optional()])
    bestelldatum = DateField('Bestelldatum', validators=[Optional()], default=date.today)
    baustelle = SelectField('Baustelle', validators=[Optional()])
    new_baustelle = StringField('New Baustelle', validators=[Optional()])
    k_trv = RadioField('K_TRV', choices=[('K', 'Kraftwerk'), ('TRV', 'Thermische Rest Verwertungsanlage')], validators=[DataRequired()])
    auftrags_nr_kaefer = SelectField('Auftrags-Nr KAEFER', validators=[Optional()])
    new_auftrags_nr_kaefer = StringField('New Auftrags-Nr KAEFER', validators=[Optional()])
    ausfuehrungsbeginn = DateField('Ausführungsbeginn', validators=[Optional()], default=date.today() - timedelta(days=14))
    ausfuehrungsende = DateField('Ausführungsende', validators=[Optional()], default=date.today() - timedelta(days=1))
    bemerkung = TextAreaField('Bemerkung', validators=[Optional()])
    aufmass_nr = IntegerField('AufmassNr', validators=[DataRequired()])
    monteur = StringField('Monteur', validators=[Optional()])
    lohnart = StringField('lohnart', validators=[Optional()])
    so = FloatField('So', validators=[Optional()])
    mo = FloatField('Mo', validators=[Optional()])
    di = FloatField('Di', validators=[Optional()])
    mi = FloatField('Mi', validators=[Optional()])
    do = FloatField('Do', validators=[Optional()])
    fr = FloatField('Fr', validators=[Optional()])
    sa = FloatField('Sa', validators=[Optional()])
    gesamtstunden = FloatField('Gesamtstunden', validators=[Optional()])
    gesamtpreis = FloatField('Gesamtpreis', validators=[Optional()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.auftraggeber.choices = [('new', 'Add New')] + get_kraftwerk_choices()
        self.rahmenvertrags_nr.choices = [('new', 'Add New')] + get_rahmenvertragsnr_choices()
        self.projekt.choices = [('new', 'Add New')] + get_projekt_choices()
        self.auftrags_nr.choices = [('new', 'Add New')] + get_auftragsnr_choices()
        self.baustelle.choices = [('new', 'Add New')] + get_baustelle_choices()
        self.auftrags_nr_kaefer.choices = [('new', 'Add New')] + get_auftragsnr_kaefer_choices()

class ArbeitsbescheinigungForm(FlaskForm):
    auftraggeber = StringField('Auftraggeber', validators=[Optional(), Length(max=255)])
    rv_pos = StringField('RV_Pos')
    rahmenvertrags_nr = StringField('Rahmenvertrags Nr', validators=[Optional(), Length(max=255)])
    projekt = StringField('Projekt', validators=[Optional(), Length(max=255)])
    auftrags_nr = StringField('Auftrags Nr', validators=[Optional(), Length(max=255)])
    bestelldatum = DateField('Bestelldatum', validators=[Optional()])
    baustelle = StringField('Baustelle', validators=[Optional(), Length(max=255)])
    kraftwerk = BooleanField('Kraftwerk')
    trv = BooleanField('TRV')
    ArbBeschNr = IntegerField('Arbeitsbescheinigung Nr', validators=[DataRequired()])
    auftrags_nr_kaefer = StringField('Auftrags-Nr KAEFER', validators=[Optional(), Length(max=255)])
    ausfuehrungsbeginn = DateField('Ausführungsbeginn', validators=[Optional()])
    ausfuehrungsende = DateField('Ausführungsende', validators=[Optional()])
    arb_besch_summe = DecimalField('Summe', validators=[Optional()])

    # Detailed Information Fields
    monteur = SelectField('Monteur', validators=[Optional()])
    lohn_art = SelectField('Lohn Art', validators=[Optional()], choices=[])
    so = IntegerField('So', validators=[Optional()])
    mo = IntegerField('Mo', validators=[Optional()])
    di = IntegerField('Di', validators=[Optional()])
    mi = IntegerField('Mi', validators=[Optional()])
    do = IntegerField('Do', validators=[Optional()])
    fr = IntegerField('Fr', validators=[Optional()])
    sa = IntegerField('Sa', validators=[Optional()])
    gp = FloatField('GP', validators=[Optional()])

    # Financial Fields
    summe = DecimalField('Summe', validators=[Optional()])

    # Metadata Fields
    bemerkung = TextAreaField('Bemerkung', validators=[Optional(), Length(max=255)])
    erstellt_von = StringField('Erstellt von', validators=[Optional(), Length(max=255)])
    erstellt_am = DateField('Erstellt am', validators=[Optional()])
    geaendert_von = StringField('Geaendert von', validators=[Optional(), Length(max=255)])
    geaendert_am = DateField('Geaendert am', validators=[Optional()])
    
    submit = SubmitField('Submit')

    def __init__(self, kraftwerk_id=None, *args, **kwargs):
        super(ArbeitsbescheinigungForm, self).__init__(*args, **kwargs)
        self.lohn_art.choices = [(l.Id, f"{l.lohnart} - {l.bezeichnung}") for l in Lohnsaetze.query.order_by(Lohnsaetze.lohnart).all()]
        self.monteur.choices = [(m.Benennung, m.Benennung) for m in ArbeitsbeschDetaildaten.query.filter(ArbeitsbeschDetaildaten.gruppe.like("STD")).group_by(ArbeitsbeschDetaildaten.Benennung).order_by(ArbeitsbeschDetaildaten.Benennung).all()]
class LohnsatzForm(FlaskForm):
    kraftwerk_id = SelectField('Kraftwerk / TRV', validators=[DataRequired()], choices=[])
    lohnart = StringField('lohnart', validators=[DataRequired()])
    std_satz = StringField('VKP EUR/h', validators=[DataRequired()])
    basis_satz = StringField('Basis EUR/h')
    bezeichnung = StringField('Bezeichnung', validators=[DataRequired()])
    new_kraftwerk_name = StringField('New Kraftwerk Name')
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(LohnsatzForm, self).__init__(*args, **kwargs)
        self.kraftwerk_id.choices = [(kw.name, kw.name) for kw in tblKraftwerk.query.all() if kw.name is not None]
        self.kraftwerk_id.choices.append(('new_entry', 'Neuer Eintrag'))

    def validate_std_satz(form, field):
        if not re.match(r'^\d+,\d{2}$', field.data):
            raise ValidationError('VKP EUR/h must be in the format of euros,comma,cents (e.g., 100,00)')

    def validate_basis_satz(form, field):
        if field.data and not re.match(r'^\d+,\d{2}$', field.data):
            raise ValidationError('Basis EUR/h must be in the format of euros,comma,cents (e.g., 100,00)')

    def get_std_satz(self):
        return float(self.std_satz.data.replace(',', '.'))

    def get_basis_satz(self):
        return float(self.basis_satz.data.replace(',', '.')) if self.basis_satz.data else None

class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"class": "form-control"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"class": "form-control"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')], render_kw={"class": "form-control"})
    submit = SubmitField('Create User', render_kw={"class": "btn btn-primary btn-block"})

class KraftwerkForm(FlaskForm):
    name = HiddenField()
    kraftwerkname = StringField('Kraftwerk Name', validators=[DataRequired()])
    partner_id = SelectField('Ansprechpartner', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Save')

class LohnzulagenForm(FlaskForm):
    zulage_id = HiddenField()
    zulage_art = StringField('Zulage Art', validators=[DataRequired()])
    bezeichnung = StringField('Bezeichnung', validators=[DataRequired()])
    zulage_proz = StringField('Zulage in %', validators=[DataRequired(), validate_percentage], widget=NumberInput(min=0, max=1000, step=0.01))
    submit = SubmitField('Save')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PartnerForm(FlaskForm):
    partner_id = HiddenField('partner_id')
    anrede = SelectField('Anrede', choices=[('Herr', 'Herr'), ('Frau', 'Frau'), ('Divers', 'Divers')], validators=[DataRequired()], render_kw={"class": "form-control"})
    vorname = StringField('Vorname', validators=[DataRequired()], render_kw={"class": "form-control"})
    nachname = StringField('Nachname', validators=[DataRequired()], render_kw={"class": "form-control"})
    telefonnummer = StringField('Telefonnummer', validators=[DataRequired()], render_kw={"class": "form-control", "value": "+"})
    telefaxnummer = StringField('Telefaxnummer', render_kw={"class": "form-control", "value": "+"})
    email = StringField('Email', validators=[Email()], render_kw={"class": "form-control", "placeholder": "name@example.com"})
    submit = SubmitField('Create', render_kw={"class": "btn btn-primary"})

    def validate_email(self, email):
        partner_id = self.partner_id.data
        existing_partner = TblPartner.query.filter_by(email=email.data).first()
        if existing_partner and (not partner_id or existing_partner.nummer != int(partner_id)):
            raise ValidationError('Email address already exists.')

    def validate_telefonnummer(self, telefonnummer):
        partner_id = self.partner_id.data
        existing_partner = TblPartner.query.filter_by(telefonnummer=telefonnummer.data).first()
        if existing_partner and (not partner_id or existing_partner.nummer != int(partner_id)):
            raise ValidationError('Phone number already exists.')
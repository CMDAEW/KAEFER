from flask import current_app
from wtforms import ValidationError
from .models import tblKraftwerk, ArbeitsbeschKopfdaten, TblBaustellen, ArbeitsbeschDetaildaten
from datetime import datetime

def get_kraftwerk_choices():
    with current_app.app_context():
        return [(kw.name, kw.name) for kw in tblKraftwerk.query.all()]

def get_rahmenvertragsnr_choices():
    with current_app.app_context():
        return [(rv.rahmenvertrags_nr, rv.rahmenvertrags_nr) for rv in ArbeitsbeschKopfdaten.query.group_by(ArbeitsbeschKopfdaten.rahmenvertrags_nr).all()]

def get_projekt_choices():
    with current_app.app_context():
        return [(pj.projekt, pj.projekt) for pj in ArbeitsbeschKopfdaten.query.group_by(ArbeitsbeschKopfdaten.projekt).all()]

def get_auftragsnr_choices():
    with current_app.app_context():
        return [(an.kommisionsnummer, an.kommisionsnummer) for an in ArbeitsbeschKopfdaten.query.group_by(ArbeitsbeschKopfdaten.kommisionsnummer).all()]

def get_baustelle_choices():
    with current_app.app_context():
        return [(bs.baustelle, bs.baustelle) for bs in ArbeitsbeschKopfdaten.query.group_by(ArbeitsbeschKopfdaten.baustelle).all()]

def get_auftragsnr_kaefer_choices():
    with current_app.app_context():
        return [(ak.auftrags_nr_kaefer, ak.auftrags_nr_kaefer) for ak in ArbeitsbeschKopfdaten.query.group_by(ArbeitsbeschKopfdaten.auftrags_nr_kaefer).all()]

def validate_percentage(form, field):
    try:
        value = float(field.data)
        if not 0 <= value <= 1000:
            raise ValidationError('Percentage must be between 0 and 100')
    except ValueError:
        raise ValidationError('Invalid percentage value')
    
def format_dates(entries):
    for entry in entries:
        if isinstance(entry.angelegtdat, str):
            entry.angelegtdat = datetime.strptime(entry.angelegtdat, '%d.%m.%Y %H:%M:%S').isoformat()
        if isinstance(entry.geaendertdat, str):
            entry.geaendertdat = datetime.strptime(entry.geaendertdat, '%d.%m.%Y %H:%M:%S').isoformat()
    return entries

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        # Handle specific date formats if necessary, e.g. '14.5.2024 00:00:00'
        try:
            return datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')
        except ValueError:
            return None
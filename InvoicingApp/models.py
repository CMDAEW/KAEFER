from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from InvoicingApp import db
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Float, Date, Text, DateTime

class ArbeitsbeschKopfdaten(db.Model):
    __tablename__ = 'Arbeitsbesch_Kopfdaten'
    id = db.Column('ArbBeschNr', db.Integer, primary_key=True, autoincrement=True)
    rahmenvertrags_nr = db.Column('Rahmenvertrags_Nr', db.String(255), nullable=True)
    auftrags_nr_kaefer = db.Column('Auftrags_Nr_KAEFER', db.String(255), nullable=True)
    projekt = db.Column('Projekt', db.String(255), nullable=True)
    lohnsaetze_id = db.Column('LohnsaetzeID', db.Integer, nullable=True)
    baustelle = db.Column('Baustelle', db.String(255), nullable=True)
    auftraggeber = db.Column('Auftraggeber', db.String(255), nullable=True)
    kommisionsnummer = db.Column('Kommisionsnummer', db.String(255), nullable=True)
    bestell_datum = db.Column('Bestell_Datum', db.String(255), nullable=True)
    ausfuehrungsbeginn = db.Column('Ausführungsbeginn', db.String(255), nullable=True)
    ausfuehrungsende = db.Column('Ausführungsende', db.String(255), nullable=True)
    bemerkung = db.Column('Bemerkung', db.Text, nullable=True)
    arb_besch_summe = db.Column('ArBesch_Summe', db.String(255), nullable=True)
    angelegt_dat = db.Column('AngelegtDat', db.String(255), nullable=True)
    angelegt_durch = db.Column('Angelegt_durch', db.String(255), nullable=True)
    geaendert_dat = db.Column('GeaendertDat', db.String(255), nullable=True)
    geaendert_durch = db.Column('Geaendert_durch', db.String(255), nullable=True)
    k_trv = db.Column('K_TRV', db.Integer, nullable=True)
    erstellt_datum = db.Column('Erstelldatum', db.String(255), nullable=True)

    def __repr__(self):
        return f'<ArbeitsbeschKopfdaten {self.projekt}>'

class ArbeitsbeschDetaildaten(db.Model):
    __tablename__ = 'arbeitsbesch__detaildaten'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ArbBeschNr = db.Column(db.Integer, nullable=True)
    RV_Pos = db.Column(db.String(255), nullable=True)
    Benennung = db.Column(db.String(255), nullable=True)
    Menge = db.Column(db.String(255), nullable=True)
    ME = db.Column(db.String(255), nullable=True)
    EP = db.Column(db.String(255), nullable=True)
    Per = db.Column(db.String(255), nullable=True)
    So = db.Column(db.Float, nullable=True)
    Mo = db.Column(db.Float, nullable=True)
    Di = db.Column(db.Float, nullable=True)
    Mi = db.Column(db.Float, nullable=True)
    Do = db.Column(db.Float, nullable=True)
    Fr = db.Column(db.Float, nullable=True)
    Sa = db.Column(db.Float, nullable=True)
    lohnart = db.Column(db.String(255), nullable=True)
    Basis_EP = db.Column(db.String(255), nullable=True)
    ZulageArt1 = db.Column(db.String(255), nullable=True)
    Zu_Std1 = db.Column(db.Float, nullable=True)
    ZulageArt2 = db.Column(db.String(255), nullable=True)
    Zu_Std2 = db.Column(db.Float, nullable=True)
    ZulageArt3 = db.Column(db.String(255), nullable=True)
    Zu_Std3 = db.Column(db.Float, nullable=True)
    ZulageArt4 = db.Column(db.String(255), nullable=True)
    Zu_Std4 = db.Column(db.Float, nullable=True)
    ZulageArt5 = db.Column(db.String(255), nullable=True)
    Zu_Std5 = db.Column(db.Float, nullable=True)
    ZulageArt6 = db.Column(db.String(255), nullable=True)
    Zu_Std6 = db.Column(db.Float, nullable=True)
    ZulageArt7 = db.Column(db.String(255), nullable=True)
    Zu_Std7 = db.Column(db.Float, nullable=True)
    ZulageArt8 = db.Column(db.String(255), nullable=True)
    Zu_Std8 = db.Column(db.Float, nullable=True)
    GP = db.Column(db.String(255), nullable=True)
    Satz_Nr = db.Column(db.Integer, nullable=True)
    Gruppe = db.Column(db.String(255), nullable=True)
    AngelegtDat = db.Column(db.Text, nullable=True)
    Angelegt_durch = db.Column(db.String(255), nullable=True)
    GeaendertDat = db.Column(db.Text, nullable=True)
    Geaendert_durch = db.Column(db.String(255), nullable=True)
    gesamtstunden = db.Column(db.Float, nullable=True)
    gesamtpreis = db.Column(db.Float, nullable=True)
    kraftwerkname = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<ArbeitsbeschDetaildaten {self.id}>'

    @staticmethod
    def parse_date(date_str):
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            try:
                return datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')
            except ValueError:
                return None

class AufmassKopfdaten(db.Model):
    __tablename__ = 'Aufmass_Kopfdaten'

    AufmassNr = db.Column(db.Integer, primary_key=True)
    AufmassArt = db.Column(db.String(255), nullable=True)
    RahmvertragsNr = db.Column(db.String(255), nullable=True)
    Auftrags_Nr_KAEFER = db.Column(db.String(255), nullable=True)
    Projekt = db.Column(db.String(255), nullable=True)
    Baustelle = db.Column(db.String(255), nullable=True)
    Kommisionsnummer = db.Column(db.String(255), nullable=True)
    Bestell_Datum = db.Column(db.DateTime, nullable=True)
    Ausführungsbeginn = db.Column(db.DateTime, nullable=True)
    Ausführungsende = db.Column(db.DateTime, nullable=True)
    Bemerkung = db.Column(db.String(255), nullable=True)
    Aufmass_Summe = db.Column(db.Float, nullable=True)
    AngelegtDat = db.Column(db.DateTime, nullable=False)
    Angelegt_durch = db.Column(db.String(255), nullable=True)
    GeaendertDat = db.Column(db.DateTime, nullable=True)
    Geaendert_durch = db.Column(db.String(255), nullable=True)
    KraftwerkId = db.Column(db.String(255), nullable=True)
    K_TRV = db.Column(db.String(255), nullable=True)
    Erstelldatum = db.Column(db.DateTime, nullable=False)

    def __init__(self, AufmassNr, AufmassArt=None, RahmvertragsNr=None, Auftrags_Nr_KAEFER=None, Projekt=None, Baustelle=None, Kommisionsnummer=None,
                 Bestell_Datum=None, Ausführungsbeginn=None, Ausführungsende=None, Bemerkung=None, Aufmass_Summe=None, AngelegtDat=None, 
                 Angelegt_durch=None, GeaendertDat=None, Geaendert_durch=None, KraftwerkId=None, K_TRV=None, Erstelldatum=None):
        self.AufmassNr = AufmassNr
        self.AufmassArt = AufmassArt
        self.RahmvertragsNr = RahmvertragsNr
        self.Auftrags_Nr_KAEFER = Auftrags_Nr_KAEFER
        self.Projekt = Projekt
        self.Baustelle = Baustelle
        self.Kommisionsnummer = Kommisionsnummer
        self.Bestell_Datum = Bestell_Datum
        self.Ausführungsbeginn = Ausführungsbeginn
        self.Ausführungsende = Ausführungsende
        self.Bemerkung = Bemerkung
        self.Aufmass_Summe = Aufmass_Summe
        self.AngelegtDat = AngelegtDat if AngelegtDat else datetime.utcnow()
        self.Angelegt_durch = Angelegt_durch
        self.GeaendertDat = GeaendertDat
        self.Geaendert_durch = Geaendert_durch
        self.KraftwerkId = KraftwerkId
        self.K_TRV = K_TRV
        self.Erstelldatum = Erstelldatum if Erstelldatum else datetime.utcnow()

class AufmassDetaildaten(db.Model):
    __tablename__ = 'Aufmass_Detaildaten'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    AufmassNr = Column(Integer, nullable=True)
    LFD_Pos_Nr = Column(Integer, nullable=True)
    RV_Pos = Column(Text, nullable=True)
    Benennung = Column(Text, nullable=True)
    Umfang_DN = Column(Text, nullable=True)
    Leistung = Column(Text, nullable=True)
    Qm = Column(Text, nullable=True)
    Menge = Column(Text, nullable=True)
    ME = Column(Text, nullable=True)
    IS = Column(Text, nullable=True)
    Basis_EP = Column(Text, nullable=True)
    Per = Column(Text, nullable=True)
    Faktor_1 = Column(Integer, nullable=True)
    Faktor_2 = Column(Integer, nullable=True)
    Faktor_3 = Column(Integer, nullable=True)
    Faktor_4 = Column(Integer, nullable=True)
    Faktor_5 = Column(Integer, nullable=True)
    Faktor_6 = Column(Integer, nullable=True)
    Faktor_EP = Column(Text, nullable=True)
    Z_Menge = Column(Integer, nullable=True)
    Zulage = Column(Text, nullable=True)
    GP = Column(Text, nullable=True)
    Satz_Nr = Column(Integer, nullable=True)
    Gruppe = Column(Text, nullable=True)
    AngelegtDat = Column(Text, nullable=True)
    Angelegt_durch = Column(Text, nullable=True)
    GeaendertDat = Column(Text, nullable=True)
    Geaendert_durch = Column(Text, nullable=True)

class AktuellerUser(db.Model):
    __tablename__ = 'aktueller_user'
    id = db.Column('User-ID', db.Integer, primary_key=True)
    anrede = db.Column('UserAnrede', db.String(255), nullable=False)
    name = db.Column('UserName', db.String(255), nullable=False)
    password = db.Column('UserPassword', db.String(255), nullable=False)
    level = db.Column('UserLevel', db.Integer, nullable=False)

    def __repr__(self):
        return f'<AktuellerUser {self.name}>'

class EP(db.Model):
    __tablename__ = 'ep'
    RV_Pos = db.Column(db.Integer, primary_key=True)
    DN = db.Column(db.Integer)
    DA = db.Column(db.String(255))
    IS = db.Column(db.String(255))
    ME = db.Column(db.String(255))
    EP = db.Column(db.String(255))
    AngelegtDat = db.Column(db.String(255))
    Angelegt_durch = db.Column(db.String(255))
    GeaendertDat = db.Column(db.String(255))
    Geaendert_durch = db.Column(db.String(255))
    Leistung = db.Column(db.String(255))

    def __repr__(self):
        return f'<EP {self.RV_Pos}>'

class EPFaktoren(db.Model):
    __tablename__ = 'ep_faktoren'
    RV_Pos = db.Column(db.Integer, primary_key=True)
    Benennung = db.Column('Benennung', db.String(255))
    faktor = db.Column('Faktor', db.String(255))
    angelegt_dat = db.Column('AngelegtDat', db.String(255))
    angelegt_durch = db.Column('Angelegt_durch', db.String(255))
    geaendert_dat = db.Column('GeaendertDat', db.String(255))
    geaendert_durch = db.Column('Geaendert_durch', db.String(255))

    def __repr__(self):
        return f'<EPFaktoren {self.RV_Pos}>'

class EPKopie(db.Model):
    __tablename__ = 'ep_kopie'
    RV_Pos = db.Column(db.Integer, primary_key=True)
    leistung = db.Column('Leistung', db.String(255))
    DN = db.Column('DN', db.Integer)
    DA = db.Column('DA', db.String(255))
    IS = db.Column('IS', db.String(255))
    Benennung = db.Column('_Benennung', db.String(255))
    ME = db.Column('ME', db.String(255))
    EP = db.Column('EP', db.String(255))
    angelegt_dat = db.Column('AngelegtDat', db.String(255))
    angelegt_durch = db.Column('Angelegt_durch', db.String(255))
    geaendert_dat = db.Column('GeaendertDat', db.String(255))
    geaendert_durch = db.Column('Geaendert_durch', db.String(255))

    def __repr__(self):
        return f'<EPKopie {self.RV_Pos}>'

class Einfuegefehler(db.Model):
    __tablename__ = 'einfuegefehler'
    F1 = db.Column(db.String(255), primary_key=True)

    def __repr__(self):
        return f'<Einfuegefehler {self.F1}>'

class KAEFlaechen(db.Model):
    __tablename__ = 'kae_flaechen'
    ZZSKL = db.Column(db.String(255), primary_key=True)
    DN = db.Column(db.String(255))
    DA = db.Column(db.String(255))
    IS = db.Column(db.Integer)
    DaIs = db.Column(db.String(255))
    DaBL = db.Column(db.Integer)
    E_Flae = db.Column(db.String(255))

    def __repr__(self):
        return f'<KAEFlaechen {self.ZZSKL}>'

class Lohnsaetze(db.Model):
    __tablename__ = 'Lohnsaetze'
    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lohnart = db.Column('lohnart', db.String(255))
    std_satz = db.Column('STD_Satz', db.String(255))
    basis_satz = db.Column('Basis_Satz', db.String(255))
    bezeichnung = db.Column('Bezeichnung', db.String(255))
    angelegt_dat = db.Column('AngelegtDat', db.String(255))
    angelegt_durch = db.Column('Angelegt_durch', db.String(255))
    geaendert_dat = db.Column('GeaendertDat', db.String(255))
    geaendert_durch = db.Column('Geaendert_durch', db.String(255))
    kraftwerk_id = db.Column('KraftwerkId', db.String(255), db.ForeignKey('tblKraftwerk.Kraftwerkname'))

    # Define relationship to tblKraftwerk
    kraftwerk = db.relationship('tblKraftwerk', backref=db.backref('lohnsaetze', lazy=True))

    def to_dict(self):
        return {
            'Id': self.Id,
            'lohnart': self.lohnart,
            'std_satz': "{:.2f}".format(float(self.std_satz.replace(',', '.'))).replace('.', ','),
            'basis_satz': "{:.2f}".format(float(self.basis_satz.replace(',', '.'))).replace('.', ',') if self.basis_satz else '',
            'bezeichnung': self.bezeichnung,
            'angelegt_dat': self.angelegt_dat,
            'angelegt_durch': self.angelegt_durch,
            'geaendert_dat': self.geaendert_dat,
            'geaendert_durch': self.geaendert_durch,
            'kraftwerk_id': self.kraftwerk_id
        }

class Lohnzulagen(db.Model):
    __tablename__ = 'lohnzulagen'
    zulage_art = db.Column('ZulageArt', db.String(255), primary_key=True)
    zulage_nr = db.Column('ZulageNr', db.Integer)
    bezeichnung = db.Column('Bezeichnung', db.String(255))
    zulage_proz = db.Column('Zulage_Proz', db.String(255))
    angelegt_dat = db.Column('AngelegtDat', db.String(255))
    angelegt_durch = db.Column('Angelegt_durch', db.String(255))
    geaendert_dat = db.Column('GeaendertDat', db.String(255))
    geaendert_durch = db.Column('Geaendert_durch', db.String(255))

    def __repr__(self):
        return f'<Lohnzulagen {self.zulage_art}>'

    def to_dict(self):
        return {
            'zulage_art': self.zulage_art,
            'zulage_nr': self.zulage_nr,
            'bezeichnung': self.bezeichnung,
            'zulage_proz': self.zulage_proz,
            'angelegt_dat': self.angelegt_dat,
            'angelegt_durch': self.angelegt_durch,
            'geaendert_dat': self.geaendert_dat,
            'geaendert_durch': self.geaendert_durch
        }

class Material(db.Model):
    __tablename__ = 'material'
    RV_Pos = db.Column(db.Integer, primary_key=True)
    Benennung = db.Column('Benennung', db.String(255))
    material = db.Column('Material', db.String(255))
    abmessung = db.Column('Abmessung', db.String(255))
    ME = db.Column('ME', db.String(255))
    EP = db.Column('EP', db.String(255))
    per = db.Column('per', db.String(255))
    angelegt_dat = db.Column('AngelegtDat', db.String(255))
    angelegt_durch = db.Column('Angelegt_durch', db.String(255))
    geaendert_dat = db.Column('GeaendertDat', db.String(255))
    geaendert_durch = db.Column('Geaendert_durch', db.String(255))

    def __repr__(self):
        return f'<Material {self.RV_Pos}>'

class Materialleistung(db.Model):
    __tablename__ = 'materialleistung'
    leistungsnummer = db.Column('Leistungsnummer', db.Float, primary_key=True)
    leistungsbezeichnung = db.Column('Leistungsbezeichnung', db.String(255))

    def __repr__(self):
        return f'<Materialleistung {self.leistungsnummer}>'

class TblVerrechnungsfaktor(db.Model):
    __tablename__ = 'tbl_verrechnungsfaktor'
    verrechnungsfaktor_id = db.Column('VerechnungsfaktorID', db.String(255), primary_key=True)

    def __repr__(self):
        return f'<TblVerrechnungsfaktor {self.verrechnungsfaktor_id}>'

class TblDA(db.Model):
    __tablename__ = 'tbl_da'
    daid_pk = db.Column('DAID_PK', db.String(255), primary_key=True)

    def __repr__(self):
        return f'<TblDA {self.daid_pk}>'

class TblDN(db.Model):
    __tablename__ = 'tbl_dn'
    dnid_pk = db.Column('DNID_PK', db.Integer, primary_key=True)

    def __repr__(self):
        return f'<TblDN {self.dnid_pk}>'

class Tbl_Einheit(db.Model):
    __tablename__ = 'Tbl_Einheit'
    einheit_id_pk = db.Column('EinheitID_PK', db.String(255), primary_key=True)
    bezeichnung = db.Column('Bezeichnung', db.String(255))

    def __repr__(self):
        return f'<Tbl_Einheit {self.einheit_id_pk}>'

class TblGUIEigenschaften(db.Model):
    __tablename__ = 'tbl_guieigenschaften'
    eigenschaft = db.Column('Eigenschaft', db.String(255), primary_key=True)
    wert = db.Column('Wert', db.String(255))
    bemerkung = db.Column('Bemerkung', db.String(255))

    def __repr__(self):
        return f'<TblGUIEigenschaften {self.eigenschaft}>'

class TblIS(db.Model):
    __tablename__ = 'tbl_is'
    isid_pk = db.Column('ISID_PK', db.String(255), primary_key=True)

    def __repr__(self):
        return f'<TblIS {self.isid_pk}>'

class TblIsolierungselement(db.Model):
    __tablename__ = 'tbl_isolierungselement'
    idie_pk = db.Column('IDIE_PK', db.String(255), primary_key=True)
    beschreibung = db.Column('Beschreibung', db.String(255))
    leistungsid_fk = db.Column('LeistungsID_FK', db.String(255))

    def __repr__(self):
        return f'<TblIsolierungselement {self.idie_pk}>'

class TblLeistungsverzeichnis(db.Model):
    __tablename__ = 'tbl_leistungsverzeichnis'
    lid_pk = db.Column('LID_PK', db.String(255), primary_key=True)
    beschreibung = db.Column('Beschreibung', db.String(255))

    def __repr__(self):
        return f'<TblLeistungsverzeichnis {self.lid_pk}>'

class TblTmpAufmassKopfdaten(db.Model):
    __tablename__ = 'tbl_tmp_aufmass_kopfdaten'
    aufmass_nr = db.Column('AufmassNr', db.Integer, primary_key=True)
    aufmass_art = db.Column('AufmassArt', db.String(255))
    rahmenvertrags_nr = db.Column('RahmvertragsNr', db.String(255))
    auftrags_nr_kaefer = db.Column('Auftrags_Nr_KAEFER', db.Integer)
    projekt = db.Column('Projekt', db.String(255))
    baustelle = db.Column('Baustelle', db.String(255))
    kommisionsnummer = db.Column('Kommisionsnummer', db.String(255))
    bestell_datum = db.Column('Bestell_Datum', db.String(255))
    ausfuehrungsbeginn = db.Column('Ausführungsbeginn', db.String(255))
    ausfuehrungsende = db.Column('Ausführungsende', db.String(255))
    bemerkung = db.Column('Bemerkung', db.String(255))
    aufmass_summe = db.Column('Aufmass_Summe', db.String(255))
    angelegt_dat = db.Column('AngelegtDat', db.String(255))
    angelegt_durch = db.Column('Angelegt_durch', db.String(255))
    geaendert_dat = db.Column('GeaendertDat', db.String(255))
    geaendert_durch = db.Column('Geaendert_durch', db.String(255))
    kraftwerk_id = db.Column('KraftwerkId', db.String(255))
    k_trv = db.Column('K_TRV', db.Integer)
    erstellt_datum = db.Column('Erstelldatum', db.String(255))

    def __repr__(self):
        return f'<TblTmpAufmassKopfdaten {self.aufmass_nr}>'

class TmpTblOptArbBeschReport(db.Model):
    __tablename__ = 'tmp_tbl_opt_arb_besch_report'
    datum_zeigen = db.Column('DatumZeigen', db.Integer, primary_key=True)
    ort_zeigen = db.Column('OrtZeigen', db.Integer)
    erstellt_datum_zeigen = db.Column('ErstelldatumZeigen', db.Integer)

    def __repr__(self):
        return f'<TmpTblOptArbBeschReport {self.datum_zeigen}>'

class TmpTblOptAufmassReport(db.Model):
    __tablename__ = 'tmp_tbl_opt_aufmass_report'
    datum_zeigen = db.Column('DatumZeigen', db.Integer, primary_key=True)
    ort_zeigen = db.Column('OrtZeigen', db.Integer)
    erstellt_datum_zeigen = db.Column('ErstelldatumZeigen', db.Integer)

    def __repr__(self):
        return f'<TmpTblOptAufmassReport {self.datum_zeigen}>'

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column('User-ID', db.Integer, primary_key=True)
    anrede = db.Column('UserAnrede', db.String(255), nullable=True)
    name = db.Column('UserName', db.String(255), nullable=False)
    password = db.Column('UserPassword', db.String(255), nullable=False)
    level = db.Column('UserLevel', db.Integer, nullable=True)
    kraftwerk_id = db.Column('KraftwerkId', db.String(255), db.ForeignKey('tblKraftwerk.Kraftwerkname'))

    kraftwerk = db.relationship('tblKraftwerk', backref=db.backref('users', lazy=True))

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class UserLevels(db.Model):
    __tablename__ = 'user_levels'
    level = db.Column('UserLevel', db.Integer, primary_key=True)
    beschreibung = db.Column('Beschreibung', db.String(255))

    def __repr__(self):
        return f'<UserLevels {self.level}>'

class Zulageposition(db.Model):
    __tablename__ = 'zulageposition'
    rv_pos = db.Column('RV_Pos', db.Integer, primary_key=True)
    bezeichnung = db.Column('Bezeichnung', db.String(255))
    laenge = db.Column('Laenge', db.String(255))
    preis = db.Column('Preis', db.String(255))
    angelegt_dat = db.Column('AngelegtDat', db.String(255))
    angelegt_durch = db.Column('Angelegt_durch', db.String(255))
    geaendert_dat = db.Column('GeaendertDat', db.String(255))
    geaendert_durch = db.Column('Geaendert_durch', db.String(255))

    def __repr__(self):
        return f'<Zulageposition {self.rv_pos}>'

class TblBaustellen(db.Model):
    __tablename__ = 'tbl_baustellen'
    id = db.Column('ID', db.Integer, primary_key=True)
    bezeichnung = db.Column('Baustellenbezeichung', db.String(255))
    auftraggeber = db.Column('Auftraggeber', db.String(255))

class TblEigenschaftenDB(db.Model):
    __tablename__ = 'tbl_eigenschaften_db'
    eigenschaft = db.Column('Eigenschaft', db.String(255), primary_key=True)
    wert = db.Column('Wert', db.String(255))
    bemerkung = db.Column('Bemerkung', db.String(255))

    def __repr__(self):
        return f'<TblEigenschaftenDB {self.eigenschaft}>'

class tblKraftwerk(db.Model):
    __tablename__ = 'tblKraftwerk'
    name = db.Column('Kraftwerkname', db.String(255), primary_key=True, unique=True)
    partner_id = db.Column('PartnerId', db.Integer)

    def __repr__(self):
        return f'<Kraftwerk {self.name}>'

    def to_dict(self):
        return {
            'name': self.name,
            'partner_id': self.partner_id
        }

    @staticmethod
    def get_next_kraftwerk_suffix(partner_id):
        count = tblKraftwerk.query.filter_by(partner_id=partner_id).count()
        return count + 1

class TblPartner(db.Model):
    __tablename__ = 'tblPartner'
    nummer = db.Column('Partnernummer', db.Integer, primary_key=True)
    anrede = db.Column('Anrede', db.String(255))
    vorname = db.Column('Vorname', db.String(255))
    nachname = db.Column('Nachname', db.String(255))
    telefonnummer = db.Column('Telefonnummer', db.String(255))
    telefaxnummer = db.Column('Telefaxnummer', db.String(255))
    email = db.Column('Email', db.String(255))

    def __repr__(self):
        return f'<tblPartner {self.nummer}>'
    
    def to_dict(self):
        return {
            'nummer': self.nummer,
            'anrede': self.anrede,
            'vorname': self.vorname,
            'nachname': self.nachname,
            'telefonnummer': self.telefonnummer,
            'telefaxnummer': self.telefaxnummer,
            'email': self.email
        }

class TblTmpEPneu(db.Model):
    __tablename__ = 'tbl_tmp_ep_neu'
    rv_pos = db.Column('RV_Pos', db.Integer, primary_key=True)
    dn = db.Column('DN', db.Integer)
    da = db.Column('DA', db.String(255))
    is_ = db.Column('IS', db.String(255))
    Benennung = db.Column('Benennung', db.String(255))
    me = db.Column('ME', db.String(255))
    ep_alt = db.Column('EPAlt', db.String(255))
    ep_neu = db.Column('EPNeu', db.String(255))
    angelegt_dat = db.Column('AngelegtDat', db.String(255))
    angelegt_durch = db.Column('Angelegt_durch', db.String(255))
    geaendert_dat = db.Column('GeaendertDat', db.String(255))
    geaendert_durch = db.Column('Geaendert_durch', db.String(255))
    leistung = db.Column('Leistung', db.String(255))

    def __repr__(self):
        return f'<TblTmpEPneu {self.rv_pos}>'

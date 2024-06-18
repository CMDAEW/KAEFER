from flask import Blueprint, app, render_template, request, redirect, url_for, flash, jsonify, make_response, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date, datetime
from weasyprint import HTML
from . import db
from .forms import LohnsatzForm, KraftwerkForm, ArbeitsbescheinigungForm, LohnzulagenForm, CreateUserForm, PartnerForm, LoginForm, ArbeitsbeschKopfdatenForm, ArbeitsbeschDetaildatenForm, ProjectForm
from .models import EP, Lohnsaetze, Lohnzulagen, tblKraftwerk, ArbeitsbeschKopfdaten, ArbeitsbeschDetaildaten, TblPartner, Tbl_Einheit, User, TblBaustellen
from .utils import get_kraftwerk_choices, get_rahmenvertragsnr_choices, get_projekt_choices, get_auftragsnr_choices, get_baustelle_choices, get_auftragsnr_kaefer_choices
import logging
from decimal import Decimal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

@main.route('/Arbeitsbescheinigung_erstellen', methods=['GET', 'POST'])
@login_required
def Arbeitsbescheinigung_erstellen():
    kraftwerk_id = getKraftwerk()  # Replace with your actual logic to get the Kraftwerk ID
    detaildaten_form = ArbeitsbeschDetaildatenForm()
    detaildaten_form.update_lohnart_choices(kraftwerk_id)  # Update choices with correct kraftwerk_id
    kopfdaten_form = ArbeitsbeschKopfdatenForm()

    if request.method == 'POST':
        auftraggeber = kopfdaten_form.auftraggeber.data
        detaildaten_form.update_lohnart_choices(kraftwerk_id)  # Ensure choices are updated

        # Calculate the total hours from the form data
        so = detaildaten_form.so.data or Decimal(0)
        mo = detaildaten_form.mo.data or Decimal(0)
        di = detaildaten_form.di.data or Decimal(0)
        mi = detaildaten_form.mi.data or Decimal(0)
        do = detaildaten_form.do.data or Decimal(0)
        fr = detaildaten_form.fr.data or Decimal(0)
        sa = detaildaten_form.sa.data or Decimal(0)

        gesamtstunden = so + mo + di + mi + do + fr + sa
        detaildaten_form.gesamtstunden.data = float(gesamtstunden)

        # Get the STD_Satz value from Lohnsaetze based on the selected lohnart
        selected_lohnart = detaildaten_form.lohnart.data
        lohn_satz = Lohnsaetze.query.filter_by(lohnart=selected_lohnart).first()

        if lohn_satz:
            std_satz = Decimal(lohn_satz.std_satz.replace(',', '.'))  # Convert to Decimal
        else:
            flash('Selected Lohnart not found in Lohnsaetze table', 'danger')
            return render_template('Arbeitsbescheinigung_erstellen.html', detaildaten_form=detaildaten_form, kopfdaten_form=kopfdaten_form)

        # Calculate gesamtpreis
        gesamtpreis = gesamtstunden * std_satz
        detaildaten_form.gesamtpreis.data = float(gesamtpreis)  # Convert back to float for the form

        if not detaildaten_form.validate_on_submit():
            flash('Detaildaten form validation failed', 'danger')
            for field, errors in detaildaten_form.errors.items():
                for error in errors:
                    flash(f'Error in {getattr(detaildaten_form, field).label.text}: {error}', 'danger')

        if not kopfdaten_form.validate_on_submit():
            flash('Kopfdaten form validation failed', 'danger')
            for field, errors in kopfdaten_form.errors.items():
                for error in errors:
                    flash(f'Error in {getattr(kopfdaten_form, field).label.text}: {error}', 'danger')

        if detaildaten_form.validate_on_submit() and kopfdaten_form.validate_on_submit():
            try:
                # Extract data from kopfdaten_form and create a new ArbeitsbeschKopfdaten instance
                kopfdaten = ArbeitsbeschKopfdaten(
                    auftraggeber=kopfdaten_form.auftraggeber.data,
                    rahmenvertrags_nr=kopfdaten_form.rahmenvertrags_nr.data,
                    projekt=kopfdaten_form.projekt.data,
                    auftrags_nr_kaefer=kopfdaten_form.auftrags_nr_kaefer.data,
                    baustelle=kopfdaten_form.baustelle.data,
                    kommisionsnummer=kopfdaten_form.kommisionsnummer.data
                )
                db.session.add(kopfdaten)
                db.session.commit()

                # Refresh the instance to ensure it is in the session
                db.session.refresh(kopfdaten)

                # Extract data from detaildaten_form and create a new ArbeitsbeschDetaildaten instance
                detaildaten = ArbeitsbeschDetaildaten(
                    Benennung=detaildaten_form.Benennung.data if detaildaten_form.Benennung.data != 'new_entry' else request.form.get('new_Benennung'),
                    lohnart=detaildaten_form.lohnart.data if detaildaten_form.lohnart.data != 'new_entry' else request.form.get('new_lohnart'),
                    So=detaildaten_form.so.data,
                    Mo=detaildaten_form.mo.data,
                    Di=detaildaten_form.di.data,
                    Mi=detaildaten_form.mi.data,
                    Do=detaildaten_form.do.data,
                    Fr=detaildaten_form.fr.data,
                    Sa=detaildaten_form.sa.data,
                    gesamtpreis=detaildaten_form.gesamtpreis.data,
                    gesamtstunden=detaildaten_form.gesamtstunden.data,
                    Zu_Std2=detaildaten_form.zu_std2.data,
                    Zu_Std4=detaildaten_form.zu_std4.data,
                    Zu_Std5=detaildaten_form.zu_std5.data,
                    Zu_Std6=detaildaten_form.zu_std6.data,
                    ArbBeschNr=kopfdaten.id  # Use the id from the created kopfdaten
                )
                db.session.add(detaildaten)
                db.session.commit()

                flash('Data created successfully!', 'success')
                return redirect(url_for('main.Arbeitsbescheinigung_erstellen'))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred while creating data: {str(e)}', 'danger')
                print(str(e))  # Print the error to the console/log

    # Prepopulate ArbBeschNr with the latest entry number
    latest_kopfdaten = ArbeitsbeschKopfdaten.query.order_by(ArbeitsbeschKopfdaten.id.desc()).first()
    if latest_kopfdaten:
        detaildaten_form.ArbBeschNr.data = latest_kopfdaten.id

    return render_template('Arbeitsbescheinigung_erstellen.html', detaildaten_form=detaildaten_form, kopfdaten_form=kopfdaten_form)

def update_lohnart_choices(form, kraftwerk_id):
    choices = get_lohnart_choices_from_db(kraftwerk_id)
    form.lohnart.choices = choices

def get_lohnart_choices_from_db(kraftwerk_id):
    choices = [(entry.lohnart, entry.lohnart) for entry in Lohnsaetze.query.filter_by(kraftwerk_id=kraftwerk_id).distinct(Lohnsaetze.lohnart).all()]
    print(f'Lohnart choices for kraftwerk_id {kraftwerk_id}: {choices}')  # Debugging
    return choices

def getKraftwerk():
    # Replace this with actual logic to get the Kraftwerk ID
    return '1'

@main.route('/get_std_satz', methods=['POST'])
@login_required
def get_std_satz():
    data = request.get_json()
    lohnart = data.get('lohnart')
    lohn_satz = Lohnsaetze.query.filter_by(lohnart=lohnart).first()
    
    if lohn_satz:
        return jsonify({'std_satz': lohn_satz.std_satz})
    else:
        return jsonify({'std_satz': '0'})

@main.route('/get_lohnart_choices', methods=['POST'])
@login_required
def get_lohnart_choices():
    data = request.get_json()
    auftraggeber = data.get('auftraggeber')
    lohnart_choices = [(entry.lohnart, entry.lohnart) for entry in Lohnsaetze.query.filter_by(kraftwerk_id=auftraggeber).distinct(Lohnsaetze.lohnart).all()]
    return jsonify(lohnart_choices)

@main.route('/some_route', methods=['GET', 'POST'])
def some_view_function():
    form = ProjectForm()
    form.auftraggeber.choices = [('new', 'Add New')] + get_kraftwerk_choices()
    form.rahmenvertrags_nr.choices = [('new', 'Add New')] + get_rahmenvertragsnr_choices()
    form.projekt.choices = [('new', 'Add New')] + get_projekt_choices()
    form.auftrags_nr.choices = [('new', 'Add New')] + get_auftragsnr_choices()
    form.baustelle.choices = [('new', 'Add New')] + get_baustelle_choices()
    form.auftrags_nr_kaefer.choices = [('new', 'Add New')] + get_auftragsnr_kaefer_choices()
    
    if form.validate_on_submit():
        # Handle the form submission
        pass
    return render_template('some_template.html', form=form)

@main.route('/project/new', methods=['GET', 'POST'])
def new_project():
    form = ProjectForm()
    form.auftraggeber.choices = [('new', 'Add New')] + get_kraftwerk_choices()
    form.rahmenvertrags_nr.choices = [('new', 'Add New')] + get_rahmenvertragsnr_choices()
    form.projekt.choices = [('new', 'Add New')] + get_projekt_choices()
    form.auftrags_nr.choices = [('new', 'Add New')] + get_auftragsnr_choices()
    form.baustelle.choices = [('new', 'Add New')] + get_baustelle_choices()
    form.auftrags_nr_kaefer.choices = [('new', 'Add New')] + get_auftragsnr_kaefer_choices()
    
    if form.validate_on_submit():
        if form.auftraggeber.data == 'new':
            new_kraftwerkname = form.new_kraftwerkname.data
            if not new_kraftwerkname:
                flash('Please provide a name for the new Kraftwerk', 'error')
                return render_template('project_form.html', form=form)
            # Add the new Kraftwerk to the database
            new_kraftwerk = tblKraftwerk(name=new_kraftwerkname)
            db.session.add(new_kraftwerk)
            db.session.commit()
            auftraggeber = new_kraftwerkname
        else:
            auftraggeber = form.auftraggeber.data

        rahmenvertrags_nr = form.rahmenvertrags_nr.data
        if rahmenvertrags_nr == 'new':
            rahmenvertrags_nr = form.new_rahmenvertragsnr.data

        projekt = form.projekt.data
        if projekt == 'new':
            projekt = form.new_projekt.data

        auftrags_nr = form.auftrags_nr.data
        if auftrags_nr == 'new':
            auftrags_nr = form.new_auftrags_nr.data

        baustelle = form.baustelle.data
        if baustelle == 'new':
            baustelle = form.new_baustelle.data

        auftrags_nr_kaefer = form.auftrags_nr_kaefer.data
        if auftrags_nr_kaefer == 'new':
            auftrags_nr_kaefer = form.new_auftrags_nr_kaefer.data

        # Process form data and save to database
        kopfdaten = ArbeitsbeschKopfdaten(
            auftraggeber=auftraggeber,
            rahmenvertrags_nr=rahmenvertrags_nr,
            projekt=projekt,
            kommisionsnummer=auftrags_nr,
            bestell_datum=form.bestelldatum.data,
            baustelle=baustelle,
            k_trv=form.k_trv.data,
            auftrags_nr_kaefer=auftrags_nr_kaefer,
            ausfuehrungsbeginn=form.ausfuehrungsbeginn.data,
            ausfuehrungsende=form.ausfuehrungsende.data,
            bemerkung=form.bemerkung.data,
            angelegt_dat=date.today(),
            angelegt_durch=current_user.name,
            geaendert_dat=date.today(),
            geaendert_durch=current_user.name
        )
        db.session.add(kopfdaten)
        db.session.commit()
        return redirect(url_for('main.index'))  # Redirect to a success page or index
    
    return render_template('project_form.html', form=form)

# The login manager should be initialized in the application factory function (create_app) in __init__.py
# so it is already set up when the blueprint is registered

@main.route('/service-worker.js')
def service_worker():
    return current_app.send_static_file('service-worker.js')

@main.route('/create_arbeitsbescheinigung', methods=['GET', 'POST'])
@login_required
def create_arbeitsbescheinigung():
    kraftwerk_id = current_user.kraftwerk_id
    form = ArbeitsbeschKopfdatenForm(kraftwerk_id=kraftwerk_id)
    detail_form = ArbeitsbeschDetaildatenForm(kraftwerk_id=kraftwerk_id)
    
    if request.method == 'POST':
        logger.info("Received POST request.")
        
        if form.validate_on_submit() and detail_form.validate_on_submit():
            logger.info("Form and detail form validated successfully.")
            
            def to_float(value):
                try:
                    return float(value) if value is not None else 0.0
                except (TypeError, ValueError):
                    return 0.0

            total_hours = sum([
                to_float(detail_form.mo.data),
                to_float(detail_form.di.data),
                to_float(detail_form.mi.data),
                to_float(detail_form.do.data),
                to_float(detail_form.fr.data),
                to_float(detail_form.sa.data),
                to_float(detail_form.so.data)
            ])
            detail_form.gesamtstunden.data = total_hours

            selected_lohn = Lohnsaetze.query.filter_by(lohnart=detail_form.lohn_art.data).first()
            if selected_lohn and selected_lohn.std_satz:
                std_satz = selected_lohn.std_satz.replace(',', '.')
                total_price = total_hours * float(std_satz)
                detail_form.gp.data = total_price
                logger.info(f"Total price calculated: {total_price}")
            else:
                total_price = 0.0
                logger.warning("Selected Lohnsaetze not found or std_satz is None.")

            detaildaten = ArbeitsbeschDetaildaten(
                rv_pos=detail_form.rv_pos.data,
                Benennung=detail_form.monteur.data,
                menge=detail_form.menge.data,
                me=detail_form.me.data,
                ep=detail_form.ep.data,
                per=detail_form.per.data,
                so=to_float(detail_form.so.data),
                mo=to_float(detail_form.mo.data),
                di=to_float(detail_form.di.data),
                mi=to_float(detail_form.mi.data),
                do=to_float(detail_form.do.data),
                fr=to_float(detail_form.fr.data),
                sa=to_float(detail_form.sa.data),
                lohnart=detail_form.lohn_art.data,
                basis_ep=to_float(detail_form.basis_ep.data),
                zulageart1=detail_form.zulage_art1.data,
                zu_std1=to_float(detail_form.zu_std1.data),
                zulageart2=detail_form.zulage_art2.data,
                zu_std2=to_float(detail_form.zu_std2.data),
                zulageart3=detail_form.zulage_art3.data,
                zu_std3=to_float(detail_form.zu_std3.data),
                zulageart4=detail_form.zulage_art4.data,
                zu_std4=to_float(detail_form.zu_std4.data),
                gp=total_price,
                satz_nr=detail_form.satz_nr.data,
                gruppe=detail_form.gruppe.data,
                angelegtdat=detail_form.angelegt_dat.data,
                angelegt_durch=detail_form.angelegt_durch.data,
                geaendertdat=detail_form.geaendert_dat.data,
                geaendert_durch=detail_form.geaendert_durch.data,
                gesamtstunden=total_hours,
                gesamtpreis=total_price,
                kraftwerkname=detail_form.kraftwerkname.data,
                ArbBeschNr=detail_form.ArbBeschNr.data
            )

            try:
                db.session.add(detaildaten)
                db.session.commit()
                flash('Arbeitsbescheinigung erfolgreich erstellt!', 'success')
                logger.info("Arbeitsbescheinigung successfully created and committed to the database.")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error committing to the database: {e}")
                flash('An error occurred while creating Arbeitsbescheinigung.', 'danger')
                
            return redirect(url_for('main.home'))
        else:
            logger.warning("Form or detail form validation failed.")
            logger.info(f"Form errors: {form.errors}")
            logger.info(f"Detail form errors: {detail_form.errors}")
    
    return render_template('create_arbeitsbescheinigung.html', form=form, detail_form=detail_form)

@main.route('/lohnsaetze', methods=['GET', 'POST'])
@login_required
def lohnsaetze():
    lohnsaetze_id = request.args.get('edit_id')
    lohnsaetze = None
    selected_kraftwerk_id = request.form.get('kraftwerk_id') if request.method == 'POST' else None

    if lohnsaetze_id:
        lohnsaetze = Lohnsaetze.query.get(lohnsaetze_id)
        selected_kraftwerk_id = lohnsaetze.kraftwerk_id if lohnsaetze else selected_kraftwerk_id

    form = LohnsatzForm(obj=lohnsaetze)

    if selected_kraftwerk_id:
        form.kraftwerk_id.data = selected_kraftwerk_id

    if form.validate_on_submit():
        lohnsaetze_id = request.form.get('lohnsaetze_id')

        if form.kraftwerk_id.data == 'new_entry':
            if tblKraftwerk.query.filter_by(name=form.new_kraftwerk_name.data).first():
                flash('Kraftwerk existiert bereits', 'danger')
                return redirect(url_for('main.lohnsaetze', kraftwerk_id=selected_kraftwerk_id))
            new_kw = tblKraftwerk(name=form.new_kraftwerk_name.data)
            db.session.add(new_kw)
            db.session.commit()
            form.kraftwerk_id.data = new_kw.name

        if lohnsaetze_id:
            lohnsaetze = Lohnsaetze.query.get(lohnsaetze_id)
            if not lohnsaetze:
                flash('Lohnsaetze not found!', 'danger')
                return redirect(url_for('main.lohnsaetze', kraftwerk_id=selected_kraftwerk_id))

            existing_entry = Lohnsaetze.query.filter_by(kraftwerk_id=form.kraftwerk_id.data, lohnart=form.lohnart.data).first()
            if existing_entry and existing_entry.Id != lohnsaetze.Id:
                flash('Diese lohnart besteht für dieses Kraftwerk bereits', 'danger')
                return redirect(url_for('main.lohnsaetze', kraftwerk_id=selected_kraftwerk_id))

            lohnsaetze.kraftwerk_id = form.kraftwerk_id.data
            lohnsaetze.lohnart = form.lohnart.data
            lohnsaetze.std_satz = form.get_std_satz()  # Use the custom getter
            lohnsaetze.basis_satz = form.get_basis_satz()  # Use the custom getter
            lohnsaetze.bezeichnung = form.bezeichnung.data
            lohnsaetze.geaendert_dat = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            lohnsaetze.geaendert_durch = current_user.name
            try:
                db.session.commit()
                flash('Lohnsaetze updated successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error updating Lohnsaetze: ' + str(e), 'danger')
        else:
            existing_entry = Lohnsaetze.query.filter_by(kraftwerk_id=form.kraftwerk_id.data, lohnart=form.lohnart.data).first()
            if existing_entry:
                flash('Diese lohnart besteht für dieses Kraftwerk bereits', 'danger')
                return redirect(url_for('main.lohnsaetze', kraftwerk_id=selected_kraftwerk_id))

            new_lohnsaetze = Lohnsaetze(
                kraftwerk_id=form.kraftwerk_id.data,
                lohnart=form.lohnart.data,
                std_satz=form.get_std_satz(),  # Use the custom getter
                basis_satz=form.get_basis_satz(),  # Use the custom getter
                bezeichnung=form.bezeichnung.data,
                angelegt_dat=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                angelegt_durch=current_user.name
            )
            db.session.add(new_lohnsaetze)
            try:
                db.session.commit()
                flash('Lohnsaetze created successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error creating Lohnsaetze: ' + str(e), 'danger')

        return redirect(url_for('main.lohnsaetze', kraftwerk_id=form.kraftwerk_id.data))

    kraftwerke_list = tblKraftwerk.query.all()
    kraftwerke = {kw.name: kw.name for kw in kraftwerke_list}

    lohnsaetze_entries = Lohnsaetze.query.filter_by(kraftwerk_id=selected_kraftwerk_id).all() if selected_kraftwerk_id else []
    lohnsaetze_entries_dicts = [entry.to_dict() for entry in lohnsaetze_entries]

    return render_template('lohnsaetze.html', form=form, lohnsaetze_entries=lohnsaetze_entries_dicts, kraftwerke=kraftwerke, selected_kraftwerk_id=selected_kraftwerk_id)


@main.route('/delete_lohnsaetze/<int:id>', methods=['POST'])
@login_required
def delete_lohnsaetze(id):
    lohnsaetze = Lohnsaetze.query.get_or_404(id)
    try:
        db.session.delete(lohnsaetze)
        db.session.commit()
        return jsonify({'message': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'error', 'details': str(e)})

@main.route('/get_lohnsaetze/<kraftwerk_id>')
@login_required
def get_lohnsaetze(kraftwerk_id):
    lohnsaetze_entries = Lohnsaetze.query.filter_by(kraftwerk_id=kraftwerk_id).all()
    return jsonify([ls.to_dict() for ls in lohnsaetze_entries])

@main.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    response = redirect(url_for('main.login'))
    response.set_cookie('session', '', expires=0)
    flash('You have been logged out.', 'success')
    return response

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            greeting_message = f"Moin, {user.name}! Viel Spaß bei der Arbeit."
            flash(f' {greeting_message}', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@main.route('/aufmass_erstellen')
def aufmass_erstellen():
    return render_template('aufmass_erstellen.html')

@main.route('/aufmass_bearbeiten')
def aufmass_bearbeiten():
    return render_template('aufmass_bearbeiten.html')

@main.route('/aufmass_berichte_anzeigen')
def aufmass_berichte_anzeigen():
    return render_template('aufmass_berichte_anzeigen.html')

@main.route('/aufmass_berichte_drucken')
def aufmass_berichte_drucken():
    return render_template('aufmass_berichte_drucken.html')


@main.route('/create_user', methods=['GET', 'POST'])
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        username = form.username.data
        raw_password = form.password.data

        new_user = User(name=username)
        new_user.set_password(raw_password)
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('main.home'))

    return render_template('create_user.html', form=form)

@main.route('/arb_besch_eingeben_HF', methods=['GET', 'POST'])
@login_required
def ArbBesch_eingeben_HF():
    form = ArbeitsbescheinigungForm()

    if form.validate_on_submit():
        form_data = {
            'auftraggeber': form.auftraggeber.data,
            'rahmenvertrags_nr': form.rahmenvertrags_nr.data,
            'projekt': form.projekt.data,
            'auftrags_nr': form.auftrags_nr.data,
            'bestelldatum': form.bestelldatum.data.strftime('%d.%m.%Y'),
            'baustelle': form.baustelle.data,
            'kraftwerk': form.kraftwerk.data,
            'trv': form.trv.data,
            'bemerkung': form.bemerkung.data,
            'erstellt_datum': datetime.now().strftime('%d.%m.%Y')
        }

        new_arbeitsbesch = ArbeitsbeschKopfdaten(
            auftraggeber=form_data['auftraggeber'],
            Rahmenvertrags_nr=form_data['rahmenvertrags_nr'],
            projekt=form_data['projekt'],
            auftrags_nr_kaefer=form_data['auftrags_nr'],
            bestell_datum=form_data['bestelldatum'],
            baustelle=form_data['baustelle'],
            kraftwerk_id=form_data['auftraggeber'],
            k_trv=form_data['trv'],
            bemerkung=form_data['bemerkung'],
            erstellt_datum=form_data['erstellt_datum']
        )
        db.session.add(new_arbeitsbesch)
        db.session.commit()

        html_out = render_template('Report_ArbBesch.html', **form_data)
        pdf = HTML(string=html_out).write_pdf()

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=Arbeitsbescheinigung.pdf'
    
        flash('Arbeitsbescheinigung created successfully!', 'success')
        return response

    return render_template('ArbBesch_eingeben_HF.html', form=form)

@main.route('/aufmass')
@login_required
def aufmass():
    return render_template('aufmass.html')

@main.route('/verwaltung')
def verwaltung():
    return render_template('verwaltung.html')

@main.route('/')
@main.route('/home')
@login_required
def home():
    return render_template(
        'index.html',
        title='KAEFER Industrie GmbH',
        year=datetime.now().year,
    )


@main.route('/contact')
def contact():
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@main.route('/about')
def about():
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@main.route('/view_ep')
@login_required
def view_ep():
    eps = EP.query.all()
    return render_template(
        'view_ep.html',
        title='View EP Data',
        year=datetime.now().year,
        eps=eps
    )

@main.route('/user/<username>')
@login_required
def show_user_profile(username):
    return f'Profil von {username}'

@main.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    if request.method == 'POST':
        return 'Formular gesendet!'
    else:
        return 'Senden Sie ein Formular.'

@main.route('/arbeitsbescheinigung', methods=['GET', 'POST'])
@login_required
def arbeitsbescheinigung():
    form = ArbeitsbescheinigungForm()
    if form.validate_on_submit():
        auftraggeber = form.auftraggeber.data or form.new_auftraggeber.data
        rahmenvertrags_nr = form.rahmenvertrags_nr.data or form.new_rahmenvertrags_nr.data
        projekt = form.projekt.data or form.new_projekt.data
        auftrags_nr = form.auftrags_nr.data or form.new_auftrags_nr.data
        bestelldatum = form.bestelldatum.data
        baustelle = form.baustelle.data or form.new_baustelle.data
        kraftwerk = form.kraftwerk.data
        trv = form.trv.data
        bemerkung = form.bemerkung.data

        new_entry = ArbeitsbeschKopfdaten(
            auftraggeber=auftraggeber,
            Rahmenvertrags_nr=rahmenvertrags_nr,
            projekt=projekt,
            auftrags_nr_kaefer=auftrags_nr,
            bestell_datum=bestelldatum,
            baustelle=baustelle,
            k_trv=1 if trv else 0,
            bemerkung=bemerkung
        )
        db.session.add(new_entry)
        db.session.commit()

        return redirect(url_for('main.arbeitsbescheinigung'))

    return render_template('ArbBesch_eingeben_HF.html', form=form)

    auftraggeber_options = ArbeitsbeschKopfdaten.query.with_entities(ArbeitsbeschKopfdaten.auftraggeber).distinct().all()
    rahmenvertrags_options = ArbeitsbeschKopfdaten.query.with_entities(ArbeitsbeschKopfdaten.Rahmenvertrags_nr).distinct().all()
    projekt_options = ArbeitsbeschKopfdaten.query.with_entities(ArbeitsbeschKopfdaten.projekt).distinct().all()
    auftrags_nr_options = ArbeitsbeschKopfdaten.query.with_entities(ArbeitsbeschKopfdaten.auftrags_nr_kaefer).distinct().all()
    baustelle_options = ArbeitsbeschKopfdaten.query.with_entities(ArbeitsbeschKopfdaten.baustelle).distinct().all()

    auftraggeber_options = [x[0] for x in auftraggeber_options]
    rahmenvertrags_options = [x[0] for x in rahmenvertrags_options]
    projekt_options = [x[0] for x in projekt_options]
    auftrags_nr_options = [x[0] for x in auftrags_nr_options]
    baustelle_options = [x[0] for x in baustelle_options]

    return render_template(
        'ArbBesch_eingeben_HF.html',
        auftraggeber_options=auftraggeber_options,
        rahmenvertrags_options=rahmenvertrags_options,
        projekt_options=projekt_options,
        auftrags_nr_options=auftrags_nr_options,
        baustelle_options=baustelle_options
    )

@main.route('/systemzugang')
def systemzugang():
    return render_template('systemzugang.html')

@main.route('/aufmass/action', methods=['POST'])
@login_required
def aufmass_action():
    selected_option = request.form.get('aufmass_option')
    
    if selected_option == 'hinzufuegen':
        return redirect(url_for('main.hinzufuegen'))
    elif selected_option == 'bearbeiten':
        return redirect(url_for('main.bearbeiten'))
    elif selected_option == 'berichte_anzeigen':
        return redirect(url_for('main.berichte_anzeigen'))
    elif selected_option == 'summe_drucken':
        return redirect(url_for('main.summe_drucken'))
    else:
        return redirect(url_for('main.login'))

@main.route('/hinzufuegen')
@login_required
def hinzufuegen():
    return "Hinzufügen Page"

@main.route('/arbeitsbescheinigung_hinzufuegen')
@login_required
def arbeitsbescheinigung_hinzufuegen():
    return render_template('arbeitsbescheinigung_hinzufuegen.html')

@main.route('/arbeitsbescheinigung_berichte_drucken')
@login_required
def arbeitsbescheinigung_berichte_drucken():
    return render_template('arbeitsbescheinigung_berichte_drucken.html')

@main.route('/arbeitsbescheinigung_bearbeiten')
@login_required
def arbeitsbescheinigung_bearbeiten():
    return render_template('arbeitsbescheinigung_bearbeiten.html')

@main.route('/arbeitsbescheinigung_berichte_anzeigen')
def arbeitsbescheinigung_berichte_anzeigen():
    return render_template('arbeitsbescheinigung_berichte_anzeigen.html')

@main.route('/bearbeiten')
@login_required
def bearbeiten():
    return "Bearbeiten Page"

@main.route('/berichte_anzeigen')
@login_required
def berichte_anzeigen():
    return "Berichte Anzeigen Page"

@main.route('/summe_drucken')
@login_required
def summe_drucken():
    return "Summe Drucken Page"

@main.route('/ArbBesch_drucken')
@login_required
def ArbBesch_drucken():
    return render_template('ArbBesch_drucken.html')

@main.route('/ArbBesch_eingeben_UF_Mat')
@login_required
def ArbBesch_eingeben_UF_Mat():
    return render_template('ArbBesch_eingeben_UF_Mat.html')

@main.route('/ArbBesch_eingeben_UF_STD')
@login_required
def ArbBesch_eingeben_UF_STD():
    return render_template('ArbBesch_eingeben_UF_STD.html')

@main.route('/Aufmass_Drucken')
@login_required
def Aufmass_Drucken():
    return render_template('Aufmass_Drucken.html')

@main.route('/Aufmasse_eingeben_HF')
@login_required
def Aufmasse_eingeben_HF():
    return render_template('Aufmasse_eingeben_HF.html')

@main.route('/Aufmasse_eingeben_UF_FP')
@login_required
def Aufmasse_eingeben_UF_FP():
    return render_template('Aufmasse_eingeben_UF_FP.html')

@main.route('/Aufmasse_eingeben_UF_mST')
@login_required
def Aufmasse_eingeben_UF_mST():
    return render_template('Aufmasse_eingeben_UF_mST.html')

@main.route('/Aufmasse_eingeben_UF_Qm')
@login_required
def Aufmasse_eingeben_UF_Qm():
    return render_template('Aufmasse_eingeben_UF_Qm.html')

@main.route('/Auswahl_ArbBesch')
@login_required
def Auswahl_ArbBesch():
    return render_template('Auswahl_ArbBesch.html')

@main.route('/Auswahl_ArbeitsBeschBearbeitung')
@login_required
def Auswahl_ArbeitsBeschBearbeitung():
    return render_template('Auswahl_ArbeitsBeschBearbeitung.html')

@main.route('/Auswahl_Aufmass')
@login_required
def Auswahl_Aufmass():
    return render_template('Auswahl_Aufmass.html')

@main.route('/Auswahl_Aufmassbearbeitung')
@login_required
def Auswahl_Aufmassbearbeitung():
    return render_template('Auswahl_Aufmassbearbeitung.html')

@main.route('/Faktoren_pflegen_HF')
@login_required
def Faktoren_pflegen_HF():
    return render_template('Faktoren_pflegen_HF.html')

@main.route('/Faktoren_pflegen_UF')
@login_required
def Faktoren_pflegen_UF():
    return render_template('Faktoren_pflegen_UF.html')

@main.route('/Frm_ArbBescheinigungOpt_Report')
@login_required
def Frm_ArbBescheinigungOpt_Report():
    return render_template('Frm_ArbBescheinigungOpt_Report.html')

@main.route('/Frm_Aufmassbetraege')
@login_required
def Frm_Aufmassbetraege():
    return render_template('Frm_Aufmassbetraege.html')

@main.route('/Frm_AufmassOpt_Report')
@login_required
def Frm_AufmassOpt_Report():
    return render_template('Frm_AufmassOpt_Report.html')

@main.route('/Frm_DA')
@login_required
def Frm_DA():
    return render_template('Frm_DA.html')

@main.route('/Frm_DN')
@login_required
def Frm_DN():
    return render_template('Frm_DN.html')

@main.route('/Frm_Einheit')
@login_required
def Frm_Einheit():
    return render_template('Frm_Einheit.html')

@main.route('/Frm_Einheitspreise')
@login_required
def Frm_Einheitspreise():
    return render_template('Frm_Einheitspreise.html')

@main.route('/Frm_Einheitspreise_UF')
@login_required
def Frm_Einheitspreise_UF():
    return render_template('Frm_Einheitspreise_UF.html')

@main.route('/Frm_IS')
@login_required
def Frm_IS():
    return render_template('Frm_IS.html')

@main.route('/Frm_Isolierungselement')
@login_required
def Frm_Isolierungselement():
    return render_template('Frm_Isolierungselement.html')

@main.route('/Frm_Leistungsverzeichnis')
@login_required
def Frm_Leistungsverzeichnis():
    return render_template('Frm_Leistungsverzeichnis.html')

@main.route('/Frm_TmpEinheitspreise')
@login_required
def Frm_TmpEinheitspreise():
    return render_template('Frm_TmpEinheitspreise.html')

@main.route('/frmEinheitspreisänderung')
@login_required
def frmEinheitspreisänderung():
    return render_template('frmEinheitspreisänderung.html')

@main.route('/frmKraftwerk')
@login_required
def frmKraftwerk():
    return render_template('frmKraftwerk.html')

@main.route('/frmPartner')
@login_required
def frmPartner():
    return render_template('frmPartner.html')

@main.route('/Hauptübersicht')
@login_required
def Hauptübersicht():
    return render_template('Hauptübersicht.html')

@main.route('/HÜ_Datenpflege')
@login_required
def HÜ_Datenpflege():
    return render_template('HÜ_Datenpflege.html')

@main.route('/Leistungen')
@login_required
def Leistungen():
    return render_template('Leistungen.html')

@main.route('/Lohn_Pflegen', methods=['GET', 'POST'])
@login_required
def Lohn_Pflegen():
    form = LohnsatzForm()
    form.kraftwerk_id.choices = [(k.name, k.name) for k in tblKraftwerk.query.all()]
    
    if form.validate_on_submit():
        new_lohnsatz = Lohnsaetze(
            lohnart=form.lohnart.data,
            std_satz=form.std_satz.data,
            basis_satz=form.basis_satz.data,
            bezeichnung=form.bezeichnung.data,
            angelegt_durch=form.angelegt_durch.data,
            kraftwerk_id=form.kraftwerk_id.data,
            angelegt_dat=datetime.utcnow()
        )
        db.session.add(new_lohnsatz)
        db.session.commit()
        flash('Lohnsatz created successfully!', 'success')
        return redirect(url_for('main.Lohn_Pflegen'))
    return render_template('Lohn_Pflegen.html', form=form)

def get_new_partner_number():
    partners = TblPartner.query.order_by(TblPartner.nummer).all()
    for index, partner in enumerate(partners, start=1):
        partner.nummer = index
    db.session.commit()
    return len(partners) + 1

@main.route('/ansprechpartner', methods=['GET', 'POST'])
@login_required
def ansprechpartner():
    edit_id = request.args.get('edit_id')
    partner = None
    if edit_id:
        partner = TblPartner.query.get(edit_id)

    form = PartnerForm(obj=partner)

    if form.validate_on_submit():
        partner_id = form.partner_id.data
        if partner_id:
            partner = TblPartner.query.get(partner_id)
            if not partner:
                flash('Ansprechpartner not found!', 'danger')
                return redirect(url_for('main.ansprechpartner'))

            partner.anrede = form.anrede.data
            partner.vorname = form.vorname.data
            partner.nachname = form.nachname.data
            partner.telefonnummer = form.telefonnummer.data
            partner.telefaxnummer = form.telefaxnummer.data
            partner.email = form.email.data
            db.session.commit()
            flash('Ansprechpartner updated successfully!', 'success')
        else:
            new_nummer = get_new_partner_number()
            partner = TblPartner(
                nummer=new_nummer,
                anrede=form.anrede.data,
                vorname=form.vorname.data,
                nachname=form.nachname.data,
                telefonnummer=form.telefonnummer.data,
                telefaxnummer=form.telefaxnummer.data,
                email=form.email.data
            )
            db.session.add(partner)
            db.session.commit()
            flash('Ansprechpartner created successfully!', 'success')

        return redirect(url_for('main.ansprechpartner'))

    partners = TblPartner.query.all()
    return render_template('ansprechpartner.html', form=form, partners=partners, edit_id=edit_id)

@main.route('/delete_partner/<int:partner_id>', methods=['POST'])
@login_required
def delete_partner(partner_id):
    partner = TblPartner.query.get(partner_id)
    if partner:
        try:
            db.session.delete(partner)
            db.session.commit()
            get_new_partner_number()
            flash('Ansprechpartner deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting data: {e}', 'danger')
    else:
        flash('Ansprechpartner not found!', 'danger')
    return redirect(url_for('main.ansprechpartner'))

@main.route('/edit_partner/<int:partner_id>', methods=['GET', 'POST'])
@login_required
def edit_partner(partner_id):
    return redirect(url_for('main.ansprechpartner', edit_id=partner_id))

@main.route('/Kraftwerk_pflegen', methods=['GET', 'POST'])
@login_required
def Kraftwerk_pflegen():
    form = KraftwerkForm()
    if form.validate_on_submit():
        base_name = form.name.data

        existing_kraftwerk = tblKraftwerk.query.filter_by(name=base_name).first()
        if existing_kraftwerk:
            flash('Kraftwerkname already exists. Please choose a different name.', 'danger')
            return render_template('Kraftwerk_pflegen.html', form=form)
        
        partner_id = tblKraftwerk.query.count() + 1
        suffix = tblKraftwerk.get_next_kraftwerk_suffix(partner_id)
        new_name = f"{base_name}_{suffix}"

        new_kraftwerk = tblKraftwerk(
            name=new_name,
            partner_id=partner_id
        )
        db.session.add(new_kraftwerk)
        db.session.commit()
        flash('New Kraftwerk added successfully!', 'success')
        return redirect(url_for('main.home'))

    return render_template('Kraftwerk_pflegen.html', form=form)

@main.route('/LohnZulagen_pflegen_HF')
@login_required
def LohnZulagen_pflegen_HF():
    return render_template('LohnZulagen_pflegen_HF.html')

@main.route('/LohnZulagen_pflegen_UF')
@login_required
def LohnZulagen_pflegen_UF():
    return render_template('LohnZulagen_pflegen_UF.html')

@main.route('/Materialpreise_pflegen_HF')
@login_required
def Materialpreise_pflegen_HF():
    return render_template('Materialpreise_pflegen_HF.html')

@main.route('/Materialpreise_pflegen_UF')
@login_required
def Materialpreise_pflegen_UF():
    return render_template('Materialpreise_pflegen_UF.html')

@main.route('/User_Identifikation')
@login_required
def User_Identifikation():
    return render_template('User_Identifikation.html')

@main.route('/User_suchen')
@login_required
def User_suchen():
    return render_template('User_suchen.html')

@main.route('/UserPasswortAbfrage')
@login_required
def UserPasswortAbfrage():
    return render_template('UserPasswortAbfrage.html')

@main.route('/UserPflege_HF_Admin')
@login_required
def UserPflege_HF_Admin():
    return render_template('UserPflege_HF_Admin.html')

@main.route('/UserPflege_User')
@login_required
def UserPflege_User():
    return render_template('UserPflege_User.html')

@main.route('/UserPflege_UF')
@login_required
def UserPflege_UF():
    return render_template('UserPflege_UF.html')

@main.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    data = request.get_json()

    kopfdaten = ArbeitsbeschKopfdaten(
        auftraggeber=data['auftraggeber'],
        Rahmenvertrags_nr=data['rahmenvertrags_nr'],
        projekt=data['projekt'],
        auftrags_nr_kaefer=data['auftrags_nr'],
        bestell_datum=data['bestelldatum'],
        baustelle=data['baustelle'],
        kraftwerk=data['kraftwerk'],
        k_trv=data['trv'],
        bemerkung=data['bemerkung'],
        erstellt_datum=datetime.now().strftime('%d.%m.%Y')
    )
    db.session.add(kopfdaten)
    db.session.commit()

    report_data = {
        "auftraggeber": data['auftraggeber'],
        "rahmenvertrags_nr": data['rahmenvertrags_nr'],
        "projekt": data['projekt'],
        "auftrags_nr": data['auftrags_nr'],
        "bestelldatum": data['bestelldatum'],
        "baustelle": data['baustelle'],
        "kraftwerk": "Ja" if data['kraftwerk'] else "Nein",
        "trv": "Ja" if data['trv'] else "Nein",
        "bemerkung": data['bemerkung'],
        "erstellt_datum": datetime.now().strftime('%d.%m.%Y')
    }

    html_out = render_template('Report_ArbBesch.html', **report_data)
    pdf = HTML(string=html_out).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Arbeitsbescheinigung.pdf'
    
    return response

@main.route('/generate_list', methods=['POST'])
@login_required
def generate_list():
    html_out = render_template('Arbeitsbescheinigung_List.html')
    pdf = HTML(string=html_out).write_pdf()
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    
    return response

@main.route('/get_auftraggeber')
@login_required
def get_auftraggeber():
    auftraggeber_list = db.session.query(ArbeitsbeschKopfdaten.auftraggeber).distinct().all()
    auftraggeber_list = [item[0] for item in auftraggeber_list]
    return jsonify(auftraggeber_list)

@main.route('/create_kopfdaten', methods=['GET', 'POST'])
@login_required
def create_kopfdaten():
    form = ArbeitsbeschKopfdatenForm()

    if form.validate_on_submit():
        try:
            # Extract data from the form and create a new ArbeitsbeschKopfdaten instance
            kopfdaten = ArbeitsbeschKopfdaten(
                auftraggeber=form.auftraggeber.data,
                rahmenvertrags_nr=form.rahmenvertrags_nr.data,
                projekt=form.projekt.data,
                auftrags_nr_kaefer=form.auftrags_nr_kaefer.data,
                baustelle=form.baustelle.data,
                kommisionsnummer=form.kommisionsnummer.data
               
            )

            # Handle new Auftraggeber entry
            if form.auftraggeber.data == 'new_entry':
                new_auftraggeber = request.form.get('new_auftraggeber')
                if not new_auftraggeber:
                    flash('New Auftraggeber is required', 'danger')
                    return redirect(url_for('main.create_kopfdaten'))
                new_kw = tblKraftwerk(name=new_auftraggeber)
                db.session.add(new_kw)
                db.session.commit()
                kopfdaten.auftraggeber = new_kw.name

            # Handle new RahmvertragsNr entry
            if form.rahmenvertrags_nr.data == 'new_entry':
                new_rahmenvertrags_nr = request.form.get('new_rahmvertrags_nr')
                if not new_rahmenvertrags_nr:
                    flash('New RahmenvertragsNr is required', 'danger')
                    return redirect(url_for('main.create_kopfdaten'))
                kopfdaten.rahmenvertrags_nr = new_rahmenvertrags_nr

            # Handle new Projekt entry
            if form.projekt.data == 'new_entry':
                new_projekt = request.form.get('new_projekt')
                if not new_projekt:
                    flash('New Projekt is required', 'danger')
                    return redirect(url_for('main.create_kopfdaten'))
                kopfdaten.projekt = new_projekt

            # Handle new Kommisionsnummer entry
            if form.kommisionsnummer.data == 'new_entry':
                new_kommisionsnummer = request.form.get('new_kommisionsnummer')
                if not new_kommisionsnummer:
                    flash('New Kommisionsnummer is required', 'danger')
                    return redirect(url_for('main.create_kopfdaten'))
                kopfdaten.kommisionsnummer = new_kommisionsnummer

            # Handle new Baustelle entry
            if form.baustelle.data == 'new_entry':
                new_baustelle = request.form.get('new_baustelle')
                if not new_baustelle:
                    flash('New Baustelle is required', 'danger')
                    return redirect(url_for('main.create_kopfdaten'))
                new_baustelle_entry = TblBaustellen(bezeichnung=new_baustelle, auftraggeber=kopfdaten.auftraggeber)
                db.session.add(new_baustelle_entry)
                db.session.commit()
                kopfdaten.baustelle = new_baustelle_entry.bezeichnung

            # Handle new AuftragsNr KAEFER entry
            if form.auftrags_nr_kaefer.data == 'new_entry':
                new_auftrags_nr_kaefer = request.form.get('new_auftrags_nr_kaefer')
                if not new_auftrags_nr_kaefer:
                    flash('New AuftragsNr KAEFER is required', 'danger')
                    return redirect(url_for('main.create_kopfdaten'))
                kopfdaten.auftrags_nr_kaefer = new_auftrags_nr_kaefer

            db.session.add(kopfdaten)
            db.session.commit()
            flash('Kopfdaten created successfully!', 'success')
            return redirect(url_for('main.lohnsaetze'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error committing to the database: {e}")
            flash(f'An error occurred while creating Kopfdaten: {str(e)}', 'danger')

    return render_template('create_kopfdaten.html', form=form)

def parse_date(date_str):
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None

@main.route('/create_kraftwerk', methods=['GET', 'POST'])
@login_required
def create_kraftwerk():
    form = KraftwerkForm()
    form.partner_id.choices = [(partner.nummer, f"{partner.vorname} {partner.nachname}") for partner in TblPartner.query.all()]
    
    if form.validate_on_submit():
        existing_kraftwerk = tblKraftwerk.query.filter_by(name=form.kraftwerkname.data).first()
        if existing_kraftwerk:
            flash('A record with this Kraftwerkname already exists.', 'danger')
        else:
            kraftwerk = tblKraftwerk(
                name=form.kraftwerkname.data,
                partner_id=form.partner_id.data
            )
            db.session.add(kraftwerk)
            db.session.commit()
            flash('Kraftwerk created successfully!', 'success')
            return redirect(url_for('main.create_kraftwerk'))
    return render_template('create_kraftwerk.html', form=form)

@main.route('/manage_kraftwerk', methods=['GET', 'POST'])
@login_required
def manage_kraftwerk():
    form = KraftwerkForm()
    form.partner_id.choices = [(partner.nummer, f"{partner.vorname} {partner.nachname}") for partner in TblPartner.query.all()]

    if request.method == 'POST' and form.validate_on_submit():
        kraftwerk = tblKraftwerk(name=form.kraftwerkname.data, partner_id=form.partner_id.data)
        db.session.add(kraftwerk)
        db.session.commit()
        flash('Kraftwerk added successfully', 'success')
        return redirect(url_for('main.manage_kraftwerk'))

    kraftwerke = db.session.query(tblKraftwerk, TblPartner).join(TblPartner, tblKraftwerk.partner_id == TblPartner.nummer).all()
    return render_template('manage_kraftwerk.html', kraftwerke=kraftwerke, form=form)

@main.route('/delete_kraftwerk/<kraftwerk_name>', methods=['DELETE'])
@login_required
def delete_kraftwerk(kraftwerk_name):
    kraftwerk = tblKraftwerk.query.filter_by(name=kraftwerk_name).first()
    if kraftwerk:
        db.session.delete(kraftwerk)
        db.session.commit()
        return jsonify({'message': 'success'}), 200
    else:
        return jsonify({'message': 'not found'}), 404

@main.route('/lohnzulagen', methods=['GET', 'POST'])
@login_required
def lohnzulagen_pflegen():
    edit_id = request.args.get('edit_id')
    zulage = None
    if edit_id:
        zulage = Lohnzulagen.query.get(edit_id)

    form = LohnzulagenForm(obj=zulage)

    if form.validate_on_submit():
        zulage_id = form.zulage_id.data
        if zulage_id:
            zulage = Lohnzulagen.query.get(zulage_id)
            if not zulage:
                flash('Lohnzulage not found!', 'danger')
                return redirect(url_for('main.lohnzulagen_pflegen'))

            zulage.zulage_art = form.zulage_art.data
            zulage.bezeichnung = form.bezeichnung.data
            zulage.zulage_proz = form.zulage_proz.data
            zulage.geaendert_durch = current_user.name
            zulage.geaendert_dat = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.session.commit()
            flash('Lohnzulage updated successfully!', 'success')
        else:
            existing_zulage = Lohnzulagen.query.filter_by(zulage_art=form.zulage_art.data).first()
            if existing_zulage:
                flash('A record with this Zulage Art already exists.', 'danger')
            else:
                zulage = Lohnzulagen(
                    zulage_art=form.zulage_art.data,
                    bezeichnung=form.bezeichnung.data,
                    zulage_proz=form.zulage_proz.data,
                    angelegt_durch=current_user.name,
                    angelegt_dat=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
                db.session.add(zulage)
                db.session.commit()
                flash('Lohnzulage added successfully!', 'success')

        return redirect(url_for('main.lohnzulagen_pflegen'))

    zulagen = Lohnzulagen.query.all()
    return render_template('lohnzulagen_pflegen.html', form=form, zulagen=zulagen, edit_id=edit_id)

@main.route('/delete_zulage/<zulage_id>', methods=['POST'])
@login_required
def delete_zulage(zulage_id):
    zulage = Lohnzulagen.query.get(zulage_id)
    if zulage:
        db.session.delete(zulage)
        db.session.commit()
        flash('Lohnzulage deleted successfully!', 'success')
        return jsonify({'message': 'success'}), 200
    else:
        flash('Lohnzulage not found!', 'danger')
        return jsonify({'message': 'not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)

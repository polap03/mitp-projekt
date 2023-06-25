from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
from flask_login import login_required, current_user
from .models import Ad
from . import db
import json
import pandas as pd
from .models import Participant
from functools import wraps
views = Blueprint('views',__name__)
import smtplib

def user_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)  # Odmowa dostępu
            return view_func(*args, **kwargs)
        return wrapper
    return decorator
@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html", user=current_user)
@views.route('/ogloszenia', methods=['GET', 'POST'])
def add_ad():
    if request.method == 'POST':
        try:
            ad = request.form["ad"]

            if len(ad) < 1:
                flash("Ogłoszenie jest za krótkie!", category='error')
            else:
                new_ad = Ad(data=ad, user_id=current_user.id)
                db.session.add(new_ad)
                db.session.commit()
                flash("Dodano ogłoszenie!", category='success')
        except KeyError:
            flash("Błąd przy dodwaniu ogłoszenia.", category='error')
    ads = Ad.query.all()
    return render_template("ogloszenia.html", user=current_user, ads=ads)

@views.route('/delete-ad', methods=['POST'])
@login_required
@user_required('organizer')
def delete_ad():
    ad = json.loads(request.data)
    adId = ad['adId']
    ad = Ad.query.get(adId)
    if ad:
        db.session.delete(ad)
        db.session.commit()
        flash("Ad deleted!", category='success')
    return jsonify({})
    
def add_participant(request):
    name = request.form.get('name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    shirt_size = request.form.get('shirt_size')
    gender = request.form.get('gender')
    phone = request.form.get('phone')
    birthdate = request.form.get('birthdate')

    new_participant = Participant(
        first_name=name,
        last_name=last_name,
        email=email,
        shirt_size=shirt_size,
        gender=gender,
        phone_number=phone,
        birthdate=birthdate
    )

    db.session.add(new_participant)
    db.session.commit()

    participants = Participant.query.all()


    df = pd.DataFrame(
        [(participant.first_name, participant.last_name, participant.email, participant.shirt_size, participant.gender, participant.phone_number, participant.birthdate)
        for participant in participants],
        columns=['Imię', 'Nazwisko', 'Email', 'Rozmiar koszulki', 'Płeć', 'Nr telefonu', 'Data urodzenia']
    )

    # Zapisywanie DataFrame do pliku Excel
    df.to_excel('uczestnicy.xlsx', index=False)

    flash("Zapisano na bieg!", category='success')
    
@views.route('/zapisy', methods=['GET', 'POST'])
@login_required
def zapisy():
    if request.method == 'POST':
        add_participant(request)
        return redirect(url_for('views.zapisy'))
    
    return render_template("zapisy.html", user=current_user)

@views.route('/lista-biegaczy', methods=['GET', 'POST'])
@login_required
@user_required('organizer')
def lista_biegaczy():
    if request.method == 'POST':
        add_participant(request)
        return redirect(url_for('views.lista_biegaczy'))
    participants = Participant.query.all()
    return render_template("lista_biegaczy.html", participants=participants, user=current_user)

@views.route('/delete-participant', methods=['POST'])
@login_required
@user_required('organizer')
def delete_participant():
    participant = json.loads(request.data)
    participantId = participant['participantId']
    participant = Participant.query.get(participantId)
    if participant:
        db.session.delete(participant)
        db.session.commit()
        participants = Participant.query.all()

        df = pd.DataFrame(
            [(participant.first_name, participant.last_name, participant.email, participant.shirt_size, participant.gender, participant.phone_number, participant.birthdate)
            for participant in participants],
            columns=['Imię', 'Nazwisko', 'Email', 'Rozmiar koszulki', 'Płeć', 'Nr telefonu', 'Data urodzenia']
        )

        df.to_excel('uczestnicy.xlsx', index=False)
        flash("Participant deleted!", category='success')
    return jsonify({})

def send_email(to_addresses, subject, message, sender_email):
    smtp_server = 'poczta.agh.edu.pl'
    smtp_port = 465
    smtp_username = 'moj_enail'
    smtp_password = 'moje_haslo'
    sender_email = current_user.email

    email_message = f'From: {smtp_username}\r\nSubject: {subject}\n\nFrom: {sender_email}\n{message}'

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.helo(smtp_username)
            for email in to_addresses:
                server.sendmail(smtp_username, email, email_message)
                print(smtp_username, email, email_message)
        print("Wiadomości e-mail zostały wysłane.")
    except Exception as e:
        print("Wystąpił błąd podczas wysyłania wiadomości e-mail:", str(e))

@views.route('/wiadomosci', methods=['GET', 'POST'])
@login_required
@user_required('organizer')
def napisz_wiadomosc():

    participants = Participant.query.all()

    if request.method == 'POST':
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if request.form.get('send_to_all'):
            recipient_emails = [participant.email for participant in participants]
        else:
            selected_participants = request.form.getlist('selected_participants')
            recipient_emails = [participant.email for participant in participants if str(participant.id) in selected_participants]
        
        send_email(recipient_emails, subject, message, sender_email=current_user.email)
        
        flash("Wiadomość została wysłana do wszystkich uczestników.", category='success')
        return redirect(url_for('views.napisz_wiadomosc'))

    return render_template("wiadomosci.html", user=current_user, participants=participants)

@views.route('/kontakt', methods=['GET', 'POST'])
@login_required
@user_required('participant')
def contact_organizers():
    if request.method == 'POST':
        send_email(["apaciorek@student.agh.edu.pl"], request.form.get('subject'), request.form.get('message'), sender_email=current_user.email)
        flash('Wiadomość została wysłana', category='success')
    return render_template("kontakt.html", user=current_user)

# from flask import flash, redirect, url_for
# from .models import User, db

# @views.route('/delete-user', methods=['GET', 'POST'])
# def delete_user():
#     user_id = 3
#     user = User.query.get(user_id)
#     if user:
#         db.session.delete(user)
#         db.session.commit()
#         flash("Użytkownik został usunięty z bazy danych.", category='success')
#     return redirect(url_for('views.delete_user'))





# pylint: disable=missing-docstring
from flask import Flask,render_template,request,redirect,url_for,flash,session
import firebase_admin
from firebase_admin import credentials, firestore
#from flask_socketio import SocketIO, emit
from datetime import datetime
# pylint: disable=missing-docstring
import pyrebase

app = Flask(__name__)
app.secret_key = 'b6d7f0398e1f71b9e45f64c2d93c4516'
socketio = SocketIO(app)

config = {
    "apiKey": "AIzaSyCm1NoVNUla-dDZzqaAxHktIG0CAjc6d_k",
    "authDomain": "chat-flask-bd.firebaseapp.com",
    "databaseURL": "https://chat-flask-bd.firebaseio.com",
    "projectId": "chat-flask-bd",
    "storageBucket": "chat-flask-bd.firebasestorage.app",
    "messagingSenderId": "1004736765124",
    "appId": "1:1004736765124:web:2837b483055965047efd91"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
#date et heure
current_time = datetime.utcnow()
#init de la variable qui va recevoir l'id du
# recepteur = 0
# Charger la clé JSON
cred = credentials.Certificate("cle.json")
firebase_admin.initialize_app(cred)

# Initialiser Firestore
db = firestore.client()

@app.route("/home")
def index():

    # print("a")
    # print(session['id'])
    # print("a")

    return render_template("index.html")

@app.route("/deconnexion")
def deconnexion():
    session.clear()
    return render_template("auth-login.html")

@app.route("/inscription", methods=['POST','GET'])
def inscription():
    try:
        if request.method == 'POST':
        #recuperation des infos du formulaire
            nom = request.form.get('nom')
            email = request.form.get('email')
            mdp = request.form.get('mdp')
            #creation du user a partir des infos recupere dans le formulaire dans firebase auth
            utilisateur = auth.create_user_with_email_and_password(email,mdp)
            
            user_id = utilisateur['localId']
            #insertion des infos de l'utilisateur dans firestore
            db.collection("utilisateurs").document(user_id).set({
            "pseudo": nom,
            "email": email,
            "mdp":mdp,
            "date_creation": current_time
            })
            return redirect(url_for('auth-login'))
        else:
            print('!post')
    except Exception as e:  # pylint: disable=broad-exception-caught
        flash(str(e), "danger")
    return render_template("auth-register.html")

@app.route("/",methods=['POST','GET'])
def connexion():
    try:
        if request.method == 'POST':
        #recuperation des infos du formulaire
            email = request.form.get('email')
            mdp = request.form.get('mdp')
            #creation du user a partir des infos recupere dans le formulaire
            infos = auth.sign_in_with_email_and_password(email,mdp)
            session['id'] = infos['localId']# pylint: disable=redefined-outer-name
            flash("login successful. Please log in.", "success")
            return redirect(url_for('index'))
        else:
            print('!post')
    except Exception as e:  # pylint: disable=broad-exception-caught
        flash(str(e), "danger")
    return render_template("auth-login.html")

@app.route("/retrouver_mdp",methods=['POST','GET'])
def retrouver_mdp():
    try:
        if request.method == 'POST':
        #recuperation des infos du formulaire

            email = request.form.get('email')
            #creation du user a partir des infos recupere dans le formulaire
            auth.send_password_reset_email(email)
            return redirect(url_for('auth-login'))
        else:
            print('!post')
    except Exception as e:  # pylint: disable=broad-exception-caught
        flash(str(e), "danger")
    return render_template("auth-recoverpw.html")

#methode pour la recuperation des utlisateurs pour les afficher dans la liste de chat
@app.route("/users", methods=["GET"])
def users():
    users_ref = db.collection("utilisateurs").stream()
    users = []
    for user in users_ref:
        user_data = user.to_dict()
        user_data["id"] = user.id  # Ajoute l'ID Firestore pour les liens
        users.append(user_data)
    return render_template("index.html", users=users)




#affichage des conversations au clique
@app.route("/affiche_chat/<receiver_id>")
def affiche_chat(receiver_id):
    """ Afficher la discussion entre l’utilisateur connecté et celui sélectionné. """
    sender_id = session['id']  # L'utilisateur connecté
    recepteur = receiver_id #stockage de l'id du destinataire
    if not sender_id:
        return redirect(url_for("auth-login"))  # Redirige si non connecté

    # Récupérer les messages entre sender_id et receiver_id
    messages_ref = db.collection("messages").order_by("date_envoi")
    messages = [doc.to_dict() for doc in messages_ref.stream()]

    # Filtrer les messages où l'expéditeur ou le récepteur est sender_id ou receiver_id
    filtered_messages = [
        msg for msg in messages if (msg["expediteur"] in [sender_id, receiver_id] and 
                                    msg["recepteur"] in [sender_id, receiver_id])
    ]
    return render_template("index.html", messages=filtered_messages, receiver_id=receiver_id)


if __name__ == '__main__':
    app.run(debug=True)

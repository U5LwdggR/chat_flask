import firebase_admin
from firebase_admin import credentials, firestore

# Charger la clé JSON
cred = credentials.Certificate("cle-firebase.json")
firebase_admin.initialize_app(cred)

# Initialiser Firestore
db = firestore.client()

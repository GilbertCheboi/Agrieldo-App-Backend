import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate('/home/gilly/Farmers/Backend/agrieldo-bc336-firebase-adminsdk-yn7kr-c9c2246eef.json')
firebase_admin.initialize_app(cred)
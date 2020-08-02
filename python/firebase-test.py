import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Fetch the service account key JSON file contents
cred = credentials.Certificate('/home/vishnoitanuj/Downloads/service-account-file.json')
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://new-agent-twlwex.firebaseio.com/'
})

# ref = db.reference('/')
# ref.set({
#         'slot1': 0,
#         'slot2': 0,
#         })

ref = db.reference('/slots')
# box_ref = ref.child('box001')
ref.update({
    'slot1': 2,
    'slot3': 0
})
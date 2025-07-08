# firebase_helper.py
import firebase_admin
from firebase_admin import credentials, db
import uuid
import datetime

# Initialize Firebase Admin SDK

def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_config.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': "https://resourcesharingapp-6f214-default-rtdb.firebaseio.com"
        })

# Add new resource

def add_resource(title, description, tags, drive_link, uploader_email):
    init_firebase()
    ref = db.reference('/resources')
    resource_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()
    data = {
        'id': resource_id,
        'title': title,
        'description': description,
        'tags': tags,
        'drive_link': drive_link,
        'timestamp': timestamp,
        'uploader_email': uploader_email
    }
    ref.child(resource_id).set(data)

# Get all resources

def get_all_resources():
    init_firebase()
    ref = db.reference('/resources')
    return ref.get() or {}

# Delete a resource

def delete_resource(resource_id):
    init_firebase()
    ref = db.reference(f'/resources/{resource_id}')
    ref.delete()

# Update an existing resource

def update_resource(resource_id, new_data):
    init_firebase()
    ref = db.reference(f'/resources/{resource_id}')
    ref.update(new_data)

#repport a resource
def report_resource(resource_id, reporter_email, reason="No reason provided"):
    init_firebase()
    report_ref = db.reference('/reports')
    report_id = str(uuid.uuid4())
    report_ref.child(report_id).set({
        'report_id': report_id,
        'resource_id': resource_id,
        'reporter_email': reporter_email,
        'reason': reason,
        'timestamp': datetime.datetime.now().isoformat()
    })

# Upvote a resource
def upvote_resource(resource_id, user_email):
    init_firebase()
    ref = db.reference(f'/resources/{resource_id}')
    current = ref.get()

    voters = current.get("voters", {})
    safe_email = user_email.replace('.', ',')  # Firebase-safe key
    if safe_email in voters:
        return False  # already voted

    new_votes = current.get("votes", 0) + 1
    voters[safe_email] = True

    ref.update({
        "votes": new_votes,
        "voters": voters
    })
    return True

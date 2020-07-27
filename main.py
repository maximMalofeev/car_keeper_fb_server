import os
import firebase_admin
import datetime
import time
from firebase_admin import credentials, messaging, firestore

def get_owners(plate):
    db = firestore.client()
    plate_doc_ref = db.collection('plates').document(plate)
    plate_snap = plate_doc_ref.get()
    if plate_snap.exists:
        plate_dict = plate_snap.to_dict()
        return plate_dict['owners']
    else:
        print(f"No such plate({plate})")
        return []

def notify_owners(owners):
    db = firestore.client()
    users_col_ref = db.collection('users')
    for owner in owners:
        user_doc_ref = users_col_ref.document(owner)
        user_snap = user_doc_ref.get()
        if user_snap.exists:
            user_dict = user_snap.to_dict()
            print(f"Send notification to {owner} with name: {user_dict['name']}")
            send_notification(title="Your car in danger", body="Harry up!", token=user_dict["registration_token"])
        else:
            print(f"User {owner} not exists any more")

def send_notification(title, body, token):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title, body=body),
        token=token,
    )
    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)

def on_snapshot(collection_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == "ADDED":
            print(u'{} => {}, change type = {}'.format(change.document.id, change.document.to_dict(), change.type))
            owners = get_owners(change.document.id)
            notify_owners(owners)
            change.document.reference.delete()


if __name__ == "__main__":
    try:
        cred = credentials.Certificate(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
        app = firebase_admin.initialize_app(cred)
        
        print(app.name)
        
        db = firestore.client()
        col_watch = db.collection('in-danger').on_snapshot(on_snapshot)
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exit by user desire")
# app.py
import streamlit as st
import pyrebase
import re
from firebase_helper import add_resource, get_all_resources, delete_resource, update_resource, report_resource, upvote_resource
from dotenv import load_dotenv
import os

load_dotenv()



# -------------------- Firebase Client SDK Config ----------------------
firebaseConfig = {
    "apiKey": os.getenv("API_KEY"),
    "authDomain": os.getenv("AUTH_DOMAIN"),
    "databaseURL": os.getenv("DATABASE_URL"),
    "projectId": os.getenv("PROJECT_ID"),
    "storageBucket": os.getenv("STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("MESSAGING_SENDER_ID"),
    "appId": os.getenv("APP_ID")
}


firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# -------------------- Authentication State ----------------------
if 'user' not in st.session_state:
    st.session_state.user = None

st.title("📚 Real-Time Resource Sharing App")

# -------------------- If Logged In ----------------------
if st.session_state.user:
    user_email = st.session_state.user["email"]
    st.sidebar.success(f"✅ Logged in as {user_email}")

    is_admin = user_email.endswith("@admin.com")

    # Upload Form
    st.sidebar.header("➕ Upload / Update Resource")
    with st.sidebar.form("upload_form"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        tags = st.multiselect("Tags", options=["AI", "ML", "Python", "Web", "Data", "NLP", "Project", "Hackathon"], default=[])
        custom_tag = st.text_input("Custom Tag (optional)")
        if custom_tag:
            tags.append(custom_tag.strip())
        drive_link = st.text_input("Google Drive Link (public)")
        update_id = st.text_input("Resource ID to edit (optional)")
        submitted = st.form_submit_button("Submit")

        if submitted:
            if not title or not description or not drive_link:
                st.error("❌ Title, Description, and Drive Link are required.")
            else:
                if update_id:
                    update_resource(update_id, {
                        "title": title,
                        "description": description,
                        "tags": tags,
                        "drive_link": drive_link
                    })
                    st.success("✅ Resource updated.")
                else:
                    add_resource(title, description, tags, drive_link, user_email)
                    st.success("✅ New resource uploaded.")
                st.rerun()

    if st.sidebar.button("🚪 Logout"):
        st.session_state.user = None
        st.rerun()

# -------------------- Guest Mode ----------------------
elif 'guest' in st.session_state and st.session_state.guest:
    user_email = "guest"
    st.sidebar.success("👤 Using app as Guest")

    st.sidebar.info("Login to enable editing/deleting your uploads.")

    st.sidebar.header("➕ Upload Resource (Guest)")
    with st.sidebar.form("upload_form_guest"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        tags = st.multiselect("Tags", options=["AI", "ML", "Python", "Web", "Data", "NLP", "Project", "Hackathon"], default=[])
        custom_tag = st.text_input("Custom Tag (optional)")
        if custom_tag:
            tags.append(custom_tag.strip())
        drive_link = st.text_input("Google Drive Link (public)")
        submitted = st.form_submit_button("Upload")

        if submitted:
            if not title or not description or not drive_link:
                st.error("❌ Title, Description, and Drive Link are required.")
            else:
                add_resource(title, description, tags, drive_link, user_email)
                st.success("✅ Resource uploaded as Guest.")
                st.rerun()

    if st.sidebar.button("🔙 Return to Login"):
        del st.session_state.guest
        st.rerun()

# -------------------- Login or Sign Up ----------------------
else:
    st.sidebar.subheader("🔐 Login or Sign Up")
    auth_mode = st.sidebar.radio("Select Mode", ["Login", "Sign Up"])
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if auth_mode == "Sign Up":
        if st.sidebar.button("Create Account"):
            try:
                user = auth.create_user_with_email_and_password(email, password)
                auth.send_email_verification(user['idToken'])
                st.success("✅ Verification email sent. Please verify your email before logging in.")
                st.info("📧 Once verified, return to login.")
            except Exception as e:
                st.error(f"❌ Failed to create account: {str(e)}")

    if auth_mode == "Login":
        if st.sidebar.button("Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                user_info = auth.get_account_info(user['idToken'])["users"][0]
                if not user_info.get("emailVerified", False):
                    st.warning("⚠️ Email not verified. Please check your inbox and verify before logging in.")
                else:
                    st.session_state.user = user_info
                    st.success("✅ Logged in successfully.")
                    st.rerun()
            except Exception as e:
                st.error("❌ Invalid credentials. Try again or use Guest Mode.")

    if st.sidebar.button("Continue as Guest"):
        st.session_state.guest = True
        st.rerun()

# -------------------- Resource Search and Display ----------------------
st.subheader("📂 Shared Resources")
resources = get_all_resources()

search_query = st.text_input("🔎 Search by title or tag")

if not resources:
    st.info("No resources available yet.")
else:
    filtered_resources = {
        rid: r for rid, r in resources.items()
        if search_query.lower() in r.get('title', '').lower()
        or any(search_query.lower() in tag.lower() for tag in r.get('tags', []))
    } if search_query else resources

    for resource_id, res in filtered_resources.items():
        with st.container():
            st.markdown(f"### 📄 {res['title']}")
            st.markdown(f"📝 {res['description']}")
            tags = res.get('tags', [])
            if tags:
                st.markdown(f"🏷️ Tags: `{', '.join(tags)}`")
            else:
                st.markdown("🏷️ Tags: `None`")

            drive_link = res.get("drive_link", "")
            st.markdown(f"[📥 Open in Drive]({drive_link})", unsafe_allow_html=True)

            match = re.search(r"/d/([a-zA-Z0-9_-]+)", drive_link)
            if match:
                file_id = match.group(1)
                st.components.v1.iframe(f"https://drive.google.com/file/d/{file_id}/preview", height=300)

            # 👍 Upvote logic
            votes = res.get("votes", 0)
            st.markdown(f"👍 **Upvotes:** {votes}")

            if st.session_state.get("user"):
                safe_email = st.session_state.user["email"].replace('.', ',')
                has_voted = res.get("voters", {}).get(safe_email, False)

                if not has_voted:
                    if st.button("👍 Upvote", key=f"vote_{resource_id}"):
                        if upvote_resource(resource_id, st.session_state.user["email"]):
                            st.success("✅ Upvoted!")
                            st.rerun()
                else:
                    st.info("✅ You already upvoted this.")
            else:
                st.warning("🔐 Login to upvote this resource.")

            # Edit/Delete options for owner or admin
            if (st.session_state.get("user") and (res['uploader_email'] == st.session_state.user['email'] or is_admin)):
                st.markdown(f"🧾 Resource ID: `{resource_id}`")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Edit", key=f"edit_{resource_id}"):
                        st.warning("To edit, paste Resource ID in sidebar")
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{resource_id}"):
                        delete_resource(resource_id)
                        st.success("✅ Resource deleted.")
                        st.rerun()

            # Report logic
            if st.session_state.get("user"):
                with st.expander("⚠️ Report Resource"):
                    reason = st.text_input("Reason", key=f"reason_{resource_id}")
                    if st.button("🚩 Report", key=f"report_{resource_id}"):
                        reporter = st.session_state.user['email']
                        report_resource(resource_id, reporter, reason)
                        st.success("✅ Report submitted.")
            else:
                st.warning("🔒 Login to report this resource.")

            st.markdown("---")

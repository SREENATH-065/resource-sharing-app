# resource-sharing-app
Resource sharing app for educational or entertainment purposes

# 📚 Real-Time Resource Sharing App

A secure and real-time platform where users can **upload**, **browse**, **search**, and **interact with study resources**. Built using **Streamlit** and **Firebase**, it supports **authentication**, **role-based access**, **Google Drive previews**, **upvoting**, and **reporting** — making it ideal for student collaboration and content management.

---

## 🚀 Features

- 🔐 **User Login & Signup** with Firebase Authentication  
- 👤 **Guest Mode** with limited upload access  
- 📤 Upload resources with title, description, tags, and Drive link  
- 🔎 **Search and filter** resources by title or tags  
- 🧾 **Edit/Delete access** only for uploader or admin  
- 👍 **Upvote system** (one vote per user, tracked in Firebase)  
- ⚠️ **Report feature** (for logged-in users only)  
- 📄 **Google Drive preview** for uploaded resources  

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit  
- **Backend**: Firebase Realtime Database  
- **Authentication**: Firebase Auth (email/password)  
- **Storage**: Google Drive (via public links)  
- **Others**: Pyrebase, dotenv, Python, UUID, Regex  

---

## 🧪 How to Run Locally

1. **Clone the repository**

```bash
git clone https://github.com/your-username/resource-sharing-app.git
cd resource-sharing-app
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Create a `.env` file** and add your Firebase credentials:

```env
API_KEY=your_api_key
AUTH_DOMAIN=your_project.firebaseapp.com
DATABASE_URL=https://your_project.firebaseio.com
PROJECT_ID=your_project
STORAGE_BUCKET=your_project.appspot.com
MESSAGING_SENDER_ID=xxxxxx
APP_ID=xxxxxx
```

4. **Run the Streamlit app**

```bash
streamlit run app.py
```

---

## 📸 Preview

https://resource-sharing-app.streamlit.app

## 📄 License

This project is licensed under the **MIT License**.


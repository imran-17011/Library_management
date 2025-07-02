import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# File and image directory setup
data_file = "library_members.csv"
photo_dir = "photos"
os.makedirs(photo_dir, exist_ok=True)

# Load or initialize data
def load_data():
    if os.path.exists(data_file):
        return pd.read_csv(data_file)
    else:
        df = pd.DataFrame(columns=["Name", "Phone", "CNIC", "Address", "Photo", "Fee Paid", "Last Updated"])
        df.to_csv(data_file, index=False)
        return df

def save_data(df):
    df.to_csv(data_file, index=False)

# Member registration page
def register_member():
    st.title("📝 Register New Library Member")
    name = st.text_input("Full Name")
    phone = st.text_input("Phone Number")
    cnic = st.text_input("CNIC")
    address = st.text_area("Address")
    photo = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"])
    fee_paid = st.selectbox("Fee Paid?", ["Yes", "No"])

    if st.button("Register"):
        if name and phone and cnic:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            photo_path = ""
            if photo:
                photo_path = os.path.join(photo_dir, f"{name}_{timestamp}.jpg")
                with open(photo_path, "wb") as f:
                    f.write(photo.read())

            new_row = pd.DataFrame({
                "Name": [name],
                "Phone": [phone],
                "CNIC": [cnic],
                "Address": [address],
                "Photo": [photo_path],
                "Fee Paid": [fee_paid],
                "Last Updated": [datetime.now().strftime("%Y-%m-%d")]
            })
            df = load_data()
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success("✅ Member registered successfully!")
        else:
            st.error("Please fill in all required fields.")

# Dashboard page
def view_dashboard():
    st.title("📊 Admin Dashboard")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        password = st.text_input("Enter Admin Password", type="password")
        if password == "admin123":
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
        else:
            st.warning("Invalid password. Access denied.")
            return

    df = load_data()
    if df.empty:
        st.info("No members registered yet.")
        return

    st.markdown("### 📋 Member List")
    for idx, row in df.iterrows():
        st.markdown("---")
        cols = st.columns([1, 2, 2, 2, 1, 1])
        with cols[0]:
            if row["Photo"] and os.path.exists(row["Photo"]):
                st.image(Image.open(row["Photo"]), width=80)
            else:
                st.markdown("🖼️ No Photo")

        with cols[1]:
            st.markdown(f"**Name:** {row['Name']}")
            st.markdown(f"**Phone:** {row['Phone']}")

        with cols[2]:
            st.markdown(f"**CNIC:** {row['CNIC']}")
            st.markdown(f"**Address:** {row['Address']}")

        with cols[3]:
            status_color = "✅" if row["Fee Paid"] == "Yes" else "❌"
            st.markdown(f"**Fee Paid:** {status_color} {row['Fee Paid']}")

        with cols[4]:
            if st.button("Mark as Paid", key=f"paid_{idx}"):
                df.at[idx, "Fee Paid"] = "Yes"
                df.at[idx, "Last Updated"] = datetime.now().strftime("%Y-%m-%d")
                save_data(df)
                st.experimental_rerun()

    st.download_button("⬇️ Download Full Report", data=df.to_csv(index=False), file_name="library_members.csv")

# App navigation
st.sidebar.title("📚 Library System")
page = st.sidebar.radio("Select Page", ["Register Member", "Admin Dashboard"])

if page == "Register Member":
    register_member()
elif page == "Admin Dashboard":
    view_dashboard()

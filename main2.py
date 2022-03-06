# Modules**
import pyrebase
import streamlit as st

# Configuration Key
firebaseConfig = {
    'apiKey': "AIzaSyCh87v4lJmX7cas4Plf2J_yqGme4FAjkfg",
    'authDomain': "abcd-98110.firebaseapp.com",
    'projectId': "abcd-98110",
    'databaseURL': "https://abcd-98110-default-rtdb.firebaseio.com/",
    'storageBucket': "abcd-98110.appspot.com",
    'messagingSenderId': "188766950521",
    'appId': "1:188766950521:web:849fa44170be2c5ded70a8",
    'measurementId': "G-Q6GHJ03N5Y"
}


# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Database**
db = firebase.database()
storage = firebase.storage()
st.sidebar.title("Our community app")

# Authentication**
choice = st.sidebar.selectbox('login/Signup', ['Login', 'Sign up'])

# Obtain User Input for email and password
email = st.sidebar.text_input('Please enter your email address')
password = st.sidebar.text_input('Please enter your password',type = 'password')

# App** 

# Sign up Block
if choice == 'Sign up':
    handle = st.sidebar.text_input(
        'Please input your app handle name', value='Default')
    submit = st.sidebar.button('Create my account')

    if submit:
        user = auth.create_user_with_email_and_password(email, password)
        st.success('Your account is created suceesfully!')
        st.balloons()
        # Sign in
        user = auth.sign_in_with_email_and_password(email, password)
        db.child(user['localId']).child("Handle").set(handle)
        db.child(user['localId']).child("ID").set(user['localId'])
        st.title('Welcome' + handle)
        st.info('Login via login drop down selection')

# Login Block**
if choice == 'Login':
    login = st.sidebar.checkbox('Login')
    if login:
        user = auth.sign_in_with_email_and_password(email,password)
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
# import os
# import json
# from web3 import Web3
# from pathlib import Path
# from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import sqlite3 

#conn=sqlite3.connect("data.db")
#c=conn.cursor()


def create_table(c):
    c.execute("CREATE TABLE IF NOT EXISTS usertable(usertype TEXT, username TEXT, password TEXT, licence TEXT)")

def add_data(conn, usertype, username, password,licence):
    c = conn.cursor()
    c.execute("INSERT INTO usertable(usertype, username, password,licence) VALUES (?, ?, ?,?)",(usertype, username, password,licence))
    conn.commit()

def login_user(c, usertype,username,password,licence):
    if usertype == "Notary":
        c.execute("SELECT * FROM usertable WHERE usertype=? AND password=? AND licence=?",(usertype, password, licence))
    else:
        c.execute("SELECT * FROM usertable WHERE usertype=? AND username=? AND password=?",(usertype, username, password))
    data=c.fetchall()
    return data

def check_user(conn, username):
    st.write("check_user():", username)
    st.session_state.userChecked = True
    c = conn.cursor()
    create_table(c)
    c.execute("SELECT * FROM usertable WHERE username=?",(username,))
    data=c.fetchall()
    return data

def check_license(conn, identifier):
    st.write("check_licence():", identifier)
    st.session_state.userChecked = True
    c = conn.cursor()
    create_table(c)
    c.execute("SELECT * FROM usertable WHERE licence=?",(identifier,))
    data=c.fetchall()
    return data

# Will remove after checking how it works
def view_all_users(c):
    c.execute("SELECT * FROM usertable")    
    data=c.fetchall()
    return data          


### Main Login/SignUp
#def main():
#    ## Sign up/Sign in
#    st.title("Smart Document")
#    menu=["Home","Sign Up","Sign In"]
#    st.session_state.userTypes = ["User", "Notary", "Company"]
#    choice=st.sidebar.selectbox("Menu",menu)
#    
#    if choice=="Home":
#        st.subheader("Home")
#        if st.sidebar.checkbox("See all users"):
#            users=view_all_users()
#            df=pd.DataFrame(users)
#            st.dataframe(df)
#    elif choice=="Sign Up":
#        sign_up()
#
#    elif choice=="Sign In":
#        sign_in()
        
def sign_up(conn, new_usertype): 
    c=conn.cursor()
    st.subheader("Please create a new account to be able use our services")
    if new_usertype=="Notary":
        new_licence=st.text_input("Licence number")
    else:
        new_username=st.text_input("User Name")

    new_password=st.text_input("Password",type="password")
    if st.button("SignUp"):
        create_table(c)
        if new_usertype=="Notary":
            add_data(conn, new_usertype, "", new_password, new_licence)
        else:
            add_data(conn, new_usertype, new_username, new_password,"")

        st.success("You have successfully created an account")
        st.info("Go to Main Menu to Login")

    # should return success or fail?

def sign_in(conn, usertype):
    c=conn.cursor()
    st.subheader("Please sign in to use the Smart Contract services")
    #usertype=st.sidebar.selectbox("Who are you?", userType)
    if usertype=="Notary":
        licence=st.text_input("Enter your Notary licence:")
    else:
        username=st.text_input("User Name")

    password=st.text_input("Password",type="password")

    if st.checkbox("Login"):
        create_table(c)
        if usertype=="Notary":
            result=login_user(c, usertype, "", password, licence)
            identifier = licence
        else:
            result=login_user(c, usertype, username, password,"")
            identifier = username
        if result:
            st.success("{} is logged in as a verified {}".format(identifier, usertype))
        else:
            if usertype=="Notary":
                data = check_license(conn, licence)
            else:
                data = check_user(conn, username)
            if data:
                st.warning("Incorrect Password, try again.")
            else:
                st.warning("User Name does not exist. Please Sign Up")

#        st.sidebar.write("login result:", result)
        return result
    
#main()


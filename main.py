# import os
# import json
# from web3 import Web3
# from pathlib import Path
# from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import sqlite3 

conn=sqlite3.connect("data.db")
c=conn.cursor()



def create_table():
    c.execute("CREATE TABLE IF NOT EXISTS usertable(usertype TEXT, username TEXT, password TEXT, licence TEXT)")

def add_data(usertype, username, password,licence):
    c.execute("INSERT INTO usertable(usertype, username, password,licence) VALUES (?, ?, ?,?)",(usertype, username, password,licence))
    conn.commit()

def login_user(usertype,username,password,licence):
    c.execute("SELECT * FROM usertable WHERE usertype=? AND username=? AND password=?",(usertype, username, password))
    data=c.fetchall()
    return data

# Will remove after checking how it works
def view_all_users():
    c.execute("SELECT * FROM usertable")    
    data=c.fetchall()
    return data          


### Main Login/SignUp
def main():
    ## Sign up/Sign in
    st.title("Smart Document")
    menu=["Home","Sign Up","Sign In"]
    usertypes=["User", "Notary", "Company"]
    choice=st.sidebar.selectbox("Menu",menu)
    
    if choice=="Home":
        st.subheader("Home")
        if st.sidebar.checkbox("See all users"):
            users=view_all_users()
            df=pd.DataFrame(users)
            st.dataframe(df)
        
    elif choice=="Sign Up":
        st.subheader("Please create a new account to be able use our services")
        new_usertype=st.sidebar.selectbox("Who are you?",usertypes)
        new_username=st.sidebar.text_input("User Name")
        new_password=st.sidebar.text_input("",type="password")
        if new_usertype=="Notary":
            new_licence=st.sidebar.text_input("Licence number")
        if st.sidebar.button("SignUp"):
            create_table()
            if new_usertype=="Notary":
                add_data(new_usertype, new_username, new_password,new_licence)
            else:
                add_data(new_usertype, new_username, new_password,"")
            st.success("You have successfully created an account")
            st.info("Go to Main Menu to Login")

            
    
    elif choice=="Sign In":
        st.subheader("Please sign in to use the Smart Conrtract services")
        usertype=st.sidebar.selectbox("Who are you?",usertypes)
        username=st.sidebar.text_input("User Name")
        password=st.sidebar.text_input("",type="password")
        if usertype=="Notary":
            licence=st.sidebar.text_input("Enter your licence if you are a Notary")
        if st.sidebar.checkbox("Login"):
            create_table()
            if usertype=="Notary":
                result=login_user(usertype, username, password, licence)
            else:
                result=login_user(usertype, username, password,"")
            if result:
                st.success("{} is logged in as a verified {}".format(username, usertype))
            else:
                st.warning("Incorrect Password or User Name")
    
main()


import streamlit as st
import sqlite3
conn =sqlite3.connect('data.db',check_same_thread=False)
cur = conn.cursor()

# # st.set_page_config(page_title='My webpage', page_icon=":tada",layout="wide")
# #
# #
# # st.subheader("Hi, I am Pravallika :wave:")
# # st.title("A Data scientist From USA")
# # st.write(
# #         "I am passionate about learning new things."
# #     )
#
#
# def form():
#     st.write("This is a colleage admission form")
#     with st.form(key='Information form'):
#         name =st.text_input("Enter your name:")
#         age=  st.text_input("Enter your age")
#         clg_name=st.text_input("Enter your college name:")
#         date= st.date_input("Enter the date: ")
#         submission= st.form_submit_button(label="submit")
#         if submission==True:
#             addData(name,age,clg_name,date)
#
#
# def addData(a,b,c,d):
#     cur.execute("CREATE TABLE IF NOT EXISTS clg_form(NAME TEXT(50), AGE TEXT(50), CLGNAME TEXT(60),DATE TEXT(50));""")
#     cur.execute("INSERT INTO clg_form VALUES (?,?,?,?)",(a,b,c,d))
#     conn.commit()
#     conn.close()
#     st.success( "successfully submitted" )
# form()
#
for row in cur.execute(''' select * from clg_form'''):
    print(row);
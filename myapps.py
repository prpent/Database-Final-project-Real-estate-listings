# date:6/16/2022
import streamlit as st
import pandas as pd
from PIL import Image
import mysql.connector
db_conn = mysql.connector.connect( **st.secrets["mysql"] )
cur = db_conn.cursor()

import hashlib
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def run_query ( query ) :
    with db_conn.cursor() as cur :
        cur.execute( query )
        return cur.fetchall()


def main () :
    menu = ["Home" , "Search Listings" ,"Login","SignUp" ]
    choice = st.sidebar.selectbox( "Menu" , menu )



    if choice == "Home" :
        st.title( "Realtor CRUD Webapp" )
        image = Image.open( 'listing.jpeg' )
        st.image( image , caption='** Buy a Listing** ' )
        st.subheader( "About Application:" )
        st.write(
            "The objective of our project is to create a web app for US Real Estate listings. The users would be welcomed by a page listing the top/latest listing and would have the capability like" )
        st.write( "1.Search listing by filters like zip code, price range, etc." )
        st.write( "2.Add a new listing" )
        st.write( "3.Edit/Remove an existing Listing" )
        st.write( "4.Research relevant statistics about the real estate market." )

    elif choice == "Login":
        # st.subheader("Login Section")

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password",type='password')
        if st.sidebar.checkbox( "Login" ) :
            hashed_pswd = make_hashes( password )
            result =run_query('SELECT * FROM userstable WHERE username ="{}" and password="{}"'. format(username,check_hashes( password , hashed_pswd )))
            if result:
                st.sidebar.success( " Logged as {} to Manage Listings".format( username ) )
            # else:
            #     st.sidebar .warning ( "Incorrect username/password" )
                choice = st.sidebar.selectbox( "Manage Lisitings" ,
                                     ["Please Select One","Add Listings" , "Update/Delete Listings" , "Statistical plots " ] )

                if choice == "Update/Delete Listings":

                    st.subheader( "Update/Delete Listings" )
                    listing_id = run_query( "select listing_id,status_id,Price,acre_lot,house_size from listing" )
                    unique_list = [i[0] for i in listing_id]
                    update_by_listing_id = st.selectbox( "Select Listing ID to update" , unique_list )
                    resultset = run_query('select listing.listing_id,listing_status.status_name,listing.Price, city.city,city.state,city.zip_code,property_type.Property_type_name,feature.bed,feature.bath,listing.acre_lot,listing.house_size,listing.full_address,listing.street from listing inner join listing_status on listing_status.ID=listing.status_id inner join city on city.id=listing.city_id inner  join property_type on property_type.ID=listing.property_type_id inner join feature on feature.id=listing.feature_id where listing_id ="{}"'.format(update_by_listing_id ) )
                    task_status = resultset[0][1]
                    task_price = resultset[0][2]
                    with st.expander( "View Listing Current Information" ) :
                        task_Beds = resultset[0][7]
                        task_Bath = resultset[0][8]
                        task_housesize = resultset[0][10]
                        task_acrelot = resultset[0][9]
                        task_fulladdress = resultset[0][11]
                        task_street = resultset[0][12]
                        task_city = resultset[0][3]
                        task_state = resultset[0][4]
                        task_zipcode = resultset[0][5]
                        task_property = resultset[0][6]
                        clean_db = pd.DataFrame( resultset ,
                                                 columns=["Listing_ID" , "Listing_Status" , "Listing_Price" ,
                                                          "Listing_city" , "Listing_state" , "Listing_zipcode" ,
                                                          "Listing_type" , "listing_bed" , "listing_bath" ,
                                                          "Listing_Acrelot" , "Listing_house_size" ,
                                                          "Listing_full_address" , "Listing_street"] )
                        st.dataframe( clean_db )
                        listing_id = run_query( "select listing_id from listing" )
                    option = st.selectbox( "Please Select form" , ('Choose an Option','Delete Listing','Change Status' , 'Change Features' , 'Change Property_type' , 'Change Price', 'Change Address' ) )
                    if option == 'Change Price' :
                        Listing_newPrice = st.number_input( 'Enter the new Price' )
                        if st.button( "Update Task" ) :
                            run_query( 'update listing set price ="{}", Update_date=now() WHERE listing_id ="{}"'.format( Listing_newPrice , update_by_listing_id ) )
                            db_conn.commit()
                            st.success( "Record is updated" )
                    elif option == 'Change Status' :
                        pro = clean_db.Listing_Status.tolist()
                        avvl = run_query( 'select status_name from listing_status where status_name != "{}"'.format(task_status) )
                        df = pd.DataFrame( avvl , columns=[ 'protype'] )
                        pro2 = df.protype.tolist()
                        # Listing_type = st.text_input( 'Please Update Listing Type To Land,Single/Multi,Condo,Town' ,
                        #                               task_property )
                        Listing_newstatus = st.selectbox( "Listing status*" ,pro+pro2)
                        if st.button( "Update Task" ) :
                            run_query(
                                'UPDATE listing SET status_id = (select id from listing_status where status_name = "{}"), Update_date=now() where listing_id ="{}"'.format(
                                    Listing_newstatus , update_by_listing_id ) )
                            db_conn.commit()
                            st.success( "Record is updated" )

                    elif option == 'Change Features' :
                        col1 , col2 = st.columns( 2 )
                        with col1 :
                            # Listing_newBeds = st.number_input( 'Beds' , task_Beds )
                            pro = clean_db.listing_bed.tolist()
                            avvl = run_query( 'select distinct bed from feature where bed != "{}"'.format(
                                task_Beds ) )
                            df = pd.DataFrame( avvl , columns=['Bedtype'] )
                            pro3 = df.Bedtype.tolist()
                            Listing_newBeds = st.selectbox( "Bed_type" , pro + pro3 )

                        with col2 :
                            # Listing_newBaths = st.number_input( 'Baths' , task_Bath , step=0.5 , format="%.1f" )
                            pro = clean_db.listing_bath.tolist()
                            avvl = run_query( 'select distinct bath from feature where bath != "{}"'.format(
                                task_Bath ) )
                            df = pd.DataFrame( avvl , columns=['Bathtype'] )
                            pro3 = df.Bathtype.tolist()
                            Listing_newBaths = st.selectbox( "Bath_type" , pro + pro3)

                        col3 , col4 = st.columns( 2 )
                        with col3 :
                            Listing_acrelot = st.number_input( 'Acre Lot' , task_acrelot )
                        with col4 :
                            Listing_newhousesize = st.number_input( 'House_Size' , task_housesize )

                        result2 = run_query(
                            'select * from feature where bed= "{}" and bath="{}"'.format(
                                Listing_newBeds , Listing_newBaths ) )
                        if result2 :
                            st.success( "Please proceed with updates" )
                            if st.button( "Update Task" ) :
                                run_query(
                                    'UPDATE listing SET feature_id = ( select id from feature where bed = "{}" and bath = "{}"), Update_date=now(),acre_lot = "{}",house_size="{}" where listing_id ="{}"'.format(
                                        Listing_newBeds , Listing_newBaths , Listing_acrelot , Listing_newhousesize ,
                                        update_by_listing_id ) )
                                db_conn.commit()
                                st.success( "Record is updated" )
                        else :
                            st.warning( "This combination doesn't exist, Please verify below in lookup" )
                            resultset3= run_query(" select bed,bath from feature ")
                            with st.expander("Look up fo Bed and Bath combination"):
                                clean_db = pd.DataFrame( resultset3 ,
                                                         columns=["Listing_beds" , "Listing_baths"] )
                                st.dataframe(clean_db)

                    elif option == 'Change Property_type' :
                        pro = clean_db.Listing_type.tolist()
                        avvl = run_query( 'select property_type_name from property_type where property_type_name!= "{}"'.format(task_property) )
                        df = pd.DataFrame( avvl , columns=['protype'] )
                        pro2 = df.protype.tolist()
                        Listing_type = st.selectbox( 'Please Update Listing Type To Land,Single/Multi,Condo,Town' ,
                                                     pro+pro2 )
                        # Listing_type = st.selectbox( "Listing Type*" ,pro+pro2)
                        if st.button( "Update Task" ) :
                            run_query(
                                'UPDATE listing SET property_type_id = ( select id from property_type where property_type_name = "{}") where listing_id ="{}"'.format(
                                    Listing_type , update_by_listing_id ) )
                            db_conn.commit()
                            st.success( "Record is updated" )

                    elif option == 'Change Address' :
                        # Listing_Fulladdress = st.text_area( "Full Address" , task_fulladdress , max_chars=(300) )
                        Listing_Street = st.text_input( "Enter the Street" , task_street , max_chars=(300) )
                        col1 , col2 , col3 = st.columns( [4 , 3 , 2] )

                        with col1 :
                            pro = clean_db.Listing_state.tolist()
                            avvl = run_query( 'select distinct state from city where state != "{}"'.format(
                                task_state ) )
                            df = pd.DataFrame( avvl , columns=['statype'] )
                            pro2 = df.statype.tolist()
                            Listing_State = st.selectbox( "State" , pro + pro2 )

                        with col2 :
                            pro = clean_db.Listing_city.tolist()
                            avvl = run_query( 'select distinct city from city where city != "{}"'.format(
                                task_city ) )
                            df = pd.DataFrame( avvl , columns=['citype'] )
                            pro2 = df.citype.tolist()
                            Listing_uCity = st.selectbox( "City" , pro + pro2 )

                        with col3 :
                            pro = clean_db.Listing_zipcode.tolist()
                            avvl = run_query( 'select distinct zip_code from city where zip_code != "{}"'.format(
                                task_zipcode ) )
                            df = pd.DataFrame( avvl , columns=['ziptype'] )
                            pro3 = df.ziptype.tolist()
                            Listing_uZipcode = st.selectbox( "Zipcode" , pro + pro3 )
                        result2=run_query('select * from city where city= "{}" and state="{}" and zip_code="{}"'.format(Listing_uCity,Listing_State,Listing_uZipcode))
                        if result2 :
                            st.success( "Please proceed with updates" )
                            if st.button( "Update Task" ) :
                                run_query(
                                    'update listing  set Update_Date=now(),  street = "{}",  city_id = (select id from city where city= "{}" and state = "{}" and zip_code ="{}") where listing_id = "{}"'.format(
                                        Listing_Street , Listing_uCity , Listing_State ,
                                        Listing_uZipcode , update_by_listing_id ) )
                                db_conn.commit()
                                run_query('update listing l inner join city c on l.city_id=c.id set l.full_address=(select concat(lower(l.street) ,",",lower(c.city),",",lower(c.state),",",c.zip_code)) where l.listing_id="{}"'.format(update_by_listing_id))
                                st.success( "Record is updated" )
                                db_conn.commit()
                        else:
                            st.warning( "Incorrect combination, please enter correct values" )
                            with st.expander( "Pease verify  below look up for city,state and zipcode" ) :
                                resultset3=run_query("select state,city,zip_code from city")
                                clean_db = pd.DataFrame( resultset3 ,columns=["State_name" ,"City_name","Zip_code"] )
                                st.dataframe( clean_db )

                    elif option == 'Delete Listing' :
                        listing_id = run_query( "select listing_id,status_id,Price,acre_lot,house_size from listing" )
                        run_query('SET FOREIGN_KEY_CHECKS=0')
                        unique_list = [i[0] for i in listing_id]
                        if st.button( "Delete" ) :
                            run_query( 'delete from listing where listing_id ="{}"'.format( update_by_listing_id ) )
                            run_query( 'commit' )
                            st.warning( "Deleted: '{}'".format( update_by_listing_id ) )


                    with st.expander( "View Updated Data" ) :
                        resultset = resultset = run_query('select listing.listing_id,listing_status.status_name,listing.Price, city.city,city.state,city.zip_code,property_type.Property_type_name,feature.bed,feature.bath,listing.acre_lot,listing.house_size,listing.full_address,listing.street from listing inner join listing_status on listing_status.ID=listing.status_id inner join city on city.id=listing.city_id inner  join property_type on property_type.ID=listing.property_type_id inner join feature on feature.id=listing.feature_id where listing_id ="{}"'.format(update_by_listing_id ) )
                        clean_db1 = pd.DataFrame( resultset ,
                                                  columns=["Listing_ID" , "Listing_Status" , "Listing_Price" ,
                                                           "Listing_city" , "Listing_state" , "Listing_zipcode" ,
                                                           "Listing_type" , "listing_bed" , "Listing_bath" ,
                                                           "Listing_Acrelot" , "Listing_house_size" ,
                                                           "Listing_full_address" , "Listing_street"] )
                        st.dataframe( clean_db1 )
            else:
                st.sidebar.warning("incorrect usernmae/password")

    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password",type='password')

        if st.button("Signup"):
            sql="INSERT INTO userstable(username,password) VALUES (%s,%s)"
            val= (new_user , make_hashes(new_password))
            cur.execute(sql,val)
            cur.execute('commit')
            # add_userdata(new_user,make_hashes(new_password))
            st.success("You have successfully created a valid Account")
            st.info("Go to Login Menu to login")

if __name__ == '__main__':
    main()
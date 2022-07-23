# __author:Owner
# date:6/16/2022
import streamlit as st
import pandas as pd
from PIL import Image
import mysql.connector
import matplotlib.pyplot as plt

db_conn = mysql.connector.connect(**st.secrets["mysql"])
cur = db_conn.cursor()


def run_query(query):
    cur.execute(query)
    return cur.fetchall()

import hashlib
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

## GET MASTER VALUES
listing_type_query = 'select distinct property_type_name from property_type;'
listing_types = pd.DataFrame(run_query(listing_type_query),columns=('listing_type',))
search_types = [''] + listing_types['listing_type'].to_list()
    
listing_status_query = 'select distinct status_name from listing_status;'
listing_statuses = pd.DataFrame(run_query(listing_status_query),columns=('listing_status',))
search_statuses = [''] + listing_statuses['listing_status'].to_list()    

cities_query = 'select distinct city from city;'
cities = pd.DataFrame(run_query(cities_query),columns=('city',))
search_cities = [''] + cities['city'].to_list()
    
states_query = 'select distinct state from city;'
states = pd.DataFrame(run_query(states_query),columns=('state',))
search_states = [''] + states['state'].to_list()

zip_query = 'select distinct zip_code from city;'
zips = pd.DataFrame(run_query(zip_query), columns=('zip',))

bed_query = 'select distinct bed from feature;'
beds = pd.DataFrame(run_query(bed_query), columns=('bed',))

bath_query = 'select distinct bath from feature'
baths = pd.DataFrame(run_query(bath_query), columns=('bath',))


#added new Sahil
zip_query = 'select distinct lpad(zip_code,5,0) from city;'
zip_data = pd.DataFrame(run_query(zip_query))
#added new Sahil
listing_status_query_insert = "select distinct status_name from listing_status where upper(status_name) in ('FOR_SALE','READY_TO_BUILD');"
listing_statuses_insert = pd.DataFrame(run_query(listing_status_query_insert))


def home_page_module():
    st.title("Realtor Listing Webapp")
    image = Image.open( 'listing.jpeg' )
    st.image( image , caption='** Buy a Listing** ' )
    st.subheader("About Application:")
    st.write("The objective of our project is to create a web app for US Real Estate listings. The users would be welcomed by a page listing the top/latest listing and would have the capability like")
    st.write("1.Search listing by filters like zip code, price range, etc.")
    st.write("2.Add a new listing")
    st.write("3.Edit/Remove an existing Listing")
    st.write("4.Research relevant statistics about the real estate market.")


def search_module(search_query_str):
    with st.sidebar.form(key='search_form'):
        listingId = st.number_input('Listing Id',min_value=0)
        priceRange = st.slider("Price Range",value=[0,400000],step=50000)
        col1,col2 = st.columns(2)
        with col1:
            status = st.selectbox("Listing Status",search_statuses )
            bed = st.number_input('Beds',min_value=0)
            city = st.selectbox('City',search_cities)
        with col2:
            pType = st.selectbox("Property Type",search_types )
            bath = st.number_input('Baths',min_value=0.0,step=0.5)
            state = st.selectbox('State',search_states)
            
        search = st.form_submit_button('SEARCH')
        
    if search:
        if listingId > 0:
            search_query_str += ' where l.listing_id = ' + str(listingId)
        else:
            search_query_str += ' where l.listing_id is not null '
            
        if priceRange[0] > 0 or priceRange[1] < 400000:
            search_query_str += ' and price between ' + str(priceRange[0]) + ' and ' + str(priceRange[1])
        
        if len(status) > 0:
            search_query_str += " and ls.status_name = '" + status + "'"
        
        if len(pType) > 0:
            search_query_str += " and lt.property_type_name = '" + pType + "'"
        
        if bed > 0:
            search_query_str += ' and coalesce(f.bed,0) = ' + str(bed)
        
        if bath > 0:
            search_query_str += ' and coalesce(f.bath,0) = ' + str(bath)
        
        if len(city) > 0:
            search_query_str += " and c.city = '" + city + "'"
        
        if len(state) > 0:
            search_query_str += " and c.state = '" + state + "'"
        
        search_query_str += ';'
        
        #debug 
        #st.write(search_query_str)                
    else:
        search_query_str += ' order by listing_date desc limit 30 ;'
    
    return search_query_str


def add_listing_form():
    
 
    with st.form(key='add_form'):
        Listing_type= st.selectbox("Listing Type*", listing_types )
        Listing_Status = st.radio( "Select Listing status" , listing_statuses_insert  )
        Listing_Price = st.number_input('Price')
        col1,col2 = st.columns(2)
        with col1:
            Listing_Beds = st.number_input('Beds',min_value=0)
            Listing_Acrelot = st.number_input('Acre Lot')
        with col2:
            Listing_Baths = st.number_input('Baths',min_value=0.0,step=0.5)
            Lisitng_Housesize = st.number_input('House Size',min_value=0)
    
        #Listing_Fulladdress = st.text_area("Full Address", max_chars=(300))
        Listing_Street = st.text_input( "Enter the Street", max_chars=(300) )
        c_city, c_state, c_zp = st.columns([4,3,2])
        with c_city:
            Listing_City = st.selectbox("City", cities)
        with c_state:
            Listing_State = st.selectbox("State", states)
        # Updated  
        with c_zp:
            Listing_Zipcode = st.selectbox("Zipcode", zip_data)
        
        save = st.form_submit_button('SAVE')
        
    if save:        
        args = [Listing_type, Listing_Status , Listing_Price , Listing_Beds , Listing_Baths , Listing_Acrelot,
                 Listing_Street , Listing_City , Listing_State , Listing_Zipcode , Lisitng_Housesize]
        cur.callproc('insert_listing_proc',args)
        # Added new section -- Sahil
        proc_msg_query = "select * from status;"
        proc_msg = pd.DataFrame(run_query(proc_msg_query))

        if proc_msg[0][0][:5] == "Error":
            
            st.warning(proc_msg[0][0])
                #saved = add_listing_form()
        else:
            
            st.success(proc_msg[0][0])
        

def update_delete_module(update_by_listing_id):
    with st.expander( "View Listing Current Information" ) :
        resultset = run_query('select listing.listing_id,listing_status.status_name,listing.Price, city.city,city.state,city.zip_code,property_type.Property_type_name,feature.bed,feature.bath,listing.acre_lot,listing.house_size,listing.full_address,listing.street from listing inner join listing_status on listing_status.ID=listing.status_id inner join city on city.id=listing.city_id inner  join property_type on property_type.ID=listing.property_type_id inner join feature on feature.id=listing.feature_id where listing_id ="{}"'.format(update_by_listing_id ))
        task_status=resultset[0][1]
        task_price=resultset[0][2]
        task_Beds=resultset[0][7]
        task_Bath=resultset[0][8]
        task_housesize=resultset[0][10]
        task_acrelot=resultset[0][9]
        task_fulladdress=resultset[0][11]
        task_street=resultset[0][12]
        task_city=resultset[0][3]
        task_zipcode=resultset[0][5]
        task_state = resultset[0][4]
        task_property = resultset[0][6]
        clean_db = pd.DataFrame( resultset ,columns=["Listing_ID" , "Listing_Status" , "Listing_Price" , "Listing_city","Listing_state","Listing_zipcode","Listing_type","listing_bed","listing_bath","Listing_Acrelot" ,"Listing_house_size" , "Listing_full_address" , "Listing_street"] )
        st.dataframe( clean_db )
        listing_id = run_query( "select listing_id from listing" )
    option = st.selectbox( "Please Select form" , ('Delete Listing','Change Address' , 'Change Status' , 'Change Features' , 'Change Property_type','Change Price') )
    if option == 'Change Price' :
        Listing_newPrice = st.number_input( 'Enter the new Price' )
        if st.button( "Update Task" ) :
            run_query( 'update listing set price ="{}", Update_date=now() WHERE listing_id ="{}"'.format( Listing_newPrice ,update_by_listing_id ) )
            db_conn.commit()
            st.success( "Record is updated" )
            
    elif option == 'Change Status' :
        Listing_newstatus = st.selectbox("Select Listing status" , listing_statuses, index = int(listing_statuses.index[listing_statuses['listing_status'] == task_status][0]) )
        if st.button( "Update Task" ) :
            run_query('UPDATE listing SET status_id = (select id from listing_status where status_name = "{}"), Update_date=now() where listing_id ="{}"'.format(Listing_newstatus , update_by_listing_id ) )
            db_conn.commit()
            st.success( "Record is updated" )
            
    elif option == 'Change Features' :
        col1 , col2 = st.columns( 2 )
        with col1 :
            Listing_newBeds = st.selectbox( "Bed_type" , beds, index = int(beds.index[beds['bed'] == task_Beds][0]) )

        with col2 :
            Listing_newBaths = st.selectbox( "Bath_type" , baths, index = int(baths.index[baths['bath'] == task_Bath][0]) )

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
            resultset3 = run_query( " select bed,bath from feature " )
            with st.expander( "Look up for Bed and Bath combination" ) :
                clean_db = pd.DataFrame( resultset3 ,
                                         columns=["Listing_beds" , "Listing_baths"] )
                st.dataframe( clean_db )
            
    elif option == 'Change Property_type' :
        Listing_type = st.selectbox( "Listing Type*" , listing_types, index = int(listing_types.index[listing_types['listing_type'] == task_property][0]) )
        if st.button( "Update Task" ) :
            run_query('UPDATE listing SET property_type_id = ( select id from property_type where property_type_name = "{}") where listing_id ="{}"'.format(Listing_type , update_by_listing_id ))
            db_conn.commit()
            st.success( "Record is updated")

    elif option == 'Change Address' :
        Listing_Street = st.text_input( "Enter the Street" ,task_street,max_chars=(300) )
        col1 , col2,col3= st.columns( 3 )
        with col1 :
            Listing_State = st.selectbox( "State" , states, index = int(states.index[states['state'] == task_state][0]))
        with col2 :
            Listing_uCity = st.selectbox( "City" , cities, index = int(cities.index[cities['city'] == task_city][0]) )
        with col3:
            Listing_uZipcode = st.selectbox( "Zipcode",zips,index = int(zips.index[zips['zip'] == task_zipcode][0]) )
        
        result2=run_query('select * from city where city= "{}" and state="{}" and zip_code="{}"'.format(Listing_uCity,Listing_State,Listing_uZipcode))
        
        if result2 :
            st.success( "Please proceed with updates" )
            if st.button( "Update Task" ) :
                run_query(
                    'update listing  set Update_Date=now(),  street = "{}",  city_id = (select id from city where city= "{}" and state = "{}" and zip_code ="{}") where listing_id = "{}"'.format(
                        Listing_Street , Listing_uCity , Listing_State ,
                        Listing_uZipcode , update_by_listing_id ) )
                db_conn.commit()
                run_query(
                    'update listing l inner join city c on l.city_id=c.id set l.full_address=(select concat(lower(l.street) ,",",lower(c.city),",",lower(c.state),",",c.zip_code)) where l.listing_id="{}"'.format(
                        update_by_listing_id ) )
                st.success( "Record is updated" )
                db_conn.commit()
        else:
            st.warning( "Incorrect combination, please enter correct values" )
            with st.expander( "Pease verify  below look up for city,state and zipcode" ) :
                resultset3 = run_query( "select state,city,zip_code from city" )
                clean_db = pd.DataFrame( resultset3 , columns=["State_name" , "City_name" , "Zip_code"] )
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
        resultset = run_query(
                    'select listing.listing_id,listing_status.status_name,listing.Price, city.city,city.state,city.zip_code,property_type.Property_type_name,feature.bed,feature.bath,listing.acre_lot,listing.house_size,listing.full_address,listing.street from listing inner join listing_status on listing_status.ID=listing.status_id inner join city on city.id=listing.city_id inner  join property_type on property_type.ID=listing.property_type_id inner join feature on feature.id=listing.listing_id where listing_id ="{}"'.format(
                        update_by_listing_id ) )
        clean_db1 = pd.DataFrame( resultset ,
                                     columns=["Listing_ID" , "Listing_Status" , "Listing_Price" ,
                                              "Listing_city" , "Listing_state" , "Listing_zipcode" ,
                                              "Listing_type" , "listing_bed" , "listing_bath" ,
                                              "Listing_Acrelot" , "Listing_house_size" ,
                                              "Listing_full_address" , "Listing_street"] )
        st.dataframe( clean_db1 )


def delete_module():
    resultset = run_query( " select listing.listing_id,listing_status.status_name,listing.Price,listing.acre_lot,listing.house_size,listing.full_address from listing inner join listing_status on listing_status.ID=listing.status_id" )
    clean_db= pd.DataFrame( resultset,columns=["Listing_ID","Listing_Status","Listing_Price","Listing_Acrelot","Listing_house_size","Listing_full_address"] )
    st.dataframe( clean_db)
    listing_id=run_query("select listing_id,status_id,Price,acre_lot,house_size from listing")
    unique_list=[i[0] for i in listing_id]
    
    delete_by_listing_id = st.selectbox( "Select Listing ID" , unique_list)
    
    if st.button( "Delete" ) :
        run_query('delete from listing where listing_id ="{}"'.format(delete_by_listing_id) )
        run_query('commit')
        st.warning( "Deleted: '{}'".format( delete_by_listing_id ) )


def plot_avg_by_state():
    viz_query_str = """ select avg(price) as average_price, state
                          from listing l
                          join city c on l.city_id = c.id
                         group by state
                         order by avg(price) desc;"""
    
    resultset = run_query(viz_query_str)
    resultdf = pd.DataFrame(resultset, columns=('Average Price','State'))
    
    fig, ax = plt.subplots()
    ax.get_xaxis().get_major_formatter().set_scientific(False)
    ax.barh(resultdf['State'], resultdf['Average Price'], align='center')
    ax.set_ylabel('States')
    ax.set_xlabel('Average Housing Price')
    ax.tick_params(axis='x', labelrotation=45)
    ax.set_title('Average Housing Price by States')
    
    st.pyplot(fig)    


def plot_avg_by_cities(inState):
    viz_query_str = """ select avg(price) as average_price, city
                          from listing l
                          join city c on l.city_id = c.id
                        where state = '""" + inState
    viz_query_str += """' group by city
                         order by avg(price) desc
                         limit 25;"""
    
    resultset = run_query(viz_query_str)
    resultdf = pd.DataFrame(resultset, columns=('Average Price','City'))
    
    fig, ax = plt.subplots()
    ax.get_xaxis().get_major_formatter().set_scientific(False)
    ax.barh(resultdf['City'], resultdf['Average Price'], align='center')
    ax.set_ylabel('Cities')
    ax.set_xlabel('Average Housing Price')
    ax.tick_params(axis='x', labelrotation=45)
    ax.set_title('Average Housing Price by Cities')
    
    st.pyplot(fig) 


def plot_avg_by_zip(inState):
    viz_query_str = """ select avg(price) as average_price, CONVERT(zip_code,char) as zip
                          from listing l
                          join city c on l.city_id = c.id
                        where state = '""" + inState
    viz_query_str += """' group by zip_code
                         order by avg(price) desc
                         limit 25;"""
    
    resultset = run_query(viz_query_str)
    resultdf = pd.DataFrame(resultset, columns=('Average Price','Zip'))
    
    fig, ax = plt.subplots()
    ax.get_xaxis().get_major_formatter().set_scientific(False)
    ax.barh(resultdf['Zip'], resultdf['Average Price'], align='center')
    ax.set_ylabel('Zip Code')
    ax.set_xlabel('Average Housing Price')
    ax.tick_params(axis='x', labelrotation=45)
    ax.set_title('Average Housing Price by Zip Codes')
    
    st.pyplot(fig) 
    


def main():
    if 'loggedIn' not in st.session_state:
        st.session_state.loggedIn = False
    
    menu = ["Home","Search Listings" ,"Add Listings" , "Update/Delete Listings" , "Statistical Plots", "Login", "SignUp" ]
    choice = st.sidebar.selectbox("Menu",menu )
    
    ## HOME PAGE
    if choice == "Home":
        home_page_module()
        
    ## LOGIN PAGE AND SUBSEQUENT FUNCTIONS
    elif choice == "Login":
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password",type='password')
        if st.sidebar.checkbox( "Login" ) :
            hashed_pswd = make_hashes( password )
            result =run_query('SELECT * FROM userstable WHERE username ="{}" and password="{}"'. format(username,check_hashes( password , hashed_pswd )))
            
            if result:
                st.session_state.loggedIn = True
                st.success( "successfully logged in as "+  username)
            else :
                st.warning( "incorrect usernmae/password" )
    
    ## UPDATE/DELETE PAGE
    if choice == "Update/Delete Listings":
        if st.session_state.loggedIn:
            st.subheader( "Update/Delete Listings" )
            listing_id = run_query( "select listing_id,status_id,Price,acre_lot,house_size from listing")
            unique_list = [i[0] for i in listing_id]
            update_by_listing_id = st.selectbox( "Select Listing ID to update" , unique_list )
            
            update_delete_module(update_by_listing_id)
        else:
            st.error("You need to login to be able to update/delete listings")
        
    ## ADD LISTINGS
    elif choice == "Add Listings":
        if st.session_state.loggedIn:
            st.subheader("Add New Listing Details")        
            add_listing_form()
        else:
            st.error("You need to login to be able to add listings")
        
        
    ## STATISTICAL VISUALIZATIONS
    elif choice == "Statistical Plots":
        if st.session_state.loggedIn:
            plotChoice = st.sidebar.selectbox("Select the plot you want to see",["-- Choose One --","Average Housing Price by Region"])
            
            if plotChoice == "Average Housing Price by Region":
                regionChoice = st.sidebar.selectbox("Select the Region for visualization",["States","Cities","Zip"])
                
                if regionChoice == "States":
                    plot_avg_by_state()
                else:
                    inState = st.sidebar.selectbox("Choose a State",states)
                    if regionChoice == "Cities":
                        plot_avg_by_cities(inState)
                    elif regionChoice == "Zip":
                        plot_avg_by_zip(inState)
        else:
            st.error("You need to login to be able to view statistics")
                
    ## SIGNUP PAGE
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
            
    ## SEARCH PAGE
    elif choice == "Search Listings":
        search_query_str = """select l.listing_id, l.listing_date, ls.status_name, lt.property_type_name, l.price, 
                              f.bed, f.bath, l.sold_date, l.full_address, l.street, c.city, 
                              c.state, c.zip_code, l.acre_lot, l.house_size 
                               from listing l 
                               join property_type lt 
                                 on l.property_type_id = lt.id 
                               join listing_status ls 
                                 on l.status_id = ls.id 
                               join city c
                                 on l.city_id = c.id 
                               join feature f 
                                 on l.feature_id = f.id """
        
        full_query_str = search_module(search_query_str)
        
        resultset = run_query(full_query_str)
        resultdf = pd.DataFrame(resultset, columns=('Listing Id','Listing Date','Listing Status','Property Type',
                                                    'Price','Bed','Bath','Sold Date','Full Address','Street',
                                                    'City','State','Zip Code','Acre Lot','House Size'))
        st.dataframe(resultdf, 1000, 500)
        


if __name__ == '__main__':
    main()
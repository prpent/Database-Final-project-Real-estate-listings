# __author:Owner
# date:6/16/2022
import streamlit as st
import pandas as pd
from PIL import Image
import mysql.connector

db_conn = mysql.connector.connect( **st.secrets["mysql"] )
cur = db_conn.cursor()


def run_query ( query ) :
    with db_conn.cursor() as cur :
        cur.execute( query )
        return cur.fetchall()


def main () :
    menu = ["Home" , "Search Listings" , "Update/Delete Listings" , "Add New Listing" , "Statistical Plots"]
    choice = st.sidebar.selectbox( "Menu" , menu )

    if choice == "Home" :
        st.title( "Realtor CRUD Webapp" )
        # image = Image.open( 'listing.jpeg' )
        # st.image( image , caption='** Buy a Listing** ' )
        st.subheader( "About Application:" )
        st.write(
            "The objective of our project is to create a web app for US Real Estate listings. The users would be welcomed by a page listing the top/latest listing and would have the capability like" )
        st.write( "1.Search listing by filters like zip code, price range, etc." )
        st.write( "2.Add a new listing" )
        st.write( "3.Edit/Remove an existing Listing" )
        st.write( "4.Research relevant statistics about the real estate market." )

    elif choice == "Search Listings" :
        search_query_str = 'select * from listing l'
        end_query_str = ';'

        with st.sidebar.form( key='search_form' ) :
            listingId = st.number_input( 'Listing Id' , min_value=0 )
            priceRange = st.slider( "Price Range" , value=[0 , 400000] , step=50000 )
            col1 , col2 = st.columns( 2 )
            with col1 :
                status = st.text_input( "Listing Status" )
                bed = st.number_input( 'Beds' , min_value=0 )
                acreLot = st.slider( "Acre Lot" , value=[0.00 , 10.00] , step=0.25 )
            with col2 :
                type = st.text_input( "Property Type" )
                bath = st.number_input( 'Baths' , min_value=0 )
                houseSize = st.slider( "House Size" , value=[0 , 10000] , step=500 )

            search = st.form_submit_button( 'SEARCH' )

        if search :
            if len( status ) > 0 :
                search_query_str += ' join listing_status ls on l.status_id = ls.id and ls.status_name = ' + status

            if listingId > 0 :
                search_query_str += ' where l.listing_id = ' + str( listingId )
            else :
                search_query_str += ' where l.listing_id is not null '

            if priceRange[0] > 0 or priceRange[1] < 400000 :
                search_query_str += ' and price between ' + str( priceRange )

            st.write( search_query_str )
        else :
            resultset = run_query( "select * from raw_list limit 50;" )
            st.dataframe( pd.DataFrame( resultset ) )

    elif choice == "Add New Listing" :

        st.subheader( "Add New Listing Details" )
        #
        Listing_type = st.selectbox( "Listing Type*" ,
                                     ['Condo' , 'Land' , 'Townhome' , 'Multi Family Home' , 'Single Family Home'] )
        Listing_Status = st.radio( "Select Listing status" , ('for_sale' , 'SOLD' , 'ready_to_build') )
        Listing_Price = st.number_input( 'Price' )
        col1 , col2 = st.columns( 2 )
        with col1 :
            Listing_Beds = st.number_input( 'Beds' , min_value=0 )
        with col2 :
            Listing_Baths = st.number_input( 'Baths' , min_value=0 )
        col3 , col4 = st.columns( 2 )
        with col3 :
            Listing_Acrelot = st.number_input( 'Acre Lot' )
        with col4 :
            Lisitng_Housesize = st.number_input( 'House Size' , min_value=0 )

        Listing_Fulladdress = st.text_area( "Full Address" , max_chars=(300) )
        Listing_Street = st.text_input( "Enter the Street" , max_chars=(300) )
        c_city , c_state , c_zp = st.columns( [4 , 3 , 2] )
        with c_city :
            Listing_City = st.text_input( "City" , max_chars=(50) )
        with c_state :
            Listing_State = st.text_input( "State" )
        with c_zp :
            Listing_Zipcode = st.text_input( "Zipcode" )

        if st.button( "Save" ) :
            args = [Listing_type , Listing_Status , Listing_Price , Listing_Beds , Listing_Baths , Listing_Acrelot ,
                    Listing_Fulladdress , Listing_Street , Listing_City , Listing_State , Listing_Zipcode ,
                    Lisitng_Housesize]
            cur.callproc( 'Proc_insert_listing' , args )
            # result_id = run_query("select ID from Listing where full_address = Listing_Fulladdress ;")
            # st.markdown('ID',result_id)
            st.success( "Listing is successfully saved." )


if __name__ == '__main__' :
    main()
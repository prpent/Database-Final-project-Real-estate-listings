CREATE DEFINER=`root`@`localhost` PROCEDURE `insert_listing_proc`(IN Listing_type VARCHAR(20),IN Listing_Status VARCHAR(20), IN Listing_Price float,IN  Listing_Beds INT,IN  Listing_Baths INT,
IN  Listing_Acrelot FLOAT,IN Listing_Street VARCHAR(300),IN Listing_City VARCHAR(50),IN Listing_State VARCHAR(25),IN Listing_Zipcode MEDIUMINT(5),IN Lisitng_Housesize INT )
sd: BEGIN

DECLARE V_LIS_STAT_ID INT  DEFAULT 0;
DECLARE V_PROPERT_ID INT  DEFAULT 0;
DECLARE V_FEATURE_ID INT DEFAULT 0;
DECLARE V_CITY_ID INT DEFAULT 0;
DECLARE MSG INT DEFAULT 0;
DECLARE TEXT_CODE_CITY VARCHAR (200) DEFAULT NULL ;
DECLARE V_LISTING_ID INT DEFAULT NULL;
DECLARE V_NEW_LIST_ID VARCHAR(300) DEFAULT NULL ;
DECLARE V_ADDRESS_DUP VARCHAR(300) DEFAULT NULL;
DECLARE RETURN_TEXT VARCHAR(300) DEFAULT NULL;
DECLARE INSERT_TEXT VARCHAR(300) DEFAULT NULL;
-- DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET IsError=1;
-- TEMP table to hold status of proc
drop table if exists status;
create table status (MSG varchar (300));
insert into status values("Error - Please enter data for Listing"); --  #1 1 “Enter data for Listing”
commit;
truncate table status;

IF Listing_Price IS NULL or Listing_Price < 1  THEN 
insert into status values("Error - Please enter price for the listing (> $1)"); -- #2 Enter ateast $1 as Price
commit;
LEAVE sd;
END IF;


IF Listing_Street IS NULL or Listing_Street = ''  THEN 
insert into status values("Error - Please enter a valid Address"); -- #3 'Enter Address'
commit;
LEAVE sd;
END IF;


IF Listing_City IS NULL or Listing_State is null or Listing_Zipcode is null or Listing_City ='' or Listing_State  ='' or Listing_Zipcode  ='' THEN 
insert into status values( 'Error - Please enter valid City Deatils (City/State/ZIP)' ); -- Error#4 - Enter City Deatils (City/State/ZIP)
commit;
LEAVE sd;
END IF;

SELECT ID into V_FEATURE_ID FROM FEATURE WHERE BED = coalesce(bed,0) = coalesce(Listing_Beds,0) AND coalesce(bath,0.0) = coalesce(Listing_Baths,0.0) limit 1;
SELECT ID INTO V_LIS_STAT_ID FROM LISTING_STATUS  WHERE STATUS_NAME = Listing_Status limit 1;
SELECT ID INTO V_PROPERT_ID FROM PROPERTY_TYPE WHERE PROPERTY_TYPE_NAME = Listing_type limit 1;

SELECT LISTING_ID INTO V_LISTING_ID FROM LISTING 
WHERE upper(FULL_ADDRESS) = CONCAT(upper(Listing_Street), ", ",UPPER(Listing_State), ", ", lpad(Listing_Zipcode,5,0))
AND sold_date is null;

IF V_LISTING_ID IS NOT NULL THEN 
insert into status values("Error - Duplicate address found. Please Enter a valid address." ); -- 'Error#5 - DUPLICATE ADDRESS ENTRY'
commit;
LEAVE sd;
END IF;

IF V_FEATURE_ID IS NULL THEN 
insert into feature (bed, bath,create_date) values (Listing_Beds,Listing_Baths, now());
commit;
SELECT max(ID) INTO V_FEATURE_ID FROM FEATURE WHERE BED = coalesce(bed,0) = coalesce(Listing_Beds,0) AND coalesce(bath,0.0) = coalesce(Listing_Baths,0.0);
END IF;

SELECT ID INTO V_CITY_ID FROM CITY WHERE UPPER(CITY) = UPPER(Listing_City) AND UPPER(STATE) = UPPER(Listing_State) AND lpad(ZIP_CODE,5,0) = lpad(Listing_Zipcode,5,0) limit 1;

IF V_CITY_ID IS NULL THEN
insert into status values("Error - Please enter valid city details (City/State/ZIP)"); #6 PLEASE ENTER VALID CITY DETAILS
SET MSG = 2;
LEAVE sd;
END IF;

INSERT INTO LISTING (status_id, price, PROPERTY_type_id, feature_id, full_address, street, city_id, acre_lot, house_size,listing_date,CREATE_DATE) 
VALUES (V_LIS_STAT_ID,Listing_Price,V_PROPERT_ID,V_FEATURE_ID,CONCAT(upper(Listing_Street), ", ",UPPER(Listing_State), ", ", lpad(Listing_Zipcode,5,0)),Listing_Street,V_CITY_ID,coalesce(Listing_Acrelot,NULL), coalesce(Lisitng_Housesize,NULL),now(),NOW());

commit;
SELECT MAX(LISTING_ID) INTO V_NEW_LIST_ID FROM LISTING WHERE full_address = CONCAT(upper(Listing_Street), ", ",UPPER(Listing_State), ", ", lpad(Listing_Zipcode,5,0))  AND SOLD_DATE IS NULL;

SET INSERT_TEXT = concat("Listing created successfully, ID:",cast(V_NEW_LIST_ID as CHAR(10)));
insert into status values(INSERT_TEXT);
commit;
-- RETURN RETURN_TEXT;
END
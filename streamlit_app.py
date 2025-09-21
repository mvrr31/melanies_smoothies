import streamlit as st
from snowflake.snowpark.functions import col,when_matched
import requests
# App title and description
st.title("Customize Your Smoothie :cup_with_straw: ")
st.write(
    """Choose the fruits you want in your custom smoothie!"""
)

# Input for smoothie name
name_on_order = st.text_input("Name of Smoothie:")
st.write("The name of your Smoothie will be", name_on_order)

cnx =st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).to_pandas()
fruit_options = my_dataframe['FRUIT_NAME'].tolist()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

if ingredients_list:
    # Join ingredients with a space
    ingredients_string = ' '.join(ingredients_list)
    smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
    sf_df= st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    # Create the insert statement, specifying both relevant columns
    my_insert_stmt = (
        "INSERT INTO smoothies.public.orders (ingredients, name_on_order) "
        f"VALUES ('{ingredients_string}','{name_on_order}')"
    )
   

    
    # Insert on button click
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"An error occurred: {e}")


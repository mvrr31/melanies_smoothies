import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import requests

# App title and description
st.title("Customize Your Smoothie :cup_with_straw: ")
st.write(
    """Choose the fruits you want in your custom smoothie!"""
)

# Input for smoothie name
name_on_order = st.text_input("Name of Smoothie:")
st.write("The name on your Smoothie will be", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit names and their search terms from Snowflake into a Snowpark DataFrame
my_dataframe = session.table('smoothies.public.fruit_options').select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark DataFrame to pandas DataFrame for .loc/.iloc access
pd_df = my_dataframe.to_pandas()

# Show dataframe for debugging - can comment out later
st.dataframe(pd_df, use_container_width=True)
st.stop()

# List of fruit names for multiselect display
fruit_options = pd_df['FRUIT_NAME'].tolist()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        # Use pd_df.loc to get corresponding SEARCH_ON value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition Information')
        # Use the search_on value in the API call, not fruit_chosen
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    my_insert_stmt = (
        "INSERT INTO smoothies.public.orders (ingredients, name_on_order) "
        f"VALUES ('{ingredients_string.strip()}','{name_on_order}')"
    )

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"An error occurred: {e}")

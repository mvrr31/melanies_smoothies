import streamlit as st
from snowflake.snowpark.functions import col
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

# Get both FRUIT_NAME and SEARCH_ON columns
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col('FRUIT_NAME'), col('SEARCH_ON')).to_pandas()

# Show the dataframe for validation/debugging (as in image)
st.dataframe(data=my_dataframe, use_container_width=True)
st.stop()  # Pause so you can review the dataframe

# Prepare fruit option display list
fruit_options = my_dataframe['FRUIT_NAME'].tolist()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

if ingredients_list:
    fruit_chosen = ingredients_list[0]
    # Lookup corresponding SEARCH_ON value
    fruit_choosen = my_dataframe.loc[
        my_dataframe['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'
    ].values[0]
    ingredients_string = ' '.join(ingredients_list)

    st.subheader(fruit_chosen + ' Nutrition Information')
    # Now use SEARCH_ON value in the API call (not the display name)
    smoothiefroot_response = requests.get(
        "https://my.smoothiefroot.com/api/fruit/" + str(fruit_choosen)
    )
    sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    my_insert_stmt = (
        "INSERT INTO smoothies.public.orders (ingredients, name_on_order) "
        f"VALUES ('{ingredients_string}','{name_on_order}')"
    )

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"An error occurred: {e}")

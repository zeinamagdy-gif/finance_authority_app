import json
import os.path

import streamlit as st
import pandas as pd
# import numpy as np
# import plotly.express as px

category_file="Categories.json"
# first you set the webb page name icone
st.set_page_config(page_title="Simple Finance App",page_icon="💰", layout="wide")
if "Category"  not in st.session_state:
    st.session_state.category={
        "Uncategoriesd":[],
        "New Category":[],
    }
if os.path.exists(category_file):
    with open(category_file,"r") as f:
        st.session_state.category= json.load(f)
# st.write("JSON file location:",os.path.abspath(category_file))
# st.write("Category Loading:", st.session_state.category)
def save_categories():
    with open(category_file,"w")as f:
        json.dump(st.session_state.category,f)
def categories_transaction(df):
    df["Categories"]="Uncategoriesd"
    for category,keywords in st.session_state.category.items():
        if category=="Uncategoriesd" or not keywords:
            continue
        lowered_keywords=[keyword.lower().strip()for keyword in keywords]
        for idx, row in df.iterrows():
            details=row["Details"].lower().strip()
            if any(keyword in details for keyword in lowered_keywords):
                df.at[idx, "Categories"] = category

    return df
def load_transaction(file):# this function read and return every transformation to main function for user to interact file is the parameter for function to input
    try: # Read CSV file into a DataFrame
        df = pd.read_csv(file) # that read the csv file
        df.columns = [col. strip() for col in df.columns] # that doesnt do anything in my code removing it didnt add or remove anything but it subose to remove spaces in the title of columnns
        df["Amount"] = ( df["Amount"] .astype(str) .str.replace(",", "") .astype(float) ) # Remove commas from Amount and convert to float
        df["Date"] = pd.to_datetime( df["Date"], format="%d %b %Y" )# to make date writen in day month year
        # Treat empty strings and spaces as missing values
        df = df.replace(r'^\s*$', pd.NA, regex=True)

        # Remove columns where every value is empty/null
        df = df.dropna(axis=1, how="all")
        # st.write(df) # this  display the dataframe on the strealit page
        new_category = st.text_input("New Category Name ")
        category_button = st.button("Add Category")
        if category_button and new_category:
            if new_category not in st.session_state.category:
                st.session_state.category[new_category] = []
                save_categories()
                # st.success(f"Added new category{new_category}")
                st.rerun()


    except Exception as e:# if there is error say what is the error if their is no error return nothing
        st.error(f"Error processing file: {str(e)}")
        return None
    return categories_transaction(df)
# main function is responsible to control the application and what user see


def add_keyword_to_category(category, keyword):
    keyword = keyword.strip().lower()

    if category not in st.session_state.category:
        return False

    if keyword and keyword not in st.session_state.category[category]:
        st.session_state.category[category].append(keyword)
        save_categories()
        return True

    return False
def main():
    st.title("Simple Finance Dashboard")#title of the uploader so the user know what to do
    file_uploader = st.file_uploader( "Upload Your Transaction File", type=["csv"] )# the place where he put the csv its function in streamlit that pull file and its type csv
    if file_uploader is not None: # Load and process the CSV if the file uploader have a file contunie if not wait
        df = load_transaction(file_uploader) # Only continue if loading was successful so it pull from load function
        if df is not None: # Separate Debit and Credit transactions
            # st.subheader("All Transactions")
            # st.write(df)
            debit_df = df[df["Debit/Credit"] == "Debit"].copy()# create the data for the debit tab
            credit_df = df[df["Debit/Credit"] == "Credit"].copy() # create the data for the creditt tab
            st.session_state.debit_df=debit_df.copy()
            tab1, tab2 = st.tabs( ["Expenses (Debit)", "Payments (Credit)"] ) #that ctreat the 2 tabs of the two datas of debit and credit
            with tab1:
                st.subheader("Your Expenses")
                edited_df=st.data_editor(
                    st.session_state.debit_df[["Date","Details","Amount","Categories"]],
                    column_config={
                        "Date":st.column_config.DateColumn("Date",format="MM/DD/YYYY"),
                        "Amount":st.column_config.NumberColumn("Amount",format="%.2f AED"),
                        "Categories":st.column_config.SelectboxColumn(
                            "Category",
                            options=list(st.session_state.category.keys())
                        )
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="category_editor"

                )
                save_button=st.button("Apply changes:",type="primary")
                if save_button:
                    for idx, row in edited_df.iterrows():
                        new_category = row["Categories"]
                        if new_category== st.session_state.debit_df.at[idx,"Categories"]:
                            continue
                        details=row["Details"]
                        st.session_state.debit_df.at[idx,"Categories"]=new_category
                        add_keyword_to_category(new_category,details)





            with tab2: st.write(credit_df)

main()# it call main functio to see the process on streamlit page
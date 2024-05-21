import pandas as pd
from homepage.models import Product

# Load the .csv data set
data = pd.read_csv('C:/Users/myka/Documents/GitHub/AntiFE/Produktai_data_lt.csv')

# Iterate over each row in the data set
for index, row in data.iterrows():
    # Create a new Product instance for each row
    product = Product(
        name=row['Name'],
        phenylalanine=row['Phenylalanine'],
        protein=row['Protein'],
        fiber=row['Carbohydrates'],
        total_fat=row['Total_fat'],
        calories=row['Calories'],
        measure = row['Home_measure'],
        homePhenylalanine = row['Home_phenylalanine'],
        homeWeight = row['Home_weight'],
        category = row['Category'],
        color = row['Color']
    )
    # Save the new Product instance to the database
    product.save()
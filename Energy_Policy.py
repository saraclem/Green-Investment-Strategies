#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 23:57:26 2023

@author: faraz
"""


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

import requests
from bs4 import BeautifulSoup

# Send a GET request to the webpage
url = "https://www.whitehouse.gov/climate/"
response = requests.get(url)


if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
else: 
    print("Error making request, try after some time")

target_element = soup.find_all("div", class_="wysiwyg wysiwyg-text acctext--con")
target_elements=target_element[6:]
headline_elements = soup.find_all("h3", class_="accordion__headline")
headings= [i.text.strip().replace("\xa0", " ") for i in headline_elements]


data=[]

# Iterate through the HTML data for each sector
for html_data, sector in zip(target_elements, headings):
    ul_element = html_data.find("ul")
    
    # Check if the ul element exists
    if ul_element:
        # Find all list items (li) under the ul element
        list_items = ul_element.find_all("li")
        
        # Extract text from each li item
        #li_texts = [item.get_text(strip=True) for item in list_items]
        li_texts = [item.text.strip() for item in list_items]
        
        # Append the data to the list
        data.extend([(sector, li_text) for li_text in li_texts])

# Create a DataFrame from the extracted data
df = pd.DataFrame(data, columns=["Sector", "Description"])

# Print the DataFrame
print(df)

#Doing some sentiment analysis on each of the new policies 

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

# Perform sentiment analysis and add results to new columns
df["Sentiment"] = df["Description"].apply(lambda x: sia.polarity_scores(x))
df["Sentiment_Label"] = df["Sentiment"].apply(lambda x: "Positive" if x["compound"] >= 0.05 else ("Negative" if x["compound"] <= -0.05 else "Neutral"))

# Print the DataFrame with sentiment analysis results
print(df)
df.to_csv("Sector_Policies.csv")


import matplotlib.pyplot as plt
from wordcloud import WordCloud
text = ' '.join(df['Description'])

wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

# Display the WordCloud
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.title("Word Cloud for Description Column")
plt.show()

sector_counts = df['Sector'].value_counts()
# Create a bar chart
plt.figure(figsize=(10, 6))
sector_counts.plot(kind='bar', color='skyblue')
plt.xlabel('Sector')
plt.ylabel('Count')
plt.title('Sector Distribution')
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.show()



#IEA Data- https://docs.google.com/spreadsheets/d/1K0YalKFSmlQniDXvnqZIsaanVg5Nz14YV7Ptxm5MDP0/edit?usp=sharing
#File ID- 1IpR_1iMI7KPPT7z0reUE8IvIJ1XmEcda

# link= https://drive.google.com/file/d/19iU8WSb8-43KZa37Vnx9g7Yb_Cc-jHMK/view?usp=sharing
import requests



url='https://drive.google.com/file/d/16NFG9oi-2QgTHdmPYXniZiAd5j3yuhd5/view?usp=sharing'
url='https://drive.google.com/uc?id=' + url.split('/')[-2]
df_investment_data = pd.read_csv(url)


df_investment_data['Budget commitment (million USD)'] = df_investment_data['Budget commitment (million USD)'].str.replace(' ', '', regex=True).astype(float)

# Print the fixed DataFrame
print(df_investment_data)

import seaborn as sns

# Category vs Policy Count Heatmap
heatmap_data = df_investment_data.groupby(['Category', 'Measures']).size().reset_index(name='Count')
heatmap_pivot = heatmap_data.pivot(index='Category', columns='Measures', values='Count')
plt.figure(figsize=(12, 6))
sns.heatmap(heatmap_pivot, cmap='YlGnBu', annot=True, fmt='g')
plt.title('Category vs Policy Count Heatmap')
plt.xlabel('Policy Measures')
plt.ylabel('Category')
plt.show()

df_investment_data['Start year'] = df_investment_data['Start year'].astype('category')

# Budget Allocation by Category
plt.figure(figsize=(10, 6))
sns.barplot(data=df_investment_data, x='Category', y='Budget commitment (million USD)', estimator=sum)
plt.xticks(rotation=45)
plt.title('Budget Allocation by Category')
plt.xlabel('Category')
plt.ylabel('Total Budget (million USD)')
plt.show()


budget_by_category = df_investment_data.groupby('Category')['Budget commitment (million USD)'].sum().reset_index()

# Sort the data by budget in descending order for a better visualization
budget_by_category = budget_by_category.sort_values(by='Budget commitment (million USD)', ascending=False)

# Create a bar plot
plt.figure(figsize=(12, 6))
plt.barh(budget_by_category['Category'], budget_by_category['Budget commitment (million USD)'], color='skyblue')
plt.xlabel('Budget commitment (million USD)')
plt.ylabel('Category')
plt.title('Budget Allocation by Category')
plt.gca().invert_yaxis()  # Invert y-axis for the largest budget at the top
plt.show()
#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Importing all necessary libraries
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
import pandas as pd
import seaborn as sns


# In[2]:


#Load and Transform Data

Distribution_Data = pd.read_csv("C:\Walter\Career\Tech\Data Science\Projects\PYTHON\Distribution Network Analysis\synthetic_ev_distribution_data.csv")
Geospatial_Data = pd.read_csv("C:\Walter\Career\Tech\Data Science\Projects\PYTHON\Distribution Network Analysis\synthetic_geospatial_data.csv") 
Weather_Data = pd.read_csv("C:\Walter\Career\Tech\Data Science\Projects\PYTHON\Distribution Network Analysis\synthetic_weather_data.csv")


# In[3]:


Distribution_Data.head()


# In[4]:


Geospatial_Data.head()


# In[5]:


Weather_Data.head()


# ## Understanding the Structure of the Dataset

# In[6]:


#Check data types and missing values
Distribution_Data.info()

#Description of Numerical Columns
Distribution_Data.describe().round(2)


# In[7]:


#Check data types and missing values
Geospatial_Data.info()

#Description of Numerical Columns
Geospatial_Data.describe().round(2)


# In[8]:


#Check data types and missing values
Weather_Data.info()

#Description of Numerical Columns
Weather_Data.describe().round(2)


# ## Exploratory Data Analysis
# 
# ### This Phase involves both Univariate and Bivariate Analysis
# 
# __Univariate Analysis__
# 
#    1. Visualize the distribution of electricity consumption
#    2. Analyse the distribution of Electirc Vehicle (EV) types, Charging habits, customer types
# 
# **Bivariate Analysis**
# 
#    3. Use Geospatial data to visualize the location of substations and EV charging stations
#    4. Analyze the capacity of transmission lines
# 

# ### Univariate Analysis

# In[9]:


# Set the style and color palette of the plots
sns.set(style = "whitegrid")
sns.set_palette("pastel")

#Create a 2x2 subplot grid
fig, axes = plt.subplots(2,2,figsize = (10,6))

#Plot the distribution of electricity consumption
sns.histplot(data = Distribution_Data, x = "Electricity_Consumption (kWh)", bins = 30, kde = True, ax = axes[0,0])
axes[0,0].set_title("Distribution of Electricity Consumption")
axes[0,0].set_xlabel("Electricity Consumption(kwh)")
axes[0,0].set_ylabel("Frequency")

#Plot the distribution of EV types
sns.countplot(data = Distribution_Data, y = "EV_Type", ax = axes[0,1])
axes[0,1].set_title("Distribution of EV Types")
axes[0,1].set_xlabel("Count")
axes[0,1].set_ylabel("EV Type")

#Plot the distribution of Charging Habits
sns.countplot(data = Distribution_Data, y = "Charging_Habit", ax = axes[1,0])
axes[1,0].set_title("Distribution of Charging Habits")
axes[1,0].set_xlabel("Count")
axes[1,0].set_ylabel("Charging Habit")

#Plot the distribution of Customer Type
sns.countplot(data = Distribution_Data, y = "Customer_Type", ax = axes[1,1])
axes[1,1].set_title("Distribution of Customer Type")
axes[1,1].set_xlabel("Count")
axes[1,1].set_ylabel("Customer Type")

#Adjust Plot layout
plt.tight_layout

#Display the Plots
plt.show()


# ### Bivariate Analysis

# In[10]:


#Extract Lat and Long for EV charging Stations
Distribution_Data['ev_latitude'] = Distribution_Data['EV_Charging_Station_Location'].apply(lambda x: float(x.split(",")[0].replace("(", "").strip()))
Distribution_Data['ev_longitude'] = Distribution_Data['EV_Charging_Station_Location'].apply(lambda x: float(x.split(",")[1].replace(")", "").strip()))

#Extract Lat and Long for Sub-stations
Geospatial_Data['substation_latitude'] = Geospatial_Data['Substation_Location'].apply(lambda x: float(x.split(',')[0].replace('(','').strip()))
Geospatial_Data['substation_longitude'] = Geospatial_Data['Substation_Location'].apply(lambda x: float(x.split(',')[1].replace(')','').strip()))

# Drop the original Location to clean up the dataframe
Distribution_Data = Distribution_Data.drop(columns = ['EV_Charging_Station_Location'])
Geospatial_Data = Geospatial_Data.drop(columns = ['Substation_Location'])


# In[11]:


Distribution_Data.head()


# In[13]:


#Convert the dataframes to Geodataframes

ev_gdf = gpd.GeoDataFrame(Distribution_Data,
                          geometry = gpd.points_from_xy(Distribution_Data.ev_longitude, Distribution_Data.ev_latitude))

substation_gdf = gpd.GeoDataFrame(Geospatial_Data,
                          geometry = gpd.points_from_xy(Geospatial_Data.substation_longitude, Geospatial_Data.substation_latitude))

#Load the world map data
world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"));

# Filter the map to North America
north_america = world[world["continent"] == "North America"]

#Plotting the map for North America
fig,ax = plt.subplots(figsize = (7.5,7))
north_america.boundary.plot(ax = ax, linewidth = 0.5, color = 'black')
north_america.plot(ax = ax, color = 'lightblue', edgecolor = 'black')

# Plotting the substation on the map
substation_gdf.plot(ax = ax, marker = 's', markersize = 100, color = 'blue', label = 'substations')

#Plotting the ev charging stations on the map
ev_gdf.plot(ax = ax, markersize = 10, color = 'red', label = 'EV charging stations', alpha = 0.5)

# set title and axis labels
plt.title('Locations of the substations and its associated EV charging station in North America')
plt.xlabel('longitude')
plt.ylabel('latitude')
plt.tight_layout()
plt.legend()
plt.show()


# In[14]:


from shapely.geometry import LineString


# In[15]:


#Convert the dataframes to Geodataframes

ev_gdf = gpd.GeoDataFrame(Distribution_Data,
                          geometry = gpd.points_from_xy(Distribution_Data.ev_longitude, Distribution_Data.ev_latitude))

substation_gdf = gpd.GeoDataFrame(Geospatial_Data,
                          geometry = gpd.points_from_xy(Geospatial_Data.substation_longitude, Geospatial_Data.substation_latitude))

#Create Lines connecting each substation to its associated EV charging station
lines = []
for _, ev_row in Distribution_Data.iterrows():
    substation = Geospatial_Data[Geospatial_Data['Substation_ID'] == ev_row['Substation_ID']].iloc[0]
    line = [(ev_row['ev_longitude'], ev_row['ev_latitude']), (substation['substation_longitude'], substation['substation_latitude'])]
    lines.append(line)
line_gdf = gpd.GeoDataFrame(geometry = [LineString(line) for line in lines])
    
    #Load the world map data
world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

# Filter the World map to include only North America
north_america = world[world["continent"] == "North America"]

#Plotting the map for North America with lines
fig,ax = plt.subplots(figsize = (10,5))
north_america.boundary.plot(ax = ax, linewidth = 0.5, color = 'black')
north_america.plot(ax = ax, color = 'lightblue', edgecolor = 'black')

# Plotting the substations, EV charging stations, and the lines
substation_gdf.plot(ax = ax, marker = 's', markersize = 100, color = 'blue', label = 'substations')
ev_gdf.plot(ax = ax, markersize = 10, color = 'red', label = 'EV Charging Stations', alpha = 0.5)
line_gdf.plot(ax = ax, linewidth = 0.5, color = 'gray', label = 'connections')

# set title and axis labels
plt.title('Connections between the substations and associated EV charging station in North America')
plt.xlabel('longitude')
plt.ylabel('latitude')
plt.legend()
plt.tight_layout()
plt.show()


# In[14]:


import geopandas as gpd
from shapely.geometry import LineString
import matplotlib.pyplot as plt

# Filter for the first substation and its associated EV Charging stations
selected_substation = Geospatial_Data.iloc[0]
associated_ev = Distribution_Data[Distribution_Data['Substation_ID'] == selected_substation['Substation_ID']]

# Convert the dataframes to Geodataframes using the provided latitude and longitude columns
ev_gdf_selected = gpd.GeoDataFrame(associated_ev, geometry=gpd.points_from_xy(associated_ev.ev_longitude, associated_ev.ev_latitude))
selected_substation_gdf = gpd.GeoDataFrame(selected_substation.to_frame().transpose(), 
                                           geometry=gpd.points_from_xy([selected_substation['substation_longitude']], 
                                                                       [selected_substation['substation_latitude']]))

# Create lines connecting the selected substation to its associated EV charging stations
lines_selected = [(ev_row['ev_longitude'], ev_row['ev_latitude'], 
                   selected_substation['substation_longitude'], selected_substation['substation_latitude']) 
                  for _, ev_row in associated_ev.iterrows()]

line_gdf_selected = gpd.GeoDataFrame(geometry=[LineString([(line[0], line[1]), (line[2], line[3])]) for line in lines_selected])

# Define the North America variable
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
north_america = world[world['continent'] == 'North America']

# Plot the data
fig, ax = plt.subplots(figsize=(10, 10))

# Plot the North America map
north_america.plot(ax=ax, color='whitesmoke', edgecolor='black')

# Plot the EV charging stations and substation
ev_gdf_selected.plot(ax=ax, color='blue', marker='o', label='EV Charging Stations')
selected_substation_gdf.plot(ax=ax, color='red', marker='x', label='Substation')

# Plot the lines connecting the substation to the EV charging stations
line_gdf_selected.plot(ax=ax, color='green', linestyle='-', linewidth=1, label='Connection Lines')

# Add title and legend
plt.title(f"Zoomed-in View: Connections between {selected_substation['Substation_ID']} and Associated EV Charging Stations")
plt.legend()

# Show the plot
plt.show()


# In[16]:


import geopandas as gpd
from shapely.geometry import LineString
import matplotlib.pyplot as plt

# Filter for the first substation and its associated EV Charging stations
selected_substation = Geospatial_Data.iloc[1]
associated_ev = Distribution_Data[Distribution_Data['Substation_ID'] == selected_substation['Substation_ID']]

# Convert the dataframes to Geodataframes using the provided latitude and longitude columns
ev_gdf_selected = gpd.GeoDataFrame(associated_ev, geometry=gpd.points_from_xy(associated_ev.ev_longitude, associated_ev.ev_latitude))
selected_substation_gdf = gpd.GeoDataFrame(selected_substation.to_frame().transpose(), 
                                           geometry=gpd.points_from_xy([selected_substation['substation_longitude']], 
                                                                       [selected_substation['substation_latitude']]))

# Create lines connecting the selected substation to its associated EV charging stations
lines_selected = [(ev_row['ev_longitude'], ev_row['ev_latitude'], 
                   selected_substation['substation_longitude'], selected_substation['substation_latitude']) 
                  for _, ev_row in associated_ev.iterrows()]

line_gdf_selected = gpd.GeoDataFrame(geometry=[LineString([(line[0], line[1]), (line[2], line[3])]) for line in lines_selected])

# Define the North America variable
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
north_america = world[world['continent'] == 'North America']

# Plot the data
fig, ax = plt.subplots(figsize=(9, 6))

# Plot the North America map
north_america.plot(ax=ax, color='whitesmoke', edgecolor='black')

# Plot the EV charging stations and substation
ev_gdf_selected.plot(ax=ax, color='blue', marker='o', label='EV Charging Stations')
selected_substation_gdf.plot(ax=ax, color='red', marker='x', label='Substation')

# Plot the lines connecting the substation to the EV charging stations
line_gdf_selected.plot(ax=ax, color='green', linestyle='-', linewidth=1, label='Connection Lines')

# Add title and legend
plt.title(f"Zoomed-in View: Connections between {selected_substation['Substation_ID']} and Associated EV Charging Stations")
plt.legend()

# Show the plot
plt.show()


# In[15]:


import geopandas as gpd
from shapely.geometry import LineString
import matplotlib.pyplot as plt

# Filter for the first substation and its associated EV Charging stations
selected_substation = Geospatial_Data.iloc[49]
associated_ev = Distribution_Data[Distribution_Data['Substation_ID'] == selected_substation['Substation_ID']]

# Convert the dataframes to Geodataframes using the provided latitude and longitude columns
ev_gdf_selected = gpd.GeoDataFrame(associated_ev, geometry=gpd.points_from_xy(associated_ev.ev_longitude, associated_ev.ev_latitude))
selected_substation_gdf = gpd.GeoDataFrame(selected_substation.to_frame().transpose(), 
                                           geometry=gpd.points_from_xy([selected_substation['substation_longitude']], 
                                                                       [selected_substation['substation_latitude']]))

# Create lines connecting the selected substation to its associated EV charging stations
lines_selected = [(ev_row['ev_longitude'], ev_row['ev_latitude'], 
                   selected_substation['substation_longitude'], selected_substation['substation_latitude']) 
                  for _, ev_row in associated_ev.iterrows()]

line_gdf_selected = gpd.GeoDataFrame(geometry=[LineString([(line[0], line[1]), (line[2], line[3])]) for line in lines_selected])

# Define the North America variable
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
north_america = world[world['continent'] == 'North America']

# Plot the data
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the North America map
north_america.plot(ax=ax, color='whitesmoke', edgecolor='black')

# Plot the EV charging stations and substation
ev_gdf_selected.plot(ax=ax, color='blue', marker='o', label='EV Charging Stations')
selected_substation_gdf.plot(ax=ax, color='red', marker='x', label='Substation')

# Plot the lines connecting the substation to the EV charging stations
line_gdf_selected.plot(ax=ax, color='green', linestyle='-', linewidth=1, label='Connection Lines')

# Add title and legend
plt.title(f"Zoomed-in View: Connections between {selected_substation['Substation_ID']} and Associated EV Charging Stations")
plt.legend()

# Show the plot
plt.show()


# In[16]:


Distribution_Data.columns


# In[17]:


# Group by Location and the EV type, then count the number of stations
grouped_data = Distribution_Data.groupby(['ev_latitude', 'ev_longitude', 'EV_Type']).size().reset_index(name = 'count')

# Convert grouped data to GeoDataFrame
grouped_gdf = gpd.GeoDataFrame(grouped_data,
                              geometry = gpd.points_from_xy(grouped_data.ev_longitude, grouped_data.ev_latitude))

# Load the World Map data and filter for North America
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
north_america = world[world['continent'] == 'North America']

# Plotting with zoom
fig, ax = plt.subplots(figsize = (9,6))
north_america.boundary.plot(ax = ax, linewidth = 0.5, color = 'black')
north_america.plot(ax = ax, color = 'lightblue', edgecolor = 'black')

#  Define colors for each EV type
colors = {'Electric Car':'magenta', 'Electric Scooter':'yellow', 'Electric Bike':'k'}

# Plot the EV charging stations with marker sizes reflecting the count
for ev_type, color in colors.items():
    sub_gdf = grouped_gdf[grouped_gdf['EV_Type'] == ev_type]
    sub_gdf.plot(ax = ax, markersize = sub_gdf['count'] * 20, color = color, label = ev_type, alpha = 0.7)

# set title and axis labels
plt.title('Distribution of EV Charging Stations by Type and Frequency in North America')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.legend()
plt.tight_layout()
plt.show()    


# #### NETWORK CAPACITY ASSESSMENT
# 
# To perform network capacity assessment
# 
# * Calculate the total electricity consumption for each substation
# * Compare the total consumption with the transmission line capacity

# In[18]:


# Group the EV Distribution data by substation ID and calculate the total electricity consumption for each substation
total_consumption_per_substation = Distribution_Data.groupby('Substation_ID')['Electricity_Consumption (kWh)'].sum().reset_index()

# Merging the total consumption data with Geospatial data
network_capacity_data = pd.merge(Geospatial_Data, total_consumption_per_substation, on = 'Substation_ID')

# Renaming the columns for better understanding
network_capacity_data.rename(columns = {'Electricity_Consumption (kWh)': 'Total_Consumption (kWh)'}, inplace = True)

# Calculating the ratio of total consumption to transmission line Capacity
# Conversion: 1MW = 1,000kWh
network_capacity_data['Consumption_to_Capacity_Ratio'] = network_capacity_data['Total_Consumption (kWh)']/(network_capacity_data['Transmission_Line_Capacity (MW)'] * 1000)


# In[19]:


network_capacity_data.head()


# In[21]:


from shapely.geometry import Point


# In[22]:


# Create the GeoDataFrame for the network capacity for the dataframes
geometry_network_capacity = [Point(lon,lat) for lon,lat in zip(network_capacity_data['substation_longitude'], network_capacity_data['substation_latitude'])]
gdf_network_capacity = gpd.GeoDataFrame(network_capacity_data, geometry = geometry_network_capacity)

# Plotting in chloropleth style
fig, ax = plt.subplots(figsize = (12,10))
north_america.plot(ax = ax, color = 'lightgray', edgecolor = 'k')
gdf_network_capacity.plot(column = 'Consumption_to_Capacity_Ratio', cmap = 'coolwarm', legend = True, 
                          marker = 's', markersize = 100, ax = ax, legend_kwds = {'label': 'Consumption to Capacity Ratio','orientation': 'horizontal'})
ax.set_title('Consumption to Capacity Ratio of Substations')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
plt.tight_layout()
plt.show()


# In[23]:


# Group by the substation ID for the number of EVs
ev_counts = Distribution_Data.groupby('Substation_ID')['Number_of_EVs'].sum().reset_index()

# Merge the network capacity data with the EV counts
final_data = pd.merge(ev_counts, network_capacity_data, on = 'Substation_ID')

# Correlation
correlation_ratio = final_data['Number_of_EVs'].corr(final_data['Consumption_to_Capacity_Ratio'])


# In[24]:


correlation_ratio.round(5)


# In[25]:


# Scatter plot with regressing line
plt.figure(figsize = (10,5))
sns.regplot(x = 'Number_of_EVs', y = 'Consumption_to_Capacity_Ratio', data = final_data, scatter_kws = {'s': 50}, line_kws = {'color':'red'}, ci = None)
plt.title('Relationship between number of EVs and Consumption to Capacity Ratio')
plt.xlabel('Number of EVs')
plt.ylabel('Consumption to Capacity Ratio')
plt.grid(True)
plt.tight_layout()
plt.show()


# #### IDENTIFYING BOTTLENECKS
# 
# * By analysing the map, we can identify the substations and areas that are potential bottlenecks in the distribution network. These are the areas where the consumption ratio is high.

# In[26]:


# bottleneck consumption to capacity ratio greater than 1
bottleneck_substation = network_capacity_data[network_capacity_data['Consumption_to_Capacity_Ratio']>0.9]


# In[27]:


# Displaying
bottleneck_substation


# #### OPTIMIZING NETWORK UPGRADES
# For optimizing upgrades, focus on substations with potential to have high consumption_to_Capacity_Ratio. Upgrading the  transmission lines or adding additional capacity in these areas can help in managing the potential to have increased load effectively and ensuring grid reliability.
# 
# Additionally, lets note from the analysis
# * The Geographical distribution of EV charging stations: where EV charging stations are quite far from the Substations
# 
# Also, the business should consider:
# 
# * Potential future growth in EV adoption in different areas
# * Costs associated with different upgrade options

# In[28]:


# Top 5 top stations reaching the maximum consumption to capacity Ratio 
top_5_substations = network_capacity_data.nlargest(5,'Consumption_to_Capacity_Ratio')
top_5_substations 


# #### Correlation With Weather Data
# * Analyzing the correlation between weather data and electricity consumption can provide insights into how weather conditions affect the distribution

# In[29]:


# merge weather data with distribution data
merged_data = pd.merge(Distribution_Data, Weather_Data, on =['Timestamp', 'Substation_ID'])

# Calculate then correlation between weather condition and electricity consumption
correlation_matrix = merged_data[['Electricity_Consumption (kWh)','Temperature (°C)','Precipitation (mm)']].corr()

# Display
correlation_matrix


# In[30]:


# Electricity consumption vs Temperature
plt.figure(figsize = (7,5))
sns.scatterplot(data = merged_data, x = 'Temperature (°C)', y = 'Electricity_Consumption (kWh)', alpha = 0.6)
plt.title('Electricity vs Temperature')
plt.xlabel('Temperature')
plt.ylabel('Electricity')
plt.show;


# In[75]:


# Electricity consumption vs Precipitation
plt.figure(figsize = (7,5))
sns.scatterplot(data = merged_data, x = 'Precipitation (mm)', y = 'Electricity_Consumption (kWh)', alpha = 0.6)
plt.title('Precipitation vs Temperature')
plt.xlabel('Precipitation')
plt.ylabel('Electricity')
plt.show;


# #### Insights
# 1. Electricity Consumption: The electricity consumption is mostly centered around 500 kWh, with certain instances of higher consumption. This indicates varied demand at different times and locations.
# 
# 2. EV Types and Charging Habits: Electric scooter is the most common EV type. Most customers charge their EVs daily, indicating a consistent daily load on the distribution network
# 
# 3. Consumer Type: Most customers are commercial customers
# 
# 4. Geospatial Distribution: The spatial distribution of substations and EV charging stations is widespread.
# 
# 5. Geospatial Distribution:Thd EV charging station seems to be too far from its corresponding Substation.
# 
# 6. Network Capacity: Some substations have a high  Consumption_to_Capacity_Ratio (CTCR,) indicating potential bottlenecks and oveerloads within the network. There is also no correlation with the number of EVs per substation and the CTCR.This shows that Number of EVs is not a factor for overload.
# 
# 7. Weather Correlation: The correlation between weather conditions (Temperature and Precipitaion) and electricity consumption is weak in the current dataset, suggesting that other factors might be more directly responsible for electricity consumption. 

# #### The Optimization Strategy/Recommendation
# 
# Based on the business problem under consideration, and the insights gathered, the following recommendations are made as a way forward.
# 
# 1. **Prioritize Sustation upgrade**: Priorotize upgrades at substations where the Consumption_to_Capacity_Ratio is high, indicating potential overloads. Upgrade the transmission lines because the EV charging stations are too far from the corresponding Substations.
# 
# 2. **Geospatial Analysis for Upgrade Palnning**: Use Geospatial analysis to determine the optimal locations for new substations or upgrades to existing ones. Consider factors like the proximity to high load demand areas (areas with high consumption to capacity ratio) and geographical constraints.
# 
# 3. **Demand Side Management**: Implement demand-side management strategies to balance the  load on the grid. Encourage customers to charge their EVs during off-peak hours incentives of dynamic pricing.
# 
# 4. **Advanced Monitoring amd Analytics**: Deploy advanced systems to continuously monitor the health and performance of the distribution network. Use analytics to predict potential issues and the preventive action.
# 
# 5. **Return on Investment**: Conduct a comprehensive cost benefit analysis for different upgrade options. Consider factors like the cos of upgrades, operational costs, potential revenue from increased capacity and the impact on service reliability and customer satisfaction.
# 
# 6. **Customer Engagement**: Engae with customers to understand their needs and expectations. Provide clear communication and network upgrades and how they would enhance service reliability and meet the growing demand for EV charging.
# 
# 7. **Continuous Improvement**: Continuously monitor amd assess the performance of the distribbution network. Gather feedback from customers amd their stakeholders, and use the feedback to make further improvements and optimization.
# 
# By following these steps, PowerCharge Utilities can develop and effective optimization strategy and enhance to manage the increased load demand from EV Charging stations, ensure the reliability and resilience of the distribution nework as well as meet customer expectation, while optimizinf costs and upholding regulatory standards.

# In[ ]:





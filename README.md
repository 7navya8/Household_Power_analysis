# Household Energy Consumption Analysis

A Python project that analyses minute-level household electricity data to find peak usage, unusual days, and the biggest energy-using circuits, and to estimate cost and CO2 emissions.

## Dataset
UCI Individual Household Electric Power Consumption dataset (one household in France, Dec 2006 to Nov 2010, about 2.07 million readings). Download it from the UCI Machine Learning Repository or Kaggle. The raw file is not included here because of its size.

## What I did
- Cleaned the data: handled missing values (1.25% of rows) and checked for duplicates and invalid readings
- Converted readings to kWh and built daily and monthly totals
- Found peak usage hours
- Flagged unusual days (above mean + 2 standard deviations)
- Split consumption by circuit (kitchen, laundry, water heater/AC, other)
- Estimated cost and CO2 emissions

## Key results
- Peak usage is around 8 PM (about 1.9 kW on average)
- Average daily use is about 25.9 kWh, with 49 unusually high days
- Water heater / AC is the largest metered load (35.5%); kitchen 6.2%, laundry 7.1%, other 51.2%
- Total use was about 37,284 kWh, which is roughly 26.5 tonnes of CO2 and Rs 2.6 lakh at the assumed values below

## Assumptions
- Emission factor: 0.71 kg CO2 per kWh (approximate India grid average)
- Tariff: Rs 7 per kWh (assumed)

## Tools
Python, Pandas, Matplotlib

## How to run
1. Download the dataset and put household_power_consumption.txt in this folder
2. pip install pandas matplotlib
3. python energy_analysis.py

## Note
The data is from a French household, so this project shows the method and is not a study of Indian homes.


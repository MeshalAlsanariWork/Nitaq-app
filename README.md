# 🏡 Nitaq - Smart Property Finder

## 📌 Project Overview

Finding the perfect apartment in Riyadh can be challenging, especially when looking for essential services nearby. **Nitaq** simplifies this process by offering interactive maps, valuable insights, and smart filtering options to help renters make informed decisions based on their needs.

## 🚀 Features

- 🗺 **Interactive Map**: Allows users to explore different areas based on their preferences.
- 🍽 **Nearby Services**: Displays available services such as restaurants and markets, with ratings.
- 🏠 **Available Apartments**: Showcases rental properties in the selected area.
- 📝 **Detailed Apartment Info**: Provides in-depth details about each listed apartment.

## 🔧 Installation

Clone the repository:

```bash
git clone https://github.com/MeshalAlsanariWork/Nitaq_app.git
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

## 📊 Data Collection & Processing

### 🔍 Web Scraping: Google Maps API

Extracting data from Google Maps API to collect relevant details for real estate insights.Includes information on nearby restaurants, markets, and services.**Data points collected:** Location coordinates, service ratings, reviews, business categories.

### 🏠 Data Storage
- Raw data stored in `Riyadh_data`.
- Cleaned and structured data stored in `Cleaned/Original_data.rar`.
- Analyzed in `Nitaq_EDA.ipynb`
- Ensures efficient retrieval and analysis.

**Data categories include:**
- Bus Stops
- Cafes & Bakeries
- Airbnb Listings
- Entertainment Venues
- Supermarkets & Groceries
- Gyms
- Hospitals & Clinics
- Malls
- Metro Stations
- Pharmacies
- Restaurants

### 📊 Exploratory Data Analysis (EDA)

Analyzed in `Nitaq_EDA.ipynb` in data storage.Key insights derived from real estate trends, service distributions, and user preferences.Includes data visualization and statistical summaries.

### 🧪 Data Processing Pipeline
1. **Data Collection**: Extracting information via APIs and web scraping.
2. **Data Cleaning**: Handling missing values, duplicates, and formatting inconsistencies.
3. **EDA**: Understanding patterns, correlations, and insights.
4. **Final Storage**: Structured data ready for predictive modeling and application integration.

## 🚀 Next Steps
- Implement ML models for improved recommendations.
- Optimize database for efficient querying.
- Enhance the user interface (UI) for a smoother and more engaging user experience.
- Improve search performance to reduce response time for finding properties and nearby services.

## 🔗 Useful Links

- **Live Demo**: [Nitaq](https://nitaq-app-demo.streamlit.app)
- **GitHub Repository**: [Nitaq-Property-Finder](https://github.com/MeshalAlsanariWork/Nitaq_app)
- **Data**: [Bus Stop](https://www.kaggle.com/datasets/meshalalsanari/riyadh-bus-stop-stations/data)
- **Data**: [Cafes and Bakeries](https://www.kaggle.com/datasets/meshalalsanari/riyadh-cafes-and-bakeries-data)
- **Data**: [Entertainment](https://www.kaggle.com/datasets/meshalalsanari/riyadh-entertainment)
- **Data**: [Gyms](https://www.kaggle.com/datasets/meshalalsanari/riyadh-gyms-1-7k)
- **Data**: [Hospitals and Clinics](https://www.kaggle.com/datasets/meshalalsanari/riyadh-hospitals-and-clinics-719/data)
- **Data**: [Metro Stations](https://www.kaggle.com/datasets/meshalalsanari/riyadh-metro-stations)
- **Data**: [Restaurants](https://www.kaggle.com/datasets/meshalalsanari/riyadh-restaurants/data)
- **Data**: [SuperMarker and Groceries](https://www.kaggle.com/datasets/meshalalsanari/riyadh-supermarket-and-groceries/data)
- **Data**: [Pharamcies](https://www.kaggle.com/datasets/meshalalsanari/riyadh-pharmacies/data)
- **Data**: [Mall](https://www.kaggle.com/datasets/meshalalsanari/riyadh-mall/data)
- **Data**: Airbnb containted in Data Stroage folder.

  
- ## 🌞 Future Enhancements
- AI-driven insights for data visualization.
- Expansion of service categories.
- Machine learning models for personalized recommendations.
- Add More Airbnb services 

## 🤝 Contribution
We welcome contributions! Feel free to submit pull requests or report any issues.

## 💡 Contributors
- **Meshal Alsanari**
- **Manar AlShaykh**
- **Munirah AlZuman**
- **Tahani AlOtaibi**
- **Jumanah AlQurashi**
- **linktre URL:** [linktree](https://linktr.ee/Netaq)


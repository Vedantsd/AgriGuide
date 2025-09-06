# 🌾 AgriGuide - Crop Prediction System

A comprehensive Python application built with CustomTkinter that predicts the best crops to grow based on soil conditions, environmental parameters, and location data.

## 🎯 Features

### Core Functionality
- **Smart Crop Prediction**: Analyzes soil and environmental parameters to recommend suitable crops
- **Comprehensive Dataset**: 40+ crops with detailed growing requirements
- **Auto-Location Detection**: Automatically fetches your location using IP geolocation
- **Seasonal Awareness**: Considers current month for seasonal crop recommendations
- **Suitability Scoring**: Provides percentage match scores for each crop recommendation

### Input Parameters
- **Soil pH Level**: Range validation (4.0-9.0)
- **Soil Moisture**: Percentage-based moisture content (20-100%)
- **Soil Type**: Dropdown selection (Clay, Loam, Sandy, Sandy Loam)
- **Temperature**: Current/expected temperature in Celsius (10-40°C)
- **Rainfall**: Expected rainfall in millimeters (20-400mm)

### Auto-Detected Information
- **Location**: City, country, and climate zone detection
- **Current Month**: Seasonal timing for crop planning
- **Climate Zone**: Tropical, Semi-arid, or Temperate classification

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7+
- Internet connection (for location detection)

### Required Packages
```bash
pip install customtkinter pandas requests
```

## 🏃 Running the Application

1. **Clone or download** the project files
2. **Navigate** to the project directory
3. **Run** the application:
   ```bash
   python crop_predictor.py
   ```

## 🎮 How to Use

1. **Launch the Application**: Run `crop_predictor.py`
2. **Auto-Detection**: The app automatically detects your location and current month
3. **Manual Options** (Optional):
   - Click **🔄** to refresh location detection
   - Click **✏️** next to location to enter manually
   - Click **✏️** next to month to select different growing month
4. **Enter Parameters**:
   - Soil pH level (e.g., 6.5)
   - Soil moisture percentage (e.g., 70)
   - Select soil type from dropdown
   - Enter temperature in Celsius (e.g., 25)
   - Enter expected rainfall in mm (e.g., 100)
5. **Get Predictions**: Click "🔍 Predict Best Crops"
6. **Review Results**: Scroll through detailed recommendations with compatibility scores

## 📊 Dataset Information

The application uses a comprehensive CSV dataset containing 40+ crops with the following parameters:

### Crop Parameters
- **pH Range**: Minimum and maximum soil pH requirements
- **Moisture Range**: Soil moisture requirements (%)
- **Soil Type**: Preferred soil type (Clay, Loam, Sandy, Sandy Loam)
- **Temperature Range**: Optimal growing temperature (°C)
- **Rainfall Range**: Required rainfall (mm)
- **Growing Season**: Start and end months
- **NPK Values**: Nitrogen, Phosphorus, Potassium requirements

### Sample Crops Included
- **Cereals**: Rice, Wheat, Corn, Barley, Oats, Millet, Sorghum
- **Legumes**: Soybean, Chickpea, Lentil, Black Gram, Green Gram
- **Vegetables**: Tomato, Potato, Onion, Carrot, Cabbage, Spinach
- **Fruits**: Banana, Mango, Apple, Orange, Grapes
- **Cash Crops**: Cotton, Sugarcane, Sunflower, Groundnut
- **Spices**: Chilli, Garlic
- **Plantation Crops**: Tea, Coffee, Rubber, Coconut

## 🧠 Prediction Algorithm

### Suitability Scoring System
The application uses a weighted scoring system to calculate crop suitability:

1. **pH Level (25% weight)**: Matches user pH with crop's optimal range
2. **Moisture Content (20% weight)**: Compares soil moisture requirements
3. **Soil Type (15% weight)**: Exact match for soil type preference
4. **Temperature (20% weight)**: Matches with crop's temperature range
5. **Rainfall (15% weight)**: Compares expected vs required rainfall
6. **Seasonal Timing (5% weight)**: Current month vs growing season

### Score Interpretation
- **🟢 80-100%**: Excellent match - highly recommended
- **🟡 60-79%**: Good match - suitable with minor adjustments
- **🟠 40-59%**: Fair match - possible with care
- **Below 40%**: Not recommended for current conditions

## 🔧 Technical Features

### GUI Components
- **Modern Interface**: Built with CustomTkinter for a contemporary look
- **Dark Theme**: Eye-friendly dark mode interface
- **Scrollable Layout**: Full content visibility with smooth scrolling
- **Manual Override Options**: Edit location and month manually if needed
- **Intuitive Controls**: Refresh and edit buttons positioned strategically
- **Input Validation**: Real-time validation with helpful error messages
- **Enhanced Results**: Comprehensive crop information with improved formatting

### Data Processing
- **CSV Data Handling**: Efficient pandas-based data processing
- **Real-time Calculations**: Instant suitability scoring
- **Location Services**: IP-based geolocation with fallback options
- **Climate Classification**: Automatic climate zone determination

## 🌐 Location & Climate Detection

The application automatically determines your climate zone based on latitude:
- **Tropical**: Within 23.5° of the equator
- **Semi-arid**: Between 23.5° and 35° latitude
- **Temperate**: Beyond 35° latitude

## 📝 Example Usage Scenario

**Input Example:**
- pH: 6.2
- Moisture: 65%
- Soil Type: Loam
- Temperature: 22°C
- Rainfall: 80mm
- Location: Mumbai, India (Tropical)
- Month: June

**Expected Output:**
- Rice (95% match)
- Corn (87% match)
- Soybean (82% match)
- Tomato (76% match)
- Cotton (71% match)

## 🔍 Troubleshooting

### Common Issues
1. **Dataset Not Found**: Ensure `crops_dataset.csv` is in the same directory
2. **Location Detection Failed**: Check internet connection; app works offline with default settings
3. **Invalid Input**: Follow the specified ranges for each parameter
4. **No Crop Recommendations**: Adjust parameters or consider soil improvement

### Error Messages
- **"Dataset file not found"**: Place the CSV file in the correct location
- **"pH must be between 4.0 and 9.0"**: Enter valid pH range
- **"No suitable crops found"**: Try different parameter combinations

## 🛠 Customization Options

### Adding New Crops
1. Open `crops_dataset.csv`
2. Add new rows with crop parameters
3. Follow the existing column format
4. Save and restart the application

### Modifying Scoring Weights
Edit the `calculate_crop_suitability()` method in `crop_predictor.py` to adjust parameter weights.

## 🎨 UI Customization

The application supports CustomTkinter themes:
- **Appearance Mode**: "dark", "light", or "system"
- **Color Theme**: "blue", "green", or "dark-blue"

Modify these in the `__init__()` method of the `CropPredictorApp` class.

## 📈 Future Enhancements

Potential improvements for future versions:
- Weather API integration for real-time data
- Soil testing recommendations
- Crop rotation suggestions
- Market price integration
- Multiple language support
- Mobile app version
- Machine learning-based predictions
- Historical weather data analysis

## 🤝 Contributing

Feel free to contribute to this project by:
- Adding more crops to the dataset
- Improving the prediction algorithm
- Enhancing the user interface
- Adding new features
- Reporting bugs or suggestions

## 🏅 Acknowledgments

- **CustomTkinter**: Modern GUI framework
- **Pandas**: Data processing capabilities
- **IP Geolocation Services**: Location detection functionality
- **Agricultural Research**: Crop parameter data sources

---

**Happy Farming! 🌱**
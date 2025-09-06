import customtkinter as ctk
import pandas as pd
import requests
import json
from datetime import datetime
from tkinter import messagebox
import os

class CropPredictorApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Crop Prediction System")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        self.location_info = {"city": "Unknown", "country": "Unknown", "climate": "Temperate"}
        self.current_month = datetime.now().month
        self.dataset_path = "crops_dataset.csv"
        
        self.load_dataset()
        
        self.create_widgets()
        
        self.fetch_location_data()
        
    def manual_location_input(self, event=None):
        from tkinter import simpledialog
        
        location_dialog = ctk.CTkToplevel(self.root)
        location_dialog.title("Manual Location Entry")
        location_dialog.geometry("400x300")
        location_dialog.transient(self.root)
        location_dialog.grab_set()
        
        location_dialog.update_idletasks()
        x = (location_dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (location_dialog.winfo_screenheight() // 2) - (300 // 2)
        location_dialog.geometry(f"400x300+{x}+{y}")
        
        title_label = ctk.CTkLabel(
            location_dialog,
            text="Enter Location Details",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=20)
        
        city_label = ctk.CTkLabel(location_dialog, text="City:")
        city_label.pack(pady=5)
        city_entry = ctk.CTkEntry(location_dialog, placeholder_text="Enter your city")
        city_entry.pack(pady=5, padx=20, fill="x")
        
        country_label = ctk.CTkLabel(location_dialog, text="Country:")
        country_label.pack(pady=5)
        country_entry = ctk.CTkEntry(location_dialog, placeholder_text="Enter your country")
        country_entry.pack(pady=5, padx=20, fill="x")
        
        climate_label = ctk.CTkLabel(location_dialog, text="Climate Zone:")
        climate_label.pack(pady=5)
        climate_var = ctk.StringVar(value="Temperate")
        climate_dropdown = ctk.CTkOptionMenu(
            location_dialog,
            values=["Tropical", "Semi-arid", "Temperate"],
            variable=climate_var
        )
        climate_dropdown.pack(pady=5, padx=20, fill="x")
        
        def save_location():
            city = city_entry.get().strip()
            country = country_entry.get().strip()
            
            if city and country:
                self.location_info["city"] = city
                self.location_info["country"] = country
                self.location_info["climate"] = climate_var.get()
                
                self.location_label.configure(
                    text=f"Location: {city}, {country} ({climate_var.get()} climate)"
                )
                location_dialog.destroy()
            else:
                error_label = ctk.CTkLabel(
                    location_dialog,
                    text="Please enter both city and country",
                    text_color="red"
                )
                error_label.pack(pady=5)
        
        def cancel_location():
            location_dialog.destroy()
        
        button_frame = ctk.CTkFrame(location_dialog)
        button_frame.pack(pady=20, padx=20, fill="x")
        
        save_button = ctk.CTkButton(button_frame, text="Save", command=save_location)
        save_button.pack(side="left", padx=10)
        
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=cancel_location)
        cancel_button.pack(side="right", padx=10)
        
    def manual_month_input(self, event=None):
        month_dialog = ctk.CTkToplevel(self.root)
        month_dialog.title("Select Month")
        month_dialog.geometry("350x250")
        month_dialog.transient(self.root)
        month_dialog.grab_set()
        
        month_dialog.update_idletasks()
        x = (month_dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (month_dialog.winfo_screenheight() // 2) - (250 // 2)
        month_dialog.geometry(f"350x250+{x}+{y}")
        
        title_label = ctk.CTkLabel(
            month_dialog,
            text="Select Growing Month",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=20)
        
        info_label = ctk.CTkLabel(
            month_dialog,
            text="Choose the month you plan to start growing:",
            font=ctk.CTkFont(size=12)
        )
        info_label.pack(pady=5)
        
        month_names = ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
        
        current_month_name = month_names[self.current_month - 1]
        month_var = ctk.StringVar(value=current_month_name)
        month_dropdown = ctk.CTkOptionMenu(
            month_dialog,
            values=month_names,
            variable=month_var
        )
        month_dropdown.pack(pady=15, padx=20, fill="x")
        
        def save_month():
            selected_month = month_var.get()
            month_number = month_names.index(selected_month) + 1
            self.current_month = month_number
            
            self.month_label.configure(
                text=f"Current Month: {selected_month}"
            )
            month_dialog.destroy()
        
        def cancel_month():
            month_dialog.destroy()
        
        button_frame = ctk.CTkFrame(month_dialog)
        button_frame.pack(pady=20, padx=20, fill="x")
        
        save_button = ctk.CTkButton(button_frame, text="Save", command=save_month)
        save_button.pack(side="left", padx=10)
        
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=cancel_month)
        cancel_button.pack(side="right", padx=10)
        
    def load_dataset(self):
        try:
            if os.path.exists(self.dataset_path):
                self.crop_data = pd.read_csv(self.dataset_path)
                print(f"Loaded {len(self.crop_data)} crops from dataset")
            else:
                messagebox.showerror("Error", f"Dataset file '{self.dataset_path}' not found!")
                self.crop_data = pd.DataFrame()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dataset: {str(e)}")
            self.crop_data = pd.DataFrame()
    
    def create_widgets(self):
        title_label = ctk.CTkLabel(
            self.root, 
            text="🌾 Crop Prediction System 🌾", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=20)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.root,
            height=580,
            fg_color="transparent",
            scrollbar_button_color="gray",
            scrollbar_button_hover_color="darkgray"
        )
        self.scrollable_frame.pack(pady=10, padx=40, fill="both", expand=True)
        
        def _on_mousewheel(event):
            self.scrollable_frame._parent_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.root.bind_all("<MouseWheel>", _on_mousewheel)
        
        main_frame = ctk.CTkFrame(self.scrollable_frame)
        main_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        auto_info_frame = ctk.CTkFrame(main_frame)
        auto_info_frame.pack(pady=10, padx=20, fill="x")
        
        auto_info_label = ctk.CTkLabel(
            auto_info_frame, 
            text="📍 Auto-Detected Information", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        auto_info_label.pack(pady=10)
        
        location_frame = ctk.CTkFrame(auto_info_frame)
        location_frame.pack(pady=5, padx=10, fill="x")
        
        self.location_label = ctk.CTkLabel(
            location_frame, 
            text="Location: Fetching...", 
            font=ctk.CTkFont(size=12)
        )
        self.location_label.pack(side="left", padx=(10, 5), pady=5)
        
        refresh_location_button = ctk.CTkButton(
            location_frame,
            text="🔄",
            width=30,
            height=25,
            command=self.fetch_location_data
        )
        refresh_location_button.pack(side="right", padx=(5, 10), pady=5)
        
        manual_location_button = ctk.CTkButton(
            location_frame,
            text="✏️",
            width=30,
            height=25,
            command=self.manual_location_input
        )
        manual_location_button.pack(side="right", padx=2, pady=5)
        
        month_frame = ctk.CTkFrame(auto_info_frame)
        month_frame.pack(pady=5, padx=10, fill="x")
        
        month_names = ["", "January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
        self.month_label = ctk.CTkLabel(
            month_frame, 
            text=f"Current Month: {month_names[self.current_month]}", 
            font=ctk.CTkFont(size=12)
        )
        self.month_label.pack(side="left", padx=(10, 5), pady=5)
        
        manual_month_button = ctk.CTkButton(
            month_frame,
            text="✏️",
            width=30,
            height=25,
            command=self.manual_month_input
        )
        manual_month_button.pack(side="right", padx=(5, 10), pady=5)
        
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(pady=20, padx=20, fill="x")
        
        input_label = ctk.CTkLabel(
            input_frame, 
            text="📝 Enter Soil & Environmental Parameters", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        input_label.pack(pady=15)
        
        grid_frame = ctk.CTkFrame(input_frame)
        grid_frame.pack(pady=10, padx=20, fill="x")
        
        ph_label = ctk.CTkLabel(grid_frame, text="Soil pH Level:", font=ctk.CTkFont(size=12))
        ph_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.ph_entry = ctk.CTkEntry(grid_frame, placeholder_text="Enter pH (4.0-9.0)")
        self.ph_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        moisture_label = ctk.CTkLabel(grid_frame, text="Soil Moisture (%):", font=ctk.CTkFont(size=12))
        moisture_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.moisture_entry = ctk.CTkEntry(grid_frame, placeholder_text="Enter moisture (20-100%)")
        self.moisture_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        soil_type_label = ctk.CTkLabel(grid_frame, text="Soil Type:", font=ctk.CTkFont(size=12))
        soil_type_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        self.soil_type_var = ctk.StringVar(value="Loam")
        self.soil_type_dropdown = ctk.CTkOptionMenu(
            grid_frame, 
            values=["Clay", "Loam", "Sandy", "Sandy Loam"], 
            variable=self.soil_type_var
        )
        self.soil_type_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        temp_label = ctk.CTkLabel(grid_frame, text="Temperature (°C):", font=ctk.CTkFont(size=12))
        temp_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        self.temp_entry = ctk.CTkEntry(grid_frame, placeholder_text="Enter temperature (10-40°C)")
        self.temp_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        
        rainfall_label = ctk.CTkLabel(grid_frame, text="Expected Rainfall (mm):", font=ctk.CTkFont(size=12))
        rainfall_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        
        self.rainfall_entry = ctk.CTkEntry(grid_frame, placeholder_text="Enter rainfall (20-400mm)")
        self.rainfall_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        
        grid_frame.grid_columnconfigure(1, weight=1)
        
        predict_button = ctk.CTkButton(
            input_frame, 
            text="🔍 Predict Best Crops", 
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self.predict_crops
        )
        predict_button.pack(pady=20)
        
        results_frame = ctk.CTkFrame(main_frame)
        results_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        results_label = ctk.CTkLabel(
            results_frame, 
            text="🌱 Crop Recommendations", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        results_label.pack(pady=15)
        
        self.results_text = ctk.CTkTextbox(
            results_frame, 
            height=300,
            font=ctk.CTkFont(size=11),
            wrap="word"
        )
        self.results_text.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.results_text.insert("0.0", "Enter your soil and environmental parameters above and click 'Predict Best Crops' to get personalized crop recommendations based on your conditions.")
    
    def fetch_location_data(self):
        apis = [
            {
                'url': 'http://ip-api.com/json/',
                'city_key': 'city',
                'country_key': 'country',
                'lat_key': 'lat'
            },
            {
                'url': 'https://ipinfo.io/json',
                'city_key': 'city',
                'country_key': 'country',
                'lat_key': None  # This API returns "loc" as "lat,lon"
            },
            {
                'url': 'http://ipapi.co/json/',
                'city_key': 'city',
                'country_key': 'country_name',
                'lat_key': 'latitude'
            },
            {
                'url': 'https://ipapi.co/json/',
                'city_key': 'city',
                'country_key': 'country_name', 
                'lat_key': 'latitude'
            }
        ]
        
        self.location_label.configure(text="Location: Detecting...")
        
        for api in apis:
            try:
                print(f"Trying API: {api['url']}")
                response = requests.get(api['url'], timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"API Response: {data}")
                    
                    city = data.get(api['city_key'], 'Unknown')
                    country = data.get(api['country_key'], 'Unknown')
                    
                    latitude = None
                    if api['lat_key'] and api['lat_key'] in data:
                        latitude = data[api['lat_key']]
                    elif 'loc' in data:
                        try:
                            lat_lon = data['loc'].split(',')
                            latitude = float(lat_lon[0])
                        except:
                            latitude = None
                    
                    if city != 'Unknown' and country != 'Unknown':
                        self.location_info["city"] = city
                        self.location_info["country"] = country
                        
                        if latitude is not None:
                            try:
                                lat_float = float(latitude)
                                if abs(lat_float) < 23.5:
                                    self.location_info["climate"] = "Tropical"
                                elif abs(lat_float) < 35:
                                    self.location_info["climate"] = "Semi-arid"
                                else:
                                    self.location_info["climate"] = "Temperate"
                            except:
                                self.location_info["climate"] = "Temperate"
                        
                        self.location_label.configure(
                            text=f"Location: {self.location_info['city']}, {self.location_info['country']} ({self.location_info['climate']} climate)"
                        )
                        print(f"Successfully detected location: {city}, {country}")
                        return
                    
            except requests.exceptions.Timeout:
                print(f"Timeout for API: {api['url']}")
                continue
            except requests.exceptions.RequestException as e:
                print(f"Request error for API {api['url']}: {e}")
                continue
            except Exception as e:
                print(f"Error with API {api['url']}: {e}")
                continue
        
        print("All location APIs failed")
        self.location_label.configure(text="Location: Unable to detect - Click to set manually")
        
        self.location_label.bind("<Button-1>", self.manual_location_input)
    
    def validate_inputs(self):
        try:
            ph = float(self.ph_entry.get())
            if not (4.0 <= ph <= 9.0):
                raise ValueError("pH must be between 4.0 and 9.0")
            
            moisture = float(self.moisture_entry.get())
            if not (20 <= moisture <= 100):
                raise ValueError("Moisture must be between 20% and 100%")
            
            temp = float(self.temp_entry.get())
            if not (10 <= temp <= 40):
                raise ValueError("Temperature must be between 10°C and 40°C")
            
            rainfall = float(self.rainfall_entry.get())
            if not (20 <= rainfall <= 400):
                raise ValueError("Rainfall must be between 20mm and 400mm")
            
            return {
                "ph": ph,
                "moisture": moisture,
                "soil_type": self.soil_type_var.get(),
                "temperature": temp,
                "rainfall": rainfall
            }
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return None
    
    def calculate_crop_suitability(self, crop_row, user_inputs):
        score = 0
        max_score = 0
        
        if crop_row['ph_min'] <= user_inputs['ph'] <= crop_row['ph_max']:
            score += 25
        else:
            ph_distance = min(abs(user_inputs['ph'] - crop_row['ph_min']), 
                            abs(user_inputs['ph'] - crop_row['ph_max']))
            score += max(0, 25 - (ph_distance * 5))
        max_score += 25
        
        if crop_row['moisture_min'] <= user_inputs['moisture'] <= crop_row['moisture_max']:
            score += 20
        else:
            moisture_distance = min(abs(user_inputs['moisture'] - crop_row['moisture_min']), 
                                  abs(user_inputs['moisture'] - crop_row['moisture_max']))
            score += max(0, 20 - (moisture_distance * 0.5))
        max_score += 20
        
        if crop_row['soil_type'] == user_inputs['soil_type']:
            score += 15
        max_score += 15
        
        if crop_row['temperature_min'] <= user_inputs['temperature'] <= crop_row['temperature_max']:
            score += 20
        else:
            temp_distance = min(abs(user_inputs['temperature'] - crop_row['temperature_min']), 
                              abs(user_inputs['temperature'] - crop_row['temperature_max']))
            score += max(0, 20 - (temp_distance * 2))
        max_score += 20
        
        if crop_row['rainfall_min'] <= user_inputs['rainfall'] <= crop_row['rainfall_max']:
            score += 15
        else:
            rainfall_distance = min(abs(user_inputs['rainfall'] - crop_row['rainfall_min']), 
                                  abs(user_inputs['rainfall'] - crop_row['rainfall_max']))
            score += max(0, 15 - (rainfall_distance * 0.1))
        max_score += 15
        
        month_start = crop_row['month_start']
        month_end = crop_row['month_end']
        
        if month_start <= month_end:
            if month_start <= self.current_month <= month_end:
                score += 5
        else:
            if self.current_month >= month_start or self.current_month <= month_end:
                score += 5
        max_score += 5
        
        return (score / max_score) * 100 if max_score > 0 else 0
    
    def predict_crops(self):
        user_inputs = self.validate_inputs()
        if not user_inputs:
            return
        
        if self.crop_data.empty:
            messagebox.showerror("Error", "No crop data available!")
            return
        
        crop_scores = []
        for _, crop_row in self.crop_data.iterrows():
            suitability_score = self.calculate_crop_suitability(crop_row, user_inputs)
            if suitability_score > 40:
                crop_scores.append({
                    'name': crop_row['crop_name'],
                    'score': suitability_score,
                    'ph_range': f"{crop_row['ph_min']}-{crop_row['ph_max']}",
                    'moisture_range': f"{crop_row['moisture_min']}-{crop_row['moisture_max']}%",
                    'soil_type': crop_row['soil_type'],
                    'temp_range': f"{crop_row['temperature_min']}-{crop_row['temperature_max']}°C",
                    'rainfall_range': f"{crop_row['rainfall_min']}-{crop_row['rainfall_max']}mm",
                    'season': f"Month {crop_row['month_start']}-{crop_row['month_end']}",
                    'npk': f"N:{crop_row['nitrogen']}, P:{crop_row['phosphorus']}, K:{crop_row['potassium']}"
                })
        
        crop_scores.sort(key=lambda x: x['score'], reverse=True)
        
        self.display_results(crop_scores, user_inputs)
    
    def display_results(self, crop_scores, user_inputs):
        self.results_text.delete("0.0", "end")
        
        if not crop_scores:
            self.results_text.insert("0.0", 
                "❌ No suitable crops found for your current conditions.\n\n"
                "Try adjusting your parameters or consider soil improvement techniques."
            )
            return
        
        result_text = f"🎯 CROP RECOMMENDATIONS\n"
        result_text += f"{'='*60}\n\n"
        result_text += f"📊 YOUR CONDITIONS:\n"
        result_text += f"   • pH Level: {user_inputs['ph']}\n"
        result_text += f"   • Soil Moisture: {user_inputs['moisture']}%\n"
        result_text += f"   • Soil Type: {user_inputs['soil_type']}\n"
        result_text += f"   • Temperature: {user_inputs['temperature']}°C\n"
        result_text += f"   • Expected Rainfall: {user_inputs['rainfall']}mm\n"
        result_text += f"   • Location: {self.location_info['city']}, {self.location_info['country']}\n"
        result_text += f"   • Climate Zone: {self.location_info['climate']}\n\n"
        
        result_text += f"🏆 TOP CROP RECOMMENDATIONS:\n"
        result_text += f"{'-'*60}\n\n"
        
        for i, crop in enumerate(crop_scores[:5], 1):
            if crop['score'] >= 80:
                emoji = "🟢"
            elif crop['score'] >= 60:
                emoji = "🟡"
            else:
                emoji = "🟠"
            
            result_text += f"{emoji} {i}. {crop['name']} - {crop['score']:.1f}% Compatibility\n"
            result_text += f"   ├─ Optimal pH Range: {crop['ph_range']}\n"
            result_text += f"   ├─ Soil Moisture: {crop['moisture_range']}\n"
            result_text += f"   ├─ Preferred Soil: {crop['soil_type']}\n"
            result_text += f"   ├─ Temperature Range: {crop['temp_range']}\n"
            result_text += f"   ├─ Rainfall Requirement: {crop['rainfall_range']}\n"
            result_text += f"   ├─ Growing Season: {crop['season']}\n"
            result_text += f"   └─ Fertilizer Needs (NPK): {crop['npk']}\n\n"
        
        if len(crop_scores) > 5:
            result_text += f"💡 OTHER SUITABLE CROPS ({len(crop_scores) - 5} more):\n"
            result_text += f"{'-'*40}\n"
            for crop in crop_scores[5:]:
                if crop['score'] >= 70:
                    emoji = "🔥"
                elif crop['score'] >= 60:
                    emoji = "⭐"
                else:
                    emoji = "🌱"
                result_text += f"   {emoji} {crop['name']} - {crop['score']:.1f}% compatibility\n"
            result_text += "\n"
        
        result_text += f"📝 IMPORTANT NOTES:\n"
        result_text += f"{'-'*40}\n"
        result_text += f"• Recommendations based on your soil and climate conditions\n"
        result_text += f"• Consider local market demand and crop rotation\n"
        result_text += f"• Seasonal timing is crucial for optimal yields\n"
        result_text += f"• Soil testing recommended for precise pH measurement\n\n"
        result_text += f"🌱 Happy Farming! Choose crops with 70%+ compatibility for best results."
        
        self.results_text.insert("0.0", result_text)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CropPredictorApp()
    app.run()

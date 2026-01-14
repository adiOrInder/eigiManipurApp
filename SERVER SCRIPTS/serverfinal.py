import pandas as pd
import numpy as np
import sqlite3
import os
from flask import Flask, request, jsonify
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from datetime import datetime  # ← ADDED FOR REAL-TIME TRAFFIC

app = Flask(__name__)

# --- CONFIGURATION ---
CSV_FILE = 'ambulance_ml_dataset.csv'
DB_FILE = 'ambulance_data.db'

class IntelligentDispatch:
    def __init__(self, csv_path, db_path):
        self.db_path = db_path
        self.knn = None
        self.rf_classifier = None  # Predicts Type (ALS/BLS/ICU)
        self.eta_regressor = None  # Predicts Time
        self.active_units = None
        self.encoders = {}  # Stores label encoders for strings

        if os.path.exists(csv_path):
            print(f"[SYSTEM] Loading data from {csv_path}...")
            self.df = pd.read_csv(csv_path)
            
            # 1. BUILD SQL DATABASE
            conn = sqlite3.connect(self.db_path)
            self.df.to_sql('ambulances', conn, if_exists='replace', index=False)
            conn.close()
            
            # 2. TRAIN ALL AI MODELS
            self.train_models()
        else:
            print(f"[ERROR] {csv_path} not found.")

    def train_models(self):
        print("[AI] Training Classification & Regression Models...")
        
        # --- MODEL 1: RANDOM FOREST (Predict Ambulance Type) ---
        X_cls = self.df[["age", "oxygen_required", "conscious", "trauma"]]
        y_cls = self.df["ambulance_type"]
        
        self.encoders['type'] = LabelEncoder()
        y_cls_encoded = self.encoders['type'].fit_transform(y_cls)
        
        self.rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.rf_classifier.fit(X_cls, y_cls_encoded)
        
        # --- MODEL 2: LINEAR REGRESSION (Predict ETA) ---
        df_eta = self.df.copy()
        
        self.encoders['traffic'] = LabelEncoder()
        df_eta['traffic_level'] = self.encoders['traffic'].fit_transform(df_eta['traffic_level'])
        
        self.encoders['priority'] = LabelEncoder()
        df_eta['priority'] = self.encoders['priority'].fit_transform(df_eta['priority'])

        X_eta = df_eta[["distance_km", "traffic_level", "priority"]]
        y_eta = df_eta["eta_minutes"]
        
        self.eta_regressor = LinearRegression()
        self.eta_regressor.fit(X_eta, y_eta)
        
        # --- MODEL 3: KNN (Spatial Matching) ---
        available_units = self.df[self.df["available"] == 1]
        coords = np.radians(available_units[["ambulance_lat", "ambulance_lon"]])
        self.knn = NearestNeighbors(n_neighbors=1, metric="haversine")
        self.knn.fit(coords)
        
        print("[AI] All Models (RF, LinReg, KNN) Trained Successfully.")

    def predict_need(self, age, oxy, con, tra):
        prediction_code = self.rf_classifier.predict([[age, oxy, con, tra]])[0]
        return self.encoders['type'].inverse_transform([prediction_code])[0]

    def predict_eta(self, distance, traffic_str="Medium", priority_str="High"):
        try:
            t_code = self.encoders['traffic'].transform([traffic_str])[0] if traffic_str in self.encoders['traffic'].classes_ else 1
            p_code = self.encoders['priority'].transform([priority_str])[0] if priority_str in self.encoders['priority'].classes_ else 1
            
            pred_eta = self.eta_regressor.predict([[distance, t_code, p_code]])[0]
            return max(1, int(pred_eta))
        except:
            return int(distance * 2)

    def find_nearest_smart(self, user_lat, user_lon, needed_type):
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM ambulances WHERE available = 1 AND ambulance_type = ?"
        candidates = pd.read_sql(query, conn, params=(needed_type,))
        conn.close()
        
        if candidates.empty:
            print(f"[WARNING] No {needed_type} available. Switching to ANY closest unit.")
            conn = sqlite3.connect(self.db_path)
            candidates = pd.read_sql("SELECT * FROM ambulances WHERE available = 1", conn)
            conn.close()

        candidate_coords = np.radians(candidates[["ambulance_lat", "ambulance_lon"]])
        temp_knn = NearestNeighbors(n_neighbors=1, metric="haversine")
        temp_knn.fit(candidate_coords)
        
        user_loc = np.radians([[user_lat, user_lon]])
        dist_rad, index = temp_knn.kneighbors(user_loc)
        
        match = candidates.iloc[index[0][0]].to_dict()
        match['distance_km'] = dist_rad[0][0] * 6371
        return match

# --- INITIALIZE SYSTEM ---
dispatch_system = IntelligentDispatch(CSV_FILE, DB_FILE)
current_mission = {}

@app.route('/location', methods=['POST'])
def receive_request():
    global current_mission
    data = request.json
    print(f"\n[INCOMING] New Emergency Request: {data}")

    try:
        # 1. PARSE INPUTS
        lat = float(data.get('lat', 24.8170))
        lon = float(data.get('lon', 93.9368))
        age = int(data.get('age', 30))
        oxy = 1 if data.get('oxygen') == "Yes" else 0
        con = 1 if data.get('conscious') == "Yes" else 0
        tra = 1 if data.get('trauma') == "Yes" else 0

        # 2. AI STEP 1: PREDICT NEED
        needed_type = dispatch_system.predict_need(age, oxy, con, tra)
        print(f"[AI DECISION] Patient Condition suggests: {needed_type}")

        # 3. AI STEP 2: FIND NEAREST MATCH
        match = dispatch_system.find_nearest_smart(lat, lon, needed_type)
        
        # 4. AI STEP 3: PREDICT ETA
        priority = "Critical" if needed_type in ["ICU", "ALS"] else "Medium"
        
        # 🔧 FIXED: Use real current hour for traffic estimation
        current_hour = datetime.now().hour
        traffic = "High" if 17 <= current_hour <= 19 else "Medium"
        
        predicted_eta = dispatch_system.predict_eta(match['distance_km'], traffic, priority)

        # 5. CONSTRUCT RESPONSE
        current_mission = {
            "patient": f"REQ-{np.random.randint(1000,9999)}",
            "assigned_unit": match['ambulance_id'],
            "driver": match.get('driver_name', 'Unknown'),
            "type": match['ambulance_type'],
            "hospital": "RIMS Trauma" if tra else "JNIMS General",
            "pain_level": "CRITICAL" if not con else "STABLE",
            "location": f"{lat:.4f}, {lon:.4f}",
            "eta": predicted_eta,
            "priority": "RED" if priority == "Critical" else "YELLOW",
            "distance": f"{match['distance_km']:.2f} km"
        }
        
        print(f"[DISPATCH] Assigned {match['ambulance_id']} ({match['ambulance_type']}) - ETA: {predicted_eta}m")
        return jsonify({"status": "success", "mission": current_mission})

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"status": "error"}), 500

@app.route('/api/assignments', methods=['GET'])
def send_to_dashboard():
    return jsonify(current_mission)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
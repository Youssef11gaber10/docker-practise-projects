
# 🛻 FoodTrucks Project - Docker Task

This project is a Flask-based web application that displays food truck locations on a map. Your task is to containerize it using Docker and Docker Compose.

---

## 📁 Project Structure

```plaintext
FoodTrucks/
│
├── flask-app/             # Main Flask application
│   ├── app.py             # Flask entry point
│   ├── requirements.txt   # Python dependencies
│   ├── webpack.config.js  # JS bundler config
│   └── static/            # CSS, favicon, icons, etc.
│
├── utils/
│   ├── trucks.geojson     # GeoJSON data for trucks
│   └── generate_geojson.py # GeoJSON utility script
│
├── setup-docker.sh        # Optional helper script
├── shot.png               # Screenshot (preview)
├── README.md              # Original readme
└── .gitignore
```

---

## 🎯 Your Task

### 🚧 Step 1: Create a `Dockerfile` for the Flask App

Inside the `flask-app/` folder, create a `Dockerfile`:


---

### 🧩 Step 2: Create `docker-compose.yml` at the Project Root

At the root level (`FoodTrucks/`), create `docker-compose.yml`:


---

### 🏁 Step 3: Build and Run

In terminal, navigate to the project directory and run:



Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

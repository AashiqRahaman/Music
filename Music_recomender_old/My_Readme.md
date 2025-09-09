## Quick Setup

#   Setup Venv For no Contradiction  
```bash
python -m venv My_music
```
#
```bash
My_music\Scripts\activate
```

#   Install dependencies: 
```bash
pip install pandas numpy scikit-learn flask flask-cors joblib
```

#   Place dataset files in `Data Set/` folder

#    Train model: 
```bash
python train_model.py
```

#   Run app: 
```bash
python app.py
```
#   Open to check `http://localhost:5000`
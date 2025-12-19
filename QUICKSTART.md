# 🏁 Quick Start Guide

## Installation & Setup

### Step 1: Install Dependencies
```bash
pip install fastapi uvicorn fastf1 pandas numpy --break-system-packages
```

### Step 2: Start the Application

**Option A: Using the start script (easiest)**
```bash
cd f1-sculpture
./start.sh
```

**Option B: Manual start**

Terminal 1 - Backend:
```bash
cd f1-sculpture/backend
python main.py
```

Terminal 2 - Frontend:
```bash
cd f1-sculpture/frontend
python -m http.server 3000
```

### Step 3: Open in Browser
Navigate to: `http://localhost:3000`

## 🎮 Using the Application

1. **Select Year**: Start with 2024 for recent data
2. **Choose Grand Prix**: Monaco, Silverstone, Monza are great choices
3. **Pick Session**: Qualifying (Q) usually has the best data
4. **Select Driver**: Try VER (Verstappen), HAM (Hamilton), or LEC (Leclerc)
5. **Click "Generate Sculpture"**: Wait 20-30 seconds for first-time data download

### Mouse Controls
- **Left Click + Drag**: Rotate the sculpture
- **Right Click + Drag**: Pan the view
- **Scroll Wheel**: Zoom in/out
- **Reset Camera**: Button to return to default view

## 💡 Tips

- **First load is slow**: FastF1 downloads and caches data (~30-60 seconds)
- **Subsequent loads are fast**: Cached data loads in 2-3 seconds
- **Try different drivers**: Each has a unique "sculpture signature"
- **Compare sessions**: See how drivers improve from FP1 to Qualifying

## 🐛 Troubleshooting

**Backend won't start**
- Make sure port 8000 is free: `lsof -i :8000`
- Check if dependencies installed: `pip list | grep fastf1`

**No data for a session**
- Not all sessions have telemetry (especially older races)
- Try a different session or race

**Sculpture looks flat**
- This can happen with street circuits (Monaco)
- Try a high-speed circuit like Monza or Spa

## 🎯 Recommended First Sculptures

1. **Max Verstappen - 2024 Monaco - Qualifying**
   - Technical circuit, shows precision

2. **Lewis Hamilton - 2024 Silverstone - Qualifying**
   - Fast, flowing corners, great G-forces

3. **Charles Leclerc - 2024 Monza - Qualifying**
   - High-speed straights and heavy braking

## 🚀 What's Next?

Check out `README.md` for:
- Full API documentation
- Architecture details
- Future enhancement ideas
- How to contribute

---

**Enjoy exploring F1 data in a whole new dimension!** 🏎️✨

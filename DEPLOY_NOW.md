# 🚀 ΓΡΗΓΟΡΟΣ ΟΔΗΓΟΣ DEPLOYMENT (15 λεπτά)

## Έχετε ΗΔΗ έτοιμα:
- ✅ Dockerfile
- ✅ docker-compose.yml
- ✅ render.yaml
- ✅ .dockerignore
- ✅ Procfile (backup)

## ΒΗΜΑ 1: Test Locally (Προαιρετικό - 3 λεπτά)

Αν έχετε Docker εγκατεστημένο:

```bash
cd /Users/ioannapappa/Documents/Projects/Unintend_backend

# Build
docker build -t unintend-backend .

# Run
docker run -p 8000:8000 unintend-backend

# Test στο browser: http://localhost:8000/
```

## ΒΗΜΑ 2: Push στο GitHub (5 λεπτά)

```bash
cd /Users/ioannapappa/Documents/Projects/Unintend_backend

# Initialize git (αν δεν έχετε)
git init
git add .
git commit -m "Ready for deployment with Docker"

# Δημιουργήστε repo στο GitHub:
# 1. Πηγαίνετε στο github.com
# 2. New Repository → "Unintend_backend"
# 3. Κάντε το Public ή Private (και τα δύο δουλεύουν)
# 4. ΜΗΝ προσθέσετε README/gitignore (έχετε ήδη)

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/Unintend_backend.git
git branch -M main
git push -u origin main
```

**Αντικαταστήστε `YOUR_USERNAME` με το GitHub username σας!**

## ΒΗΜΑ 3: Deploy στο Render (5 λεπτά)

### Option A: Blueprint (Αυτόματο - ΣΥΝΙΣΤΑΤΑΙ)

1. Πηγαίνετε στο **https://render.com**
2. Sign up / Log in (με GitHub - NO credit card needed!)
3. **Dashboard** → **"New +"** → **"Blueprint"**
4. **Connect** το `Unintend_backend` repository
5. Render θα διαβάσει το `render.yaml` αυτόματα
6. **Click "Apply"**
7. Περιμένετε 3-5 λεπτά...
8. ✅ Θα πάρετε URL: `https://unintend-backend-XXXX.onrender.com`

### Option B: Manual Web Service

1. Πηγαίνετε στο **https://render.com**
2. **Dashboard** → **"New +"** → **"Web Service"**
3. **Connect** το GitHub repo
4. Συμπληρώστε:
   - **Name:** `unintend-backend`
   - **Region:** Frankfurt (ή Oregon)
   - **Branch:** `main`
   - **Runtime:** **Docker** (σημαντικό!)
   - **Dockerfile Path:** `./Dockerfile`
   - **Plan:** Free
5. **Advanced:**
   - Add Disk:
     - **Name:** `unintend-data`
     - **Mount Path:** `/app`
     - **Size:** 1 GB
6. **Create Web Service**
7. Περιμένετε το build...

## ΒΗΜΑ 4: Πάρτε το URL & Test (2 λεπτά)

Μόλις ολοκληρωθεί το deploy:

1. **Copy** το URL: `https://unintend-backend-XXXX.onrender.com`
2. **Test** στο browser - θα δείτε:
   ```json
   {"ok": true, "service": "UnIntend Backend"}
   ```
3. **Test login endpoint:**
   ```
   https://unintend-backend-XXXX.onrender.com/api/auth/login
   ```

## ΒΗΜΑ 5: Rebuild Flutter APK (3 λεπτά)

```bash
cd /Users/ioannapappa/Documents/Projects/UnIntend-project

flutter build apk --release \
  --dart-define=API_BASE_URL=https://unintend-backend-XXXX.onrender.com
```

**Αντικαταστήστε το XXXX με το πραγματικό URL σας!**

Νέο APK: `build/app/outputs/flutter-apk/app-release.apk`

## ΒΗΜΑ 6: Test Τελικό APK (5 λεπτά)

1. Install APK σε emulator/συσκευή
2. Περιμένετε ~30 δευτερόλεπτα (backend wakeup - πρώτη φορά)
3. Login: `eleni@example.com` / `pass1234`
4. Ελέγξτε:
   - ✅ Feed φορτώνει
   - ✅ Messages δουλεύουν
   - ✅ Profile εμφανίζεται

## ΤΕΛΟΣ! 🎉

Τώρα έχετε:
- ✅ Backend deployed & running 24/7
- ✅ Production APK ready
- ✅ Απλή εγκατάσταση για αξιολογητές

## Επόμενο: Update README

1. Ανοίξτε: `/Users/ioannapappa/Documents/Projects/ΠΑΡΑΔΟΣΗ_README.md`
2. Αντικαταστήστε:
   - Line ~36: `https://unintend-backend-XXXX.onrender.com` → Το δικό σας URL
3. Save as `README.md` για παράδοση

---

## Troubleshooting

### "Build failed on Render"
- Ελέγξτε Logs στο Render Dashboard
- Βεβαιωθείτε ότι το `requirements.txt` είναι σωστό
- Κοιτάξτε για typos στο Dockerfile

### "Service starts but crashes"
- Δείτε Runtime Logs στο Render
- Ελέγξτε ότι το `PORT` env variable χρησιμοποιείται

### "Can't connect from APK"
- Βεβαιωθείτε ότι κάνατε rebuild με το σωστό URL
- Ελέγξτε CORS settings (ήδη OK στο `app/main.py`)
- Περιμένετε 30 δευτερόλεπτα για wakeup

---

## Εναλλακτικά Platforms (αν Render δεν δουλεύει)

### Railway.app
```bash
# Install CLI
npm i -g @railway/cli

# Login & deploy
railway login
railway init
railway up
```

### Fly.io
```bash
# Install CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

Όλα χρησιμοποιούν το ίδιο Dockerfile! ✨

---

**Το backend URL σας θα μείνει active μέχρι 7/2/2026 (free tier).**

**ΜΗ σβήσετε το Render service πριν την αξιολόγηση!**

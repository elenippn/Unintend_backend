# Hosting Guide (Backend)

Στόχος: να πάρεις ένα σταθερό public URL (π.χ. `https://unintend-backend.onrender.com`) ώστε να χτίσεις release APK που δουλεύει παντού.

## Επιλογή 1: Render (εύκολη)

1) Κάνε push το project σε GitHub (ή ανέβασε σε repo).
2) Στο Render: **New +** → **Web Service** → σύνδεσε το repo.
3) Επειδή υπάρχει `render.yaml` + `Dockerfile`, το Render θα το σηκώσει ως Docker service.
4) Περιμένε να κάνει deploy και πάρε το URL.
5) Health check: `GET /` πρέπει να επιστρέφει `{"ok": true, ...}`.

Σημείωση: Η SQLite βάση είναι μέσα στο container (demo-friendly). Σε redeploy μπορεί να γίνει reset. Για αξιολόγηση είναι ΟΚ γιατί το seed τρέχει στο startup.

## Build APK με hosted URL
Από `my_app/`:

```powershell
flutter build apk --release --dart-define=API_BASE_URL=https://<your-render-service>.onrender.com
```

## Επιλογή 2: Local + Emulator (χωρίς hosting)
- Τρέχεις backend στον υπολογιστή.
- Emulator: το app μιλάει στο `http://10.0.2.2:8000`.

## Troubleshooting
- Αν σε φυσική συσκευή δεν συνδέεται: χρειάζεσαι public URL ή PC IP + `--host 0.0.0.0`.
- Αν το hosted URL είναι HTTPS, όλα καλά.
- Αν είναι HTTP, στο Android χρειάζεται cleartext (έχει ενεργοποιηθεί στο manifest).

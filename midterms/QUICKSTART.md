# Quick Start Guide - Rule-Based Translation System

## 🚀 Start in 3 Steps

### 1. Install Dependencies (One-time)
```bash
cd /Users/lestat/Documents/Projects/NLP/midterm/Pangasinense_NLP/midterms
pip install fastapi uvicorn pydantic requests
```

### 2. Start the API
```bash
./start_rule_api.sh
```
Or:
```bash
python3 rule_based_api.py
```

### 3. Open Web Interface
Double-click: `translator.html`

Then:
- ✅ Check "Use Rule-Based API"
- ✅ Check "Show Rules" (optional)
- ✅ Enter Pangasinan text
- ✅ Click "Translate ▶"

---

## 📖 Example Translations

| Pangasinan | English | Rules Applied |
|------------|---------|---------------|
| `abung` | house | direct_lookup |
| `mangan` | to eat | prefix_man |
| `abung ko` | house my | direct_lookup, enclitic_ko |
| `tuboan` | place of growth | suffix_an |
| `ed Manila` | at Manila | particle |

---

## 🔍 API Endpoints

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Translate:**
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "mangan ko", "show_rules": true}'
```

**Get Rules:**
```bash
curl http://localhost:8000/rules
```

**Analyze Word:**
```bash
curl -X POST "http://localhost:8000/analyze?word=mangan"
```

**API Docs:**
Open in browser: `http://localhost:8000/docs`

---

## 🧪 Test Everything

```bash
python3 test_rule_api.py
```

---

## ❓ Troubleshooting

**API won't start?**
- Check port 8000 is free: `lsof -i :8000`
- Install dependencies: `pip install fastapi uvicorn pydantic`

**Web interface can't connect?**
- Verify API is running: `curl http://localhost:8000/health`
- Check URL is correct: `http://localhost:8000`

**No translation results?**
- Check "Use Rule-Based API" is checked
- Look at browser console (F12) for errors
- Verify API status in the banner at top

---

## 📊 For Presentation

1. Start API: `./start_rule_api.sh`
2. Open `translator.html`
3. Open API docs: `http://localhost:8000/docs`
4. Enable "Show Rules" checkbox
5. Try these demos:
   - `abung` → "house"
   - `mangan` → "to eat" (shows prefix rule)
   - `abung ko` → "house my" (shows enclitic)
   - `tuboan` → "place of growth" (shows suffix)

---

## 🎯 Why Rule-Based?

✅ **Explainable** - Shows exact rules  
✅ **Fast** - No training needed  
✅ **Linguistically valid** - Based on real grammar  
✅ **Transparent** - Can debug easily  
✅ **Educational** - Great for teaching  

---

## 📁 Key Files

- `rule_based_api.py` - Main API server
- `translator.html` - Web interface (in parent folder)
- `README_RULE_BASED.md` - Full documentation
- `PRESENTATION_GUIDE.md` - Presentation tips
- `test_rule_api.py` - Test suite
- `start_rule_api.sh` - Startup script

---

## 🆘 Emergency Backup

If API fails during demo:
1. Uncheck "Use Rule-Based API" in web interface
2. Continue with dictionary-only mode
3. Explain: "Normally the rule-based API provides morphological analysis..."

---

**Need help? Check:**
- `README_RULE_BASED.md` for full docs
- `PRESENTATION_GUIDE.md` for presentation tips
- API docs at `http://localhost:8000/docs`

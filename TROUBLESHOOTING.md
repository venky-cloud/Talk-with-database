# Troubleshooting: Backend Not Fetching Details

## ✅ Backend Status: WORKING

The backend API is working correctly:
- ✅ Backend server is running on port 8000
- ✅ Database connection is working
- ✅ Schema endpoint returns data successfully
- ✅ API responds with: `{"db": "talkwithdata", "tables": [], ...}`

## 🔍 Frontend Issues to Check

### 1. Check Frontend API Configuration

**Location:** `project/src/lib/api.ts`

The frontend uses:
```typescript
export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
```

**Solution:** Create `project/.env` file:
```env
VITE_API_BASE=http://127.0.0.1:8000
```

Or ensure frontend uses `http://localhost:8000` (both should work).

### 2. Check Browser Console

Open browser DevTools (F12) and check:
- **Console tab:** Look for errors like:
  - `Failed to fetch`
  - `CORS error`
  - `Network error`
  - `POST /schema/inspect failed: ...`

- **Network tab:** 
  - Look for requests to `/schema/inspect`
  - Check if they're failing (red status)
  - Check the error message

### 3. Verify Frontend is Running

```bash
cd project
npm run dev
```

Should show something like:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

### 4. Test API from Browser Console

Open browser console on your frontend page and run:
```javascript
fetch('http://127.0.0.1:8000/schema/inspect', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({db_type: 'mysql'})
})
.then(r => r.json())
.then(console.log)
.catch(console.error)
```

If this works, the issue is in the frontend code.
If this fails, there's a network/CORS issue.

### 5. Common Issues

#### Issue: CORS Error
**Error:** `Access to fetch at 'http://127.0.0.1:8000/...' from origin 'http://localhost:5173' has been blocked by CORS policy`

**Solution:** Backend already has CORS enabled. If still failing:
- Check `backend/fastapi_app/main.py` has CORS middleware
- Restart backend server

#### Issue: Network Error
**Error:** `Failed to fetch` or `NetworkError`

**Solution:**
- Ensure backend is running: `uvicorn fastapi_app.main:app --reload --port 8000`
- Check firewall isn't blocking port 8000
- Try `http://localhost:8000` instead of `http://127.0.0.1:8000`

#### Issue: Wrong API URL
**Error:** `POST http://localhost:8000/schema/inspect failed: 404`

**Solution:**
- Verify backend is running on port 8000
- Check `VITE_API_BASE` in frontend `.env` file
- Restart frontend dev server after changing `.env`

### 6. Quick Test Commands

**Test backend directly:**
```bash
cd backend
python test_api_endpoints.py
```

**Test database connection:**
```bash
cd backend
python check_mysql_status.py
```

**Test schema endpoint:**
```bash
cd backend
python test_schema_endpoint.py
```

## 📋 Current Configuration

- **Backend URL:** `http://127.0.0.1:8000`
- **Database:** `talkwithdata` on port `3306`
- **Database Status:** Connected, but empty (no tables)

## 🎯 Next Steps

1. **Check browser console** for specific error messages
2. **Verify frontend is running** and can reach backend
3. **Test API from browser console** (see step 4 above)
4. **Check Network tab** in DevTools for failed requests
5. **Share the specific error message** you see in the browser

The backend is working - the issue is likely in the frontend connection or configuration.

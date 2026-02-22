# 🚀 AdForge React Frontend - Quick Start Guide

## Step 1: Navigate to Frontend Directory

```bash
cd frontend-react
```

## Step 2: Install Dependencies

```bash
npm install
```

This will install:

- React 18.2.0
- TypeScript 5.0.2
- Vite 5.0.0
- Framer Motion 11.0.0 (for enhanced animations)
- All dev dependencies

## Step 3: Start Development Server

```bash
npm run dev
```

The app will start at **<http://localhost:3000>**

## Step 4: Ensure Backend is Running

Make sure your FastAPI backend is running at **<http://localhost:8000>**

```bash
# In the parent directory
python -m uvicorn backend.main:app --reload --port 8000
```

## 🎉 That's it

Your React frontend is now running and connected to the backend!

## 📋 Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

## 🎨 What's Different from the HTML Version?

### ✅ Improvements

1. **Component Architecture**: Modular, reusable components
2. **Type Safety**: Full TypeScript coverage prevents bugs
3. **Better State Management**: React hooks for clean state handling
4. **Enhanced Animations**: Smooth transitions and effects
5. **Development Experience**: Hot Module Replacement (instant updates)
6. **Production Ready**: Optimized builds with code splitting
7. **Maintainability**: Easy to extend and modify
8. **Testing Ready**: Can easily add Jest/React Testing Library

### 🔥 New Features

- **Auto-scroll to results**: Automatically scrolls when results appear
- **Enhanced copy feedback**: Visual confirmation when copying content
- **Better error handling**: More informative error messages
- **Improved accessibility**: Better keyboard navigation and ARIA labels
- **Performance**: Optimized re-renders with React.memo and useCallback

### 🎯 All Original Features Preserved

✓ Dark cyber theme with gradient backgrounds
✓ Server connection indicator with blinking dot
✓ Product information form with all fields
✓ Drag-and-drop image upload with previews
✓ Toggle switches for scraper and RAG
✓ Real-time pipeline progress tracker
✓ Streaming logs with color-coded levels
✓ Complete results display (hook, caption, CTA, insights, strategy, JSON)
✓ Copy buttons for all sections
✓ Responsive design
✓ All animations and hover effects

## 🔧 Customization

### Change Default Backend URL

Edit `src/App.tsx`:

```typescript
const [serverBase, setServerBase] = useState('http://your-backend-url:8000');
```

### Modify Theme Colors

Edit `src/index.css`:

```css
:root {
  --accent: #6c63ff;  /* Change primary color */
  --accent2: #ff6584; /* Change secondary color */
  --accent3: #43e97b; /* Change success color */
}
```

### Add More Components

Create new components in `src/components/` following the existing pattern:

- `ComponentName.tsx` for the component
- `ComponentName.module.css` for styles

## 🐛 Common Issues

### Port 3000 already in use?

Change the port in `vite.config.ts`:

```typescript
server: { port: 3001 }
```

### TypeScript errors?

Run:

```bash
npm install
```

### Backend connection failed?

Check that:

1. Backend is running at <http://localhost:8000>
2. No CORS issues (backend should allow origin)
3. API endpoints match (`/api/pipeline/generate/stream`)

## 📱 Mobile Support

The React app is fully responsive and works great on:

- Desktops
- Tablets
- Mobile phones

## 🎓 Learning Resources

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)

## 💡 Pro Tips

1. **Use React DevTools**: Install the Chrome extension for debugging
2. **Component Inspector**: Right-click → Inspect → Components tab
3. **Network Tab**: Check SSE streaming events in DevTools → Network
4. **Console Logs**: Watch for any warnings or errors
5. **Fast Refresh**: Edit code and see instant updates (no refresh needed!)

Enjoy your modern React frontend! 🎉

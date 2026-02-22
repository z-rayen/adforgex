# AdForge React Frontend

Modern React + TypeScript frontend for AdForge AI pipeline.

## ✨ Features

- **Modern Stack**: React 18, TypeScript, Vite
- **Real-time Updates**: SSE (Server-Sent Events) streaming for live pipeline progress
- **Drag & Drop**: Upload competitor images with preview
- **Responsive Design**: Works on all screen sizes
- **Dark Theme**: Cyber-aesthetic with smooth animations
- **Component Architecture**: Modular, reusable components with CSS modules
- **Type Safety**: Full TypeScript coverage

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ or higher
- npm or yarn

### Installation

```bash
# Navigate to the frontend-react directory
cd frontend-react

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Building for Production

```bash
# Build the app
npm run build

# Preview the production build
npm run preview
```

The build output will be in the `dist/` directory.

## 📁 Project Structure

```
frontend-react/
├── src/
│   ├── components/         # React components
│   │   ├── Header.tsx
│   │   ├── Card.tsx
│   │   ├── ConfigCard.tsx
│   │   ├── ProductForm.tsx
│   │   ├── ImageUploadCard.tsx
│   │   ├── PipelineTracker.tsx
│   │   ├── LogPanel.tsx
│   │   ├── Results.tsx
│   │   └── *.module.css    # Component styles
│   ├── App.tsx             # Main application
│   ├── App.module.css
│   ├── types.ts            # TypeScript definitions
│   ├── index.css           # Global styles
│   └── main.tsx            # Entry point
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 🎨 Component Overview

### Header

Displays app title, subtitle, and server connection status with animated indicator.

### ConfigCard

Server configuration with backend URL and optional API key override.

### ProductForm

Product information input (description, category, audience, messaging angle).

### ImageUploadCard

Drag-and-drop image upload with preview thumbnails and toggle switches for scraper/RAG options.

### PipelineTracker

Visual progress tracker showing 6 pipeline steps with active/done/error states.

### LogPanel

Real-time streaming logs with timestamps and color-coded log levels.

### Results

Beautiful display of generated ad content including hook, caption, CTA, visual recommendations, user insights, strategy, and raw JSON.

## 🔧 Configuration

The frontend expects the backend API to be running at `http://localhost:8000` by default. You can change this in the UI or modify the default in `App.tsx`.

### Proxy Configuration

Vite is configured with a proxy to forward `/api/*` requests to the backend:

```typescript
// vite.config.ts
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

## 🎯 Key Features Implementation

### Real-time Streaming

Uses Server-Sent Events (SSE) for real-time pipeline updates. The `runPipeline` function in `App.tsx` handles streaming events and updates UI in real-time.

### State Management

Uses React hooks (useState, useCallback, useEffect) for efficient state management without external libraries.

### Image Handling

Converts uploaded images to base64 for easy transmission to the backend API.

### Responsive Design

CSS Grid and Flexbox ensure the app works beautifully on all screen sizes.

### Animations

Smooth CSS animations using keyframes for fade-in, slide-in, and pulse effects.

## 🔒 Type Safety

All components are fully typed with TypeScript:

- `types.ts` contains all interface definitions
- Props are strictly typed
- API responses are typed
- Event handlers are typed

## 🎨 Styling

Uses CSS Modules for scoped styling:

- Global styles in `index.css`
- Component-specific styles in `*.module.css`
- CSS custom properties for theming
- No external CSS libraries (pure CSS)

## 🌐 Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## 📝 Development Tips

1. **Hot Module Replacement**: Vite provides instant HMR during development
2. **TypeScript Checking**: Run `tsc --noEmit` to check for type errors
3. **Linting**: Run `npm run lint` to check for code issues
4. **Component Development**: Each component is self-contained with its own styles

## 🚀 Deployment

### Static Hosting (Recommended)

Build the app and deploy the `dist/` folder to any static hosting service:

- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

### Docker

You can also containerize the React app with nginx:

```dockerfile
FROM node:18 as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🐛 Troubleshooting

### Port Already in Use

Change the port in `vite.config.ts`:

```typescript
server: { port: 3001 }
```

### Backend Connection Issues

Ensure the backend is running at the configured URL (default: `http://localhost:8000`)

### TypeScript Errors

Run `npm install` to ensure all type definitions are installed

## 📄 License

Same license as the parent AdForge project.

## 🤝 Contributing

Feel free to submit issues and pull requests!

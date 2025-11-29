# Character Portrait Generator - Frontend

A SvelteKit-based web application for creating customizable character portraits using layered PNG assets.

## Features

- **Real-time Portrait Rendering**: Canvas-based layering system with 21 different layers
- **Character Customization**: Mix and match facial features, hairstyles, and accessories
- **Random Generation**: One-click randomization for quick character creation
- **Export Functionality**: Download portraits as PNG images
- **Responsive Design**: Works on desktop and mobile devices

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Asset Structure

The application uses 193+ PNG sprites organized into 21 layers:
- Layer 20: Background
- Layer 19: Clothes Back
- Layer 18: Hair Back
- ... (continuing through all facial features)
- Layer 0: Front Accessories

All assets are loaded from `/static/PortraitSprites/` and rendered in order from back to front.

## Technical Implementation

- **SvelteKit**: Framework for the web application
- **HTML5 Canvas**: For real-time portrait compositing
- **Responsive Design**: CSS Grid and Flexbox for layout
- **Asset Caching**: Images are preloaded and cached for performance
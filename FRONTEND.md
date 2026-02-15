# Frontend Features

## Overview
Modern, dark-themed single-page application for analyzing GitHub repositories.

## Design
- **Theme**: Dark blue gradient background with indigo accents
- **Typography**: System fonts with monospace for code
- **Animations**: Smooth fade-in/fade-out transitions
- **Responsive**: Works on desktop and mobile

## Features

### 1. Repository Input
- Clean input field with URL validation
- Gradient button with hover effects
- Loading state with spinner animation
- Form submission via Enter key

### 2. Analysis Results Display
- **Info Cards Grid**:
  - Repository name (extracted from URL)
  - Framework badge (color-coded)
  - Total file count
  - Analysis timestamp

- **Source Files Section**:
  - Scrollable list (max 400px)
  - Each file shows:
    - Full relative path (monospace)
    - Language badge
    - File size (formatted: KB, MB, GB)
  - Hover effects with slide animation
  - Alphabetically sorted

- **Dependency Graph Section**:
  - Shows files with dependencies only
  - Tree structure visualization
  - Arrow indicators for dependencies
  - Collapsible/scrollable (max 400px)

- **Language Distribution Chart**:
  - Canvas-based horizontal bar chart
  - Top 10 languages
  - Color-coded bars
  - Shows file count per language
  - Responsive sizing

### 3. Error Handling
- Red error banner with icon
- Clear error messages from API
- Auto-retry on network issues

### 4. User Experience
- Smooth scroll to results
- Close button to hide results
- Loading indicators during analysis
- Disabled state during processing

## Color Palette
```
Background Primary:   #0a0e27
Background Secondary: #151933
Background Tertiary:  #1e2347
Accent Primary:       #6366f1 (Indigo)
Accent Secondary:     #818cf8 (Light Indigo)
Text Primary:         #e2e8f0
Text Secondary:       #94a3b8
Success:              #10b981
Error:                #ef4444
Border:               #2d3250
```

## Technology Stack
- **HTML5**: Semantic markup
- **CSS3**: Modern features (Grid, Flexbox, Custom Properties)
- **Vanilla JavaScript**: No frameworks, pure ES6+
- **Canvas API**: For chart rendering

## Browser Support
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Performance
- No external dependencies
- Minimal file sizes:
  - HTML: ~3KB
  - CSS: ~10KB
  - JS: ~8KB
- Fast page loads
- Efficient DOM updates

## Accessibility
- Semantic HTML elements
- Form validation
- Keyboard navigation support
- Clear error messages
- High contrast text

## Future Enhancements
- [ ] Interactive dependency graph visualization (D3.js)
- [ ] Code preview on file click
- [ ] Search/filter files
- [ ] Export results as JSON/PDF
- [ ] Dark/light theme toggle
- [ ] Bookmarkable analysis results
- [ ] Share results via URL

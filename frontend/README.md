# Health AI Consultant Frontend

This is the React frontend for the Health AI Consultant application. It provides a user-friendly interface for interacting with the RAG-powered health consultation chatbot.

## Features

- Interactive chat interface with markdown rendering
- Document upload functionality for PDF files
- Real-time message sending and receiving
- Citation display for sources used in responses
- Responsive design for all device sizes

## Project Structure

```
frontend/
├── public/              # Public assets
├── src/
│   ├── components/      # React components
│   │   ├── ChatInput.jsx
│   │   ├── ChatPage.jsx
│   │   ├── ChatWindow.jsx
│   │   ├── DocumentUpload.jsx
│   │   ├── Header.jsx
│   │   ├── MessageBubble.jsx
│   │   └── UploadPage.jsx
│   ├── services/        # API services
│   │   └── apiService.js
│   ├── hooks/           # Custom React hooks
│   ├── App.jsx          # Main application component
│   ├── index.css        # Global styles
│   └── main.jsx         # Application entry point
├── .env                 # Environment variables
├── package.json         # Dependencies and scripts
├── postcss.config.js    # PostCSS configuration
├── tailwind.config.js   # Tailwind CSS configuration
└── vite.config.js       # Vite configuration
```

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Backend server running at http://localhost:5000

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env` file in the root directory with the following content:
   ```
   VITE_API_URL=http://localhost:5000/api
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to http://localhost:3000

## Building for Production

```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.

## Technologies Used

- React 18
- React Router v6
- Tailwind CSS
- Vite
- Axios for API requests
- React Markdown for rendering markdown content

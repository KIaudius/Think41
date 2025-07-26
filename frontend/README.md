# Think41 Frontend - AI Chat Application

This is the frontend React application for the Think41 AI Chat system. It provides a modern, responsive chat interface with conversation history and state management.

## Features

### Milestone 6: UI Component Development ✅
- **ChatWindow**: Primary container orchestrating the entire chat interface
- **MessageList**: Component responsible for rendering a list of messages
- **Message**: Component for single messages, styled to differentiate between user and AI
- **UserInput**: Controlled form with text input and 'Send' button

### Milestone 7: Client-Side State Management ✅
- **Context API**: Implemented state management using React Context API
- **State Management**: Handles message list, loading status, and user input value
- **Redux-like Pattern**: Uses useReducer for predictable state updates

### Milestone 8: Conversation History Panel ✅
- **Side Panel**: Displays past conversations in a side panel within ChatWindow
- **Conversation Selection**: Users can click on past sessions to load history
- **New Conversation**: Button to start fresh conversations

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start the Development Server**:
   ```bash
   npm start
   ```

3. **Ensure Backend is Running**:
   Make sure the backend server is running on `http://localhost:5000`

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── ChatWindow.js      # Main chat container
│   │   ├── MessageList.js     # Message list component
│   │   ├── Message.js         # Individual message component
│   │   ├── UserInput.js       # Input form component
│   │   └── ConversationHistory.js # Conversation history panel
│   ├── context/
│   │   └── ChatContext.js     # State management context
│   ├── services/
│   │   └── api.js            # API service functions
│   ├── App.js                # Main app component
│   ├── App.css               # Main styles
│   ├── index.js              # App entry point
│   └── index.css             # Global styles
├── package.json
└── README.md
```

## State Management

The application uses React Context API with useReducer for state management:

- **Messages**: Array of chat messages
- **Loading**: Boolean for loading states
- **User Input**: Current input value
- **Current Session**: Active conversation session ID
- **Conversations**: List of past conversations

## API Integration

The frontend communicates with the backend through the `api.js` service:

- **Chat API**: Send messages, get conversations, load messages
- **Memory API**: Search memory, get memory stats
- **Error Handling**: Comprehensive error handling with user feedback

## Styling

- **Modern Design**: Clean, modern UI with smooth animations
- **Responsive**: Works on desktop and mobile devices
- **Accessibility**: Proper focus states and keyboard navigation
- **Loading States**: Visual feedback during API calls

## Usage

1. **Start a New Conversation**: Click the "New" button in the conversation panel
2. **Send Messages**: Type in the input field and press Enter or click Send
3. **View History**: Click on any conversation in the side panel to load its history
4. **Real-time Updates**: Messages are sent to the AI and responses are displayed

## Development

- **Hot Reload**: Changes are reflected immediately during development
- **Error Boundaries**: Graceful error handling throughout the app
- **Console Logging**: Detailed logging for debugging
- **Proxy Configuration**: Automatic proxy to backend during development

## Testing

The application includes comprehensive error handling and loading states for a smooth user experience. 
# Vikki ChatBot - Frontend with Prompt Management

A modern, responsive chatbot frontend - Vikki ChatBot, built with React, TypeScript, and Tailwind CSS. Now featuring comprehensive **Prompt Management** capabilities for AI agents.

## 🚀 New Features - Prompt Management

### ✨ Advanced Prompt System
- 📝 **Create & Edit Prompts** - Build reusable prompt templates with variables
- 🏷️ **Categorization** - Organize prompts by category (General, Coding, Creative, Analysis, etc.)
- 🔍 **Smart Search & Filter** - Find prompts quickly with search and category filters
- 📊 **Usage Analytics** - Track which prompts are most effective
- 🎯 **Template Variables** - Dynamic prompts with `{variable_name}` placeholders
- 🏃‍♂️ **Quick Access** - One-click prompt insertion from chat interface

### 📋 Prompt Categories
- **General** - All-purpose prompts for various tasks
- **Coding** - Programming assistance, code review, debugging
- **Creative** - Writing, brainstorming, content creation
- **Analysis** - Data analysis, research, insights
- **Conversation** - Chat enhancement, role-playing
- **Custom** - User-defined specialized prompts

## Features

- 🤖 **Modern Chat Interface** - Clean, intuitive design for Vikki ChatBot
- 💬 **Real-time Messaging** - Smooth chat experience with typing indicators
- 📱 **Responsive Design** - Works perfectly on desktop and mobile
- 🎨 **Beautiful UI** - Modern design with dark/light theme support
- 📁 **Session Management** - Multiple chat sessions with sidebar navigation
- ⚡ **Fast Performance** - Built with Vite for lightning-fast development
- 🔌 **Backend Ready** - Easy integration with your Python backend
- 🧠 **Prompt Management** - Complete prompt lifecycle management
- 🎯 **Template System** - Dynamic prompts with variable substitution

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Lucide React** for beautiful icons
- **Framer Motion** for smooth animations

## Getting Started

### Prerequisites

- Node.js (version 16 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:3000`

### Building for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── components/           # React components
│   ├── ui/              # Reusable UI components
│   │   ├── Button.tsx   # Button component
│   │   ├── Input.tsx    # Input component
│   │   ├── Textarea.tsx # Textarea component
│   │   ├── Select.tsx   # Select dropdown
│   │   └── Badge.tsx    # Badge/tag component
│   ├── ChatArea.tsx     # Main chat interface
│   ├── ChatInput.tsx    # Message input with prompt integration
│   ├── MessageBubble.tsx # Individual message display
│   ├── Sidebar.tsx      # Session & prompt management sidebar
│   ├── TypingIndicator.tsx # Typing animation
│   ├── PromptManager.tsx   # Main prompt management interface
│   ├── PromptForm.tsx      # Create/edit prompt form
│   └── PromptCard.tsx      # Individual prompt display
├── types/               # TypeScript type definitions
│   ├── chat.ts          # Chat-related types
│   └── prompt.ts        # Prompt management types
├── lib/                 # Utility functions
│   ├── api.ts          # Chat API integration
│   ├── promptAPI.ts    # Prompt management API
│   └── utils.ts        # Helper utilities
├── App.tsx             # Main application component
├── main.tsx            # Application entry point
└── index.css           # Global styles and Tailwind imports
```

## Prompt Management Usage

### Creating Prompts

1. **Access Prompt Manager** - Click the "Prompts" tab in the sidebar
2. **Create New Prompt** - Click "New Prompt" button
3. **Fill Details**:
   - **Name**: Descriptive name for your prompt
   - **Category**: Select appropriate category
   - **Description**: Brief explanation of the prompt's purpose
   - **Content**: The actual prompt text with variables like `{variable_name}`
   - **Tags**: Add searchable tags
   - **Active**: Toggle prompt availability

### Using Prompts

1. **From Chat Input** - Click the ✨ sparkles icon to open prompt selector
2. **Quick Selection** - Browse and click any prompt to insert it
3. **Variable Substitution** - Replace `{variable_name}` placeholders with actual values
4. **Send Message** - The prompt is ready to use with your AI agent

### Example Prompts

```
Name: Code Review Assistant
Category: Coding
Content: You are a senior software engineer. Review this code and provide feedback on:

1. Code quality and best practices
2. Potential bugs or issues  
3. Performance optimizations
4. Readability improvements

Code to review:
{code}

Additional context: {context}
```

```
Name: Creative Writing Helper  
Category: Creative
Content: You are a creative writing assistant. Help me with my {writing_type} by:

1. Providing creative suggestions
2. Improving narrative flow
3. Enhancing character development
4. Suggesting plot improvements

Topic: {topic}
Genre: {genre}
Target audience: {audience}
```

## Backend Integration

The frontend is designed to work with your Python backend. Update the API endpoints in `src/lib/api.ts`:

```typescript
const API_BASE_URL = 'http://your-backend-url:8000';
```

### Expected API Endpoints

#### Chat Endpoints
- `POST /chat` - Send a message and receive AI response
- `GET /sessions` - Retrieve user's chat sessions
- `DELETE /sessions/:id` - Delete a chat session

#### Prompt Management Endpoints
- `GET /prompts` - Retrieve all prompts
- `POST /prompts` - Create a new prompt
- `PUT /prompts/:id` - Update an existing prompt
- `DELETE /prompts/:id` - Delete a prompt
- `POST /prompts/:id/use` - Increment usage counter
- `GET /prompt-templates` - Get prompt templates

### API Request/Response Examples

**Create Prompt:**
```json
POST /prompts
{
  "name": "Code Review Assistant",
  "description": "Helps review code and suggest improvements",
  "content": "You are a senior software engineer...",
  "category": "coding",
  "tags": ["code-review", "development"],
  "isActive": true
}
```

**Use Prompt:**
```json
POST /prompts/123/use
// Increments usage count
```

## Customization

### Styling

The project uses Tailwind CSS with a custom design system. You can customize colors, fonts, and spacing in:

- `tailwind.config.js` - Tailwind configuration
- `src/index.css` - Global styles and CSS variables

### Components

All components are modular and can be easily customized:

- **ChatArea** - Main chat interface layout
- **MessageBubble** - Individual message styling
- **Sidebar** - Session management UI
- **ChatInput** - Message input with send button

### Theme

The app supports both light and dark themes using CSS variables. You can modify the theme colors in `src/index.css`.

## Features in Detail

### Chat Interface
- Clean, modern message bubbles
- User and AI message differentiation
- Timestamp display
- Smooth animations

### Session Management
- Create new chat sessions
- Switch between conversations
- Delete unwanted sessions
- Session titles auto-generated from first message

### Responsive Design
- Mobile-first approach
- Collapsible sidebar on mobile
- Touch-friendly interface
- Optimized for all screen sizes

### Performance
- Optimized bundle size
- Lazy loading where appropriate
- Smooth scrolling and animations
- Efficient state management

## Development

### Adding New Features

1. Create new components in `src/components/`
2. Add types in `src/types/`
3. Update API integration in `src/lib/api.ts`
4. Follow the existing code patterns

### Code Style

- Use TypeScript for type safety
- Follow React best practices
- Use Tailwind for styling
- Keep components small and focused

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

If you have questions or need help, please open an issue on GitHub.

---

Built with ❤️ for modern chatbot experiences
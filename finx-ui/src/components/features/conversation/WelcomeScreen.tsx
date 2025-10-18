import React from 'react';
import {
  Card,
  CardBody,
  Button,
  Chip,
  Avatar,
} from '@heroui/react';
import {
  Sparkles,
  Brain,
  Zap,
  Database,
  Code,
  BarChart3,
  MessageSquare,
  FileText,
} from 'lucide-react';

interface ChatWelcomeProps {
  onSendMessage: (message: string) => void;
  userName?: string;
}

export const ChatWelcome: React.FC<ChatWelcomeProps> = ({
  onSendMessage,
  userName = 'there',
}) => {
  const examplePrompts = [
    {
      icon: Brain,
      text: "What can you help me with?",
      color: "from-blue-500 to-purple-500",
      category: "General"
    },
    {
      icon: Code,
      text: "Write a Python function to sort a list",
      color: "from-green-500 to-blue-500",
      category: "Programming"
    },
    {
      icon: BarChart3,
      text: "Analyze this data and create insights",
      color: "from-purple-500 to-pink-500",
      category: "Analytics"
    },
    {
      icon: Database,
      text: "Help me design a database schema",
      color: "from-orange-500 to-red-500",
      category: "Database"
    },
    {
      icon: FileText,
      text: "Summarize this document for me",
      color: "from-teal-500 to-cyan-500",
      category: "Content"
    },
    {
      icon: Zap,
      text: "Explain quantum computing basics",
      color: "from-yellow-500 to-orange-500",
      category: "Science"
    },
  ];

  const features = [
    {
      icon: MessageSquare,
      title: "Natural Conversations",
      description: "Chat naturally and get intelligent responses"
    },
    {
      icon: Code,
      title: "Code Generation",
      description: "Generate, debug, and explain code in any language"
    },
    {
      icon: BarChart3,
      title: "Data Analysis",
      description: "Analyze data and create visualizations"
    },
    {
      icon: Database,
      title: "Database Queries",
      description: "Write and optimize SQL queries"
    },
  ];

  return (
    <div className="flex items-center justify-center h-full p-4 lg:p-8">
      <div className="text-center max-w-4xl mx-auto space-y-8">
        {/* Hero Section */}
        <div className="space-y-4">
          <div className="relative w-20 h-20 mx-auto">
            <Avatar
              className="w-20 h-20 bg-gradient-to-br from-primary to-secondary"
              icon={<Sparkles className="w-10 h-10 text-white" />}
            />
            <div className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-warning to-warning-400 rounded-full flex items-center justify-center animate-pulse">
              <span className="text-xs">✨</span>
            </div>
          </div>
          
          <div className="space-y-2">
            <h1 className="text-3xl lg:text-4xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              Welcome back, {userName}!
            </h1>
            <p className="text-default-600 text-lg leading-relaxed max-w-2xl mx-auto">
              I'm Vikki, your AI-powered assistant. I can help you with coding, data analysis, 
              writing, research, and much more. What would you like to work on today?
            </p>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="border-none shadow-sm hover:shadow-md transition-shadow">
                <CardBody className="p-4 text-center">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary/10 to-secondary/10 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <Icon className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="font-semibold text-foreground mb-1">{feature.title}</h3>
                  <p className="text-sm text-default-500">{feature.description}</p>
                </CardBody>
              </Card>
            );
          })}
        </div>

        {/* Example Prompts */}
        <div className="space-y-4">
          <div className="flex items-center justify-center gap-2">
            <Sparkles className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold text-foreground">Try these examples</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {examplePrompts.map((prompt, index) => {
              const Icon = prompt.icon;
              return (
                <Card 
                  key={index}
                  isPressable
                  isHoverable
                  className="group transition-all duration-300 hover:scale-105 cursor-pointer"
                  onPress={() => onSendMessage(prompt.text)}
                >
                  <CardBody className="p-4">
                    <div className="flex items-start gap-3">
                      <div className={`w-8 h-8 rounded-lg bg-gradient-to-r ${prompt.color} flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform duration-300`}>
                        <Icon className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex-1 text-left">
                        <div className="flex items-center gap-2 mb-1">
                          <Chip size="sm" variant="flat" color="default">
                            {prompt.category}
                          </Chip>
                        </div>
                        <p className="text-sm font-medium text-foreground group-hover:text-primary transition-colors duration-300">
                          {prompt.text}
                        </p>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Quick Tips */}
        <Card className="bg-gradient-to-r from-primary/5 to-secondary/5 border-primary/20">
          <CardBody className="p-6">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-5 h-5 text-primary" />
              <h3 className="font-semibold text-foreground">Pro Tips</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-default-600">
              <div>
                <strong>Be specific:</strong> The more details you provide, the better I can help you.
              </div>
              <div>
                <strong>Ask follow-ups:</strong> Feel free to ask for clarifications or improvements.
              </div>
              <div>
                <strong>Use examples:</strong> Show me what you're working with for better context.
              </div>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
};

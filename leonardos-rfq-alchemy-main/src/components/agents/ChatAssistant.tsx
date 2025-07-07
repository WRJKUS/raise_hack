
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { MessageSquare, Bot, User, Search, FileText, DollarSign, Calendar } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { apiClient, ChatMessage } from '@/lib/api';

const ChatAssistant = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const { toast } = useToast();

  // Initialize chat session on component mount
  useEffect(() => {
    initializeChat();
  }, []);

  const initializeChat = async () => {
    try {
      // Send initial message to start the chat session
      const response = await apiClient.sendChatMessage("Hello");
      setSessionId(response.session_id);
      setMessages([response.message]);
    } catch (error) {
      console.error('Failed to initialize chat:', error);
      // Fallback to offline message
      setMessages([{
        id: 1,
        type: 'assistant',
        content: "Hello! I'm your RFP/RFQ Chat Assistant. I notice the backend service might not be available. Please make sure the FastAPI server is running at http://localhost:8000",
        timestamp: new Date().toISOString()
      }]);
    }
  };

  const quickQuestions = [
    "What's the average budget across all proposals?",
    "Which vendors have the fastest timelines?",
    "Show me proposals from TechCorp Solutions",
    "What are the key technical requirements?",
    "Compare quotes for cloud infrastructure",
    "Which approvers are pending on current RFPs?"
  ];

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      type: 'user',
      content: newMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = newMessage;
    setNewMessage('');
    setIsTyping(true);

    try {
      const response = await apiClient.sendChatMessage(messageToSend, sessionId);

      // Update session ID if it changed
      if (response.session_id !== sessionId) {
        setSessionId(response.session_id);
      }

      setMessages(prev => [...prev, response.message]);

      // Show relevant proposals if any
      if (response.relevant_proposals.length > 0) {
        toast({
          title: "Found relevant proposals",
          description: `Referenced: ${response.relevant_proposals.join(', ')}`,
        });
      }
    } catch (error) {
      console.error('Failed to send message:', error);

      // Add error message
      const errorMessage: ChatMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `Sorry, I encountered an error: ${error.message}. Please make sure the backend service is running.`,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);

      toast({
        title: "Message failed",
        description: "Could not send message to the assistant",
        variant: "destructive"
      });
    } finally {
      setIsTyping(false);
    }
  };

  const handleQuickQuestion = (question) => {
    setNewMessage(question);
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="space-y-6">
      <Card className="bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            Agent 2: Chat Assistant (Retrieval)
          </CardTitle>
          <CardDescription>
            Ask questions about your RFP/RFQ portfolio and get intelligent, context-aware responses
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Quick Questions */}
      <Card className="bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Search className="w-4 h-4" />
            Quick Questions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {quickQuestions.map((question, index) => (
              <Button
                key={index}
                variant="outline"
                className="text-left justify-start h-auto p-3 text-sm"
                onClick={() => handleQuickQuestion(question)}
              >
                {question}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Chat Interface */}
      <Card className="bg-white shadow-sm">
        <CardContent className="p-0">
          {/* Messages Area */}
          <div className="h-96 overflow-y-auto p-4 space-y-4 border-b">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.type === 'assistant' && (
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-blue-600" />
                  </div>
                )}

                <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${message.type === 'user' ? 'order-first' : ''}`}>
                  <div
                    className={`p-3 rounded-lg ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white ml-auto'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                  </div>
                  <p className="text-xs text-gray-500 mt-1 px-1">
                    {formatTime(message.timestamp)}
                  </p>
                </div>

                {message.type === 'user' && (
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-green-600" />
                  </div>
                )}
              </div>
            ))}

            {isTyping && (
              <div className="flex gap-3 justify-start">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-blue-600" />
                </div>
                <div className="max-w-xs lg:max-w-md xl:max-w-lg">
                  <div className="p-3 rounded-lg bg-gray-100 text-gray-900">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="p-4">
            <div className="flex gap-2">
              <Input
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Ask about proposals, budgets, timelines, vendors..."
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                className="flex-1"
              />
              <Button onClick={handleSendMessage} disabled={!newMessage.trim() || isTyping}>
                Send
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Context Information */}
      <Card className="bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="text-lg">Available Context</CardTitle>
          <CardDescription>Information available for retrieval and analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
              <FileText className="w-5 h-5 text-blue-600" />
              <div>
                <p className="font-medium text-blue-900">12 Active RFPs</p>
                <p className="text-sm text-blue-700">Proposals & Requirements</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
              <DollarSign className="w-5 h-5 text-green-600" />
              <div>
                <p className="font-medium text-green-900">28 Quotes</p>
                <p className="text-sm text-green-700">Pricing & Budget Data</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
              <User className="w-5 h-5 text-purple-600" />
              <div>
                <p className="font-medium text-purple-900">47 Vendors</p>
                <p className="text-sm text-purple-700">Contact Information</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-orange-50 rounded-lg">
              <Calendar className="w-5 h-5 text-orange-600" />
              <div>
                <p className="font-medium text-orange-900">15 Workflows</p>
                <p className="text-sm text-orange-700">Approval Processes</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ChatAssistant;

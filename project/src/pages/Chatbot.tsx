import { useState } from 'react';
import { Send } from 'lucide-react';
import { useToast } from '../contexts/ToastContext';
import RobotBuddy from '../components/RobotBuddy';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  timestamp: string;
}

export default function Chatbot() {
  const { show } = useToast();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hello! I'm your database assistant. How can I help you today?",
      sender: 'bot',
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      text: input,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      setSending(true);
      const resp = await fetch('http://localhost:8000/ai/chatbot/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage.text, history: messages.slice(-6).map(m => ({ role: m.sender, content: m.text })) })
      });
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data?.detail || 'Chat service failed');
      }
      const text: string = data?.reply || "I can only answer questions related to the project documentation.";
      const botMessage: Message = {
        id: userMessage.id + 1,
        text,
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, botMessage]);
      if (data?.mode === 'fallback') {
        show('Out of scope: limited to project documentation', { type: 'info' });
      }
    } catch (e: any) {
      show(e?.message || 'Chat error', { type: 'error' });
      const botMessage: Message = {
        id: userMessage.id + 1,
        text: 'I can only answer questions related to the project documentation.',
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, botMessage]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="py-24 px-4 max-w-4xl mx-auto relative">
      <RobotBuddy />
      <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-[#00ff00] to-[#00cc00]">
        Database Assistant
      </h1>
      <p className="text-gray-400 mb-8 text-lg">Chat with your AI database expert</p>

      <div className="border border-[#00ff00]/30 rounded-lg bg-black/30 h-[600px] flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[70%] rounded-lg p-2 text-sm ${
                  message.sender === 'user'
                    ? 'bg-[#00ff00]/10 text-[#00ff00]'
                    : 'bg-gray-800 text-white'
                }`}
              >
                <p className="text-sm">{message.text}</p>
                <p className="text-[10px] text-gray-500 mt-1">{message.timestamp}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="border-t border-[#00ff00]/30 p-4">
          <div className="flex space-x-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !sending && handleSend()}
              placeholder="Ask me anything about your database..."
              className="flex-1 bg-black/50 border border-[#00ff00]/30 rounded-md px-4 py-2
                focus:outline-none focus:ring-2 focus:ring-[#00ff00]/50 text-white
                placeholder:text-gray-500 transition-all duration-300 hover:border-[#00ff00]/50"
            />
            <button
              onClick={handleSend}
              disabled={sending}
              className="bg-[#00ff00]/10 text-[#00ff00] px-4 py-2 rounded-md
                hover:bg-[#00ff00]/20 transition-all duration-300 hover-glow
                flex items-center space-x-2 border border-[#00ff00]/30 disabled:opacity-50"
            >
              <Send className="h-5 w-5" />
              <span>{sending ? 'Sending...' : 'Send'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
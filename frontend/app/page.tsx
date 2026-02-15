"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Send, Phone, User, Activity, ShieldCheck } from 'lucide-react';
import { sendMessage } from '@/lib/agent';
import clsx from 'clsx';

interface Message {
  role: 'user' | 'agent';
  content: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [customerId, setCustomerId] = useState('user123'); // Default test user
  const [threadId, setThreadId] = useState<string | undefined>(undefined);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendMessage(userMsg.content, customerId, threadId);
      setThreadId(response.thread_id);

      const agentMsg: Message = { role: 'agent', content: response.response };
      setMessages(prev => [...prev, agentMsg]);
    } catch (error) {
      console.error("Failed to get response", error);
      const errorMsg: Message = { role: 'agent', content: "Sorry, I encountered an error. Please check the backend connection." };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-900">
      {/* Header */}
      <header className="bg-blue-700 text-white p-4 shadow-md">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="h-6 w-6" />
            <h1 className="text-xl font-bold">Bank ABC Voice Agent Platform (POC)</h1>
          </div>
          <div className="flex items-center space-x-4 text-sm">
            <a href="/voice" className="hover:text-blue-200 font-semibold">
              🎙️ Voice Mode
            </a>
            <span>Status: <span className="font-semibold text-green-300">Live</span></span>
            <span>Env: <span className="font-semibold">Development</span></span>
          </div>
        </div>
      </header>

      <main className="flex-1 container mx-auto p-4 grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left Panel: Configuration & Context */}
        <div className="lg:col-span-1 space-y-6">

          {/* Simulation Control */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <User className="h-5 w-5 mr-2 text-blue-600" />
              Customer Context
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Simulated Customer ID</label>
                <select
                  value={customerId}
                  onChange={(e) => setCustomerId(e.target.value)}
                  className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 p-2 border"
                >
                  <option value="user123">John Doe (user123) - Balance: $5000</option>
                  <option value="user456">Jane Smith (user456) - Balance: $12500</option>
                  <option value="guest">Guest (Unverified)</option>
                </select>
              </div>

              <div className="p-3 bg-blue-50 rounded-md text-sm text-blue-800">
                <p className="font-semibold mb-1">Scenario Hints:</p>
                <ul className="list-disc pl-4 space-y-1">
                  <li>&quot;I lost my card&quot; (Triggers Block Card Flow)</li>
                  <li>&quot;Check my balance&quot; (Requires Verification)</li>
                  <li>&quot;My last 3 transactions&quot; (Data Retrieval)</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Monitoring Panel */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 h-64 overflow-y-auto">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <ShieldCheck className="h-5 w-5 mr-2 text-green-600" />
              Active Guardrails
            </h2>
            <div className="space-y-3">
              <div className="flex items-start space-x-2 text-sm">
                <div className="w-2 h-2 rounded-full bg-green-500 mt-1.5 flex-shrink-0"></div>
                <div>
                  <p className="font-medium text-gray-900">Identity Verification</p>
                  <p className="text-gray-500">Required for sensitive actions.</p>
                </div>
              </div>
              <div className="flex items-start space-x-2 text-sm">
                <div className="w-2 h-2 rounded-full bg-green-500 mt-1.5 flex-shrink-0"></div>
                <div>
                  <p className="font-medium text-gray-900">Confirmation Steps</p>
                  <p className="text-gray-500">Critical actions (block card) require explicit confirmation.</p>
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* Center/Right Panel: Chat Interface */}
        <div className="lg:col-span-2 flex flex-col bg-white rounded-lg shadow-sm border border-gray-100 h-[600px]">

          {/* Chat Header */}
          <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50 rounded-t-lg">
            <h2 className="text-lg font-semibold flex items-center">
              <Phone className="h-5 w-5 mr-2 text-blue-600" />
              Live Call Simulation
            </h2>
            <button
              onClick={() => { setMessages([]); setThreadId(undefined); }}
              className="text-xs text-red-600 hover:text-red-800 font-medium"
            >
              Reset Call
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 mt-20">
                <Activity className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>Start the conversation by saying &quot;Hello&quot;</p>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div key={idx} className={clsx(
                "flex w-full",
                msg.role === 'user' ? "justify-end" : "justify-start"
              )}>
                <div className={clsx(
                  "max-w-[80%] p-3 rounded-lg text-sm shadow-sm",
                  msg.role === 'user'
                    ? "bg-blue-600 text-white rounded-br-none"
                    : "bg-gray-100 text-gray-800 rounded-bl-none"
                )}>
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start w-full">
                <div className="bg-gray-100 p-3 rounded-lg rounded-bl-none flex space-x-1 items-center">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-gray-100">
            <div className="flex space-x-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Type your message..."
                className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
              />
              <button
                onClick={handleSend}
                disabled={loading || !input.trim()}
                className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-2 text-center">
              Connected to Agent: <span className="font-mono">gpt-4</span> via LangGraph
            </p>
          </div>

        </div>

      </main>
    </div>
  );
}

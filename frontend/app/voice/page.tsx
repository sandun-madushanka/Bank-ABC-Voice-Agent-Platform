"use client";

import React, { useState } from 'react';
import { LiveKitRoom, VideoConference, RoomAudioRenderer, ControlBar, useTracks } from '@livekit/components-react';
import '@livekit/components-styles';
import { Track } from 'livekit-client';
import { Phone, PhoneOff, Activity } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function VoicePage() {
    const [token, setToken] = useState('');
    const [serverUrl, setServerUrl] = useState('');
    const [roomName, setRoomName] = useState('');
    const [isConnecting, setIsConnecting] = useState(false);
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState('');
    const [participantName, setParticipantName] = useState('');

    const startVoiceCall = async () => {
        setIsConnecting(true);
        setError('');

        try {
            const response = await axios.post(`${API_BASE_URL}/voice/token`, {}, {
                params: {
                    room_name: 'bank-abc-call',
                    participant_name: participantName || 'Customer'
                }
            });

            // Check if we got placeholder credentials
            if (response.data.url && response.data.url.includes('your-project.livekit.cloud')) {
                setError('❌ LiveKit credentials not configured. Please add valid LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET to backend/.env file.');
                setIsConnecting(false);
                return;
            }

            setToken(response.data.token);
            setServerUrl(response.data.url);
            setRoomName(response.data.room_name);
            setIsConnected(true);
        } catch (err: any) {
            console.error('Failed to get token:', err);
            if (err.response?.status === 500) {
                setError('❌ Backend error: LiveKit credentials may be missing or invalid. Check backend/.env configuration.');
            } else {
                setError('❌ Failed to connect to voice server. Please check that the backend is running on port 8000.');
            }
        } finally {
            setIsConnecting(false);
        }
    };

    const endCall = () => {
        setToken('');
        setIsConnected(false);
        setRoomName('');
    };

    if (!isConnected) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
                <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-100 rounded-full mb-4">
                            <Phone className="h-10 w-10 text-blue-600" />
                        </div>
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">Bank ABC Voice Agent</h1>
                        <p className="text-gray-600">Real-time voice assistance with Gemini Live Audio</p>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Your Name (Optional)
                            </label>
                            <input
                                type="text"
                                value={participantName}
                                onChange={(e) => setParticipantName(e.target.value)}
                                placeholder="John Doe"
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>

                        {error && (
                            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                <p className="text-sm text-red-800">{error}</p>
                            </div>
                        )}

                        <button
                            onClick={startVoiceCall}
                            disabled={isConnecting}
                            className="w-full bg-blue-600 text-white py-4 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
                        >
                            {isConnecting ? (
                                <>
                                    <Activity className="h-5 w-5 animate-spin" />
                                    <span>Connecting...</span>
                                </>
                            ) : (
                                <>
                                    <Phone className="h-5 w-5" />
                                    <span>Start Voice Call</span>
                                </>
                            )}
                        </button>

                        <div className="text-center mt-6">
                            <a href="/" className="text-sm text-blue-600 hover:text-blue-800">
                                ← Back to Text Chat
                            </a>
                        </div>
                    </div>

                    <div className="mt-8 p-4 bg-blue-50 rounded-lg">
                        <p className="text-xs text-blue-800 font-semibold mb-2">Try saying:</p>
                        <ul className="text-xs text-blue-700 space-y-1">
                            <li>• &quot;Hello, I lost my card&quot;</li>
                            <li>• &quot;I want to check my balance&quot;</li>
                            <li>• &quot;Show my recent transactions&quot;</li>
                        </ul>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-900">
            <LiveKitRoom
                token={token}
                serverUrl={serverUrl}
                connect={true}
                video={false}
                audio={true}
                className="flex flex-col h-screen"
                onDisconnected={() => {
                    console.log('Disconnected from room');
                    endCall();
                }}
                onError={(error) => {
                    console.error('LiveKit connection error:', error);
                    // Set error message and reset connection state
                    setError(`❌ Connection failed: ${error.message || 'Invalid API key or connection error'}`);
                    setIsConnected(false);
                    setToken('');
                }}
            >
                <div className="flex-1 flex flex-col">
                    {/* Header */}
                    <div className="bg-gray-800 text-white p-6 border-b border-gray-700">
                        <div className="container mx-auto flex justify-between items-center">
                            <div>
                                <h1 className="text-2xl font-bold">Live Voice Call</h1>
                                <p className="text-sm text-gray-400">Connected to Bank ABC Agent</p>
                            </div>
                            <button
                                onClick={endCall}
                                className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg flex items-center space-x-2 transition-colors"
                            >
                                <PhoneOff className="h-5 w-5" />
                                <span>End Call</span>
                            </button>
                        </div>
                    </div>

                    {/* Main Call Area */}
                    <div className="flex-1 container mx-auto p-8 flex items-center justify-center">
                        <div className="text-center">
                            <div className="inline-flex items-center justify-center w-32 h-32 bg-blue-600 rounded-full mb-6 animate-pulse">
                                <Phone className="h-16 w-16 text-white" />
                            </div>
                            <h2 className="text-white text-2xl font-semibold mb-2">Voice Call Active</h2>
                            <p className="text-gray-400">Speak naturally to interact with the banking agent</p>

                            {/* Real-time transcripts would be displayed here */}
                            <TranscriptDisplay />
                        </div>
                    </div>

                    {/* Audio Renderer - Handles audio playback */}
                    <RoomAudioRenderer />
                </div>
            </LiveKitRoom>
        </div>
    );
}

function TranscriptDisplay() {
    const tracks = useTracks([Track.Source.Microphone, Track.Source.ScreenShare]);

    return (
        <div className="mt-8 bg-gray-800 rounded-lg p-6 max-w-2xl mx-auto">
            <h3 className="text-white font-semibold mb-3">Conversation Transcript</h3>
            <div className="space-y-2 text-sm text-left max-h-64 overflow-y-auto">
                <p className="text-gray-400 italic">Transcript will appear here as you speak...</p>
                {/* Transcripts from Gemini will be rendered here in real implementation */}
            </div>
        </div>
    );
}

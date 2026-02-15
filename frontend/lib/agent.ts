import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatResponse {
    response: string;
    thread_id: string;
}

export const sendMessage = async (message: string, customerId?: string, threadId?: string): Promise<ChatResponse> => {
    try {
        const response = await axios.post<ChatResponse>(`${API_BASE_URL}/chat`, {
            message,
            customer_id: customerId,
            thread_id: threadId,
        });
        return response.data;
    } catch (error) {
        console.error("Error sending message:", error);
        throw error;
    }
};

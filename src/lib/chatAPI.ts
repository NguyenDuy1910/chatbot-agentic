import { api } from './api';
import { apiConfig } from '@/config/api';

// Chat types based on backend models
export interface ChatModel {
  id: string;
  user_id: string;
  title: string;
  chat: any; // JSON field
  created_at: string;
  updated_at: string;
  share_id?: string;
  archived: boolean;
  pinned: boolean;
  folder_id?: string;
}

export interface ChatForm {
  title: string;
  chat?: any;
  folder_id?: string;
}

export interface ChatUpdateForm {
  title?: string;
  chat?: any;
  archived?: boolean;
  pinned?: boolean;
  folder_id?: string;
}

export interface MessageModel {
  id: string;
  user_id: string;
  chat_id?: string;
  channel_id?: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: string;
  created_at: string;
  updated_at: string;
}

export interface MessageForm {
  chat_id?: string;
  channel_id?: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
}

export interface MessageUpdateForm {
  content?: string;
  role?: 'user' | 'assistant' | 'system';
}

export const chatAPI = {
  // Chat operations
  async getChats(params?: {
    skip?: number;
    limit?: number;
    archived?: boolean;
    pinned?: boolean;
    folder_id?: string;
  }): Promise<ChatModel[]> {
    const searchParams = new URLSearchParams();

    if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString());
    if (params?.archived !== undefined) searchParams.append('archived', params.archived.toString());
    if (params?.pinned !== undefined) searchParams.append('pinned', params.pinned.toString());
    if (params?.folder_id) searchParams.append('folder_id', params.folder_id);

    const endpoint = `${apiConfig.endpoints.chats.base}${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;

    return api.get<ChatModel[]>(endpoint);
  },

  async getChat(chatId: string): Promise<ChatModel> {
    return api.get<ChatModel>(apiConfig.endpoints.chats.byId(chatId));
  },

  async createChat(chatData: ChatForm): Promise<ChatModel> {
    return api.post<ChatModel>(apiConfig.endpoints.chats.base, chatData);
  },

  async updateChat(chatId: string, chatData: ChatUpdateForm): Promise<ChatModel> {
    return api.put<ChatModel>(apiConfig.endpoints.chats.byId(chatId), chatData);
  },

  async deleteChat(chatId: string): Promise<{ message: string }> {
    return api.delete<{ message: string }>(apiConfig.endpoints.chats.byId(chatId));
  },

  async archiveChat(chatId: string): Promise<ChatModel> {
    return api.post<ChatModel>(apiConfig.endpoints.chats.archive(chatId));
  },

  async pinChat(chatId: string): Promise<ChatModel> {
    return api.post<ChatModel>(apiConfig.endpoints.chats.pin(chatId));
  },

  // Message operations
  async getMessages(params?: {
    chat_id?: string;
    channel_id?: string;
    user_id?: string;
    skip?: number;
    limit?: number;
  }): Promise<MessageModel[]> {
    const searchParams = new URLSearchParams();

    if (params?.chat_id) searchParams.append('chat_id', params.chat_id);
    if (params?.channel_id) searchParams.append('channel_id', params.channel_id);
    if (params?.user_id) searchParams.append('user_id', params.user_id);
    if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString());

    const endpoint = `${apiConfig.endpoints.messages.base}${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;

    return api.get<MessageModel[]>(endpoint);
  },

  async getMessage(messageId: string): Promise<MessageModel> {
    return api.get<MessageModel>(apiConfig.endpoints.messages.byId(messageId));
  },

  async createMessage(messageData: MessageForm): Promise<MessageModel> {
    return api.post<MessageModel>(apiConfig.endpoints.messages.base, messageData);
  },

  async updateMessage(messageId: string, messageData: MessageUpdateForm): Promise<MessageModel> {
    return api.put<MessageModel>(apiConfig.endpoints.messages.byId(messageId), messageData);
  },

  async deleteMessage(messageId: string): Promise<{ message: string }> {
    return api.delete<{ message: string }>(apiConfig.endpoints.messages.byId(messageId));
  },

  // Convenience methods for chat flow
  async sendMessage(chatId: string, content: string, role: 'user' | 'assistant' | 'system' = 'user'): Promise<MessageModel> {
    return this.createMessage({
      chat_id: chatId,
      content,
      role
    });
  },

  async getChatMessages(chatId: string, skip = 0, limit = 50): Promise<MessageModel[]> {
    return this.getMessages({
      chat_id: chatId,
      skip,
      limit
    });
  },

  // Legacy compatibility methods
  async getSessions(): Promise<ChatModel[]> {
    return this.getChats();
  },

  async deleteSession(sessionId: string): Promise<{ message: string }> {
    return this.deleteChat(sessionId);
  }
};

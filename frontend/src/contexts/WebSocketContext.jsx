import React, { createContext, useContext, useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const WebSocketContext = createContext();

export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider = ({ children }) => {
  const { token } = useAuth();
  const [socket, setSocket] = useState(null);
  const [realtimeNotifications, setRealtimeNotifications] = useState([]);

  useEffect(() => {
    if (!token) {
      if (socket) {
        socket.close();
        setSocket(null);
      }
      return;
    }

    const wsUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://127.0.0.1:8000/api/v1/ws/notifications';
    const ws = new WebSocket(`${wsUrl}?token=${token}`);

    ws.onopen = () => {
      console.log('Connected to WebSocket for notifications.');
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        console.log("New Notification received:", payload);
        
        // Add to our context state so pages can react if they want
        setRealtimeNotifications(prev => [payload, ...prev]);

        // Fire a Toastify alert
        if (payload.priority === 'HIGH') {
          toast.error(`${payload.title}: ${payload.message}`, { autoClose: false });
        } else if (payload.priority === 'MEDIUM') {
          toast.warning(`${payload.title}: ${payload.message}`);
        } else {
          toast.info(`${payload.title}: ${payload.message}`);
        }
      } catch (e) {
        console.error("Error parsing websocket message", e);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };

    ws.onclose = () => {
      console.log('Disconnected from WebSocket.');
    };

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, [token]);

  return (
    <WebSocketContext.Provider value={{ socket, realtimeNotifications }}>
      {children}
    </WebSocketContext.Provider>
  );
};

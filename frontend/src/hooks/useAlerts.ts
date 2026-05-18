import { useEffect, useRef, useState } from "react";
import { useAuthStore } from "@/store/authStore";

export interface AlertMessage {
  type: "out_of_stock";
  product_id: string;
  product_name: string;
  sku: string;
  qty: number;
  is_out_of_stock: boolean;
}

export function useAlerts(onAlert?: (msg: AlertMessage) => void) {
  const { isAuthenticated } = useAuthStore();
  const ws = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) return;

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(`${protocol}://${window.location.host}/api/v1/ws/alerts`);

    socket.onopen = () => setConnected(true);
    socket.onclose = () => setConnected(false);
    socket.onerror = () => setConnected(false);
    socket.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data) as AlertMessage;
        onAlert?.(msg);
      } catch {
        // ignore malformed
      }
    };

    ws.current = socket;
    return () => { socket.close(); };
  }, [isAuthenticated]);

  return { connected };
}

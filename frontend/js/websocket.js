/**
 * WebSocket Client for real-time task progress updates
 * Includes automatic reconnection and fallback to polling
 */

class TaskWebSocket {
    constructor(taskId, callbacks = {}) {
        this.taskId = taskId;
        this.callbacks = callbacks;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        this.isConnected = false;
        this.shouldReconnect = true;
        this.pollingFallback = false;
    }

    /**
     * Connect to WebSocket server
     */
    connect() {
        const wsUrl = `ws://localhost:8000/ws/tasks/${this.taskId}`;

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('WebSocket connected for task:', this.taskId);
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000;

                if (this.callbacks.onConnect) {
                    this.callbacks.onConnect();
                }
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnected = false;

                if (this.callbacks.onError) {
                    this.callbacks.onError(error);
                }
            };

            this.ws.onclose = (event) => {
                console.log('WebSocket closed:', event.code, event.reason);
                this.isConnected = false;

                if (this.shouldReconnect) {
                    this.attemptReconnect();
                }
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.fallbackToPolling();
        }
    }

    /**
     * Handle incoming WebSocket messages
     */
    handleMessage(data) {
        console.log('WebSocket message:', data);

        switch (data.type) {
            case 'connected':
                console.log('WebSocket connection confirmed');
                break;

            case 'progress':
                if (this.callbacks.onProgress) {
                    this.callbacks.onProgress({
                        stage: data.stage,
                        progress: data.progress,
                        message: data.message,
                        metadata: {
                            year: data.year,
                            event_name: data.event_name,
                            session_name: data.session_name,
                            session_date: data.session_date,
                            driver: data.driver
                        }
                    });
                }
                break;

            case 'success':
                if (this.callbacks.onSuccess) {
                    this.callbacks.onSuccess(data.result);
                }
                this.disconnect();
                break;

            case 'error':
                if (this.callbacks.onError) {
                    this.callbacks.onError(data.error);
                }
                this.disconnect();
                break;

            default:
                console.warn('Unknown WebSocket message type:', data.type);
        }
    }

    /**
     * Attempt to reconnect with exponential backoff
     */
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.warn('Max reconnection attempts reached, falling back to polling');
            this.fallbackToPolling();
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);

        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

        setTimeout(() => {
            if (this.shouldReconnect) {
                this.connect();
            }
        }, delay);
    }

    /**
     * Fall back to polling if WebSocket fails
     */
    fallbackToPolling() {
        this.pollingFallback = true;
        console.log('Switching to polling fallback');

        if (this.callbacks.onFallbackPolling) {
            this.callbacks.onFallbackPolling();
        }
    }

    /**
     * Send a message to the server (keep-alive ping)
     */
    send(message) {
        if (this.ws && this.isConnected) {
            this.ws.send(JSON.stringify(message));
        }
    }

    /**
     * Send keep-alive ping
     */
    ping() {
        this.send({ type: 'ping' });
    }

    /**
     * Disconnect and clean up
     */
    disconnect() {
        this.shouldReconnect = false;

        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        this.isConnected = false;
    }

    /**
     * Check if WebSocket is connected
     */
    get connected() {
        return this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

export default TaskWebSocket;

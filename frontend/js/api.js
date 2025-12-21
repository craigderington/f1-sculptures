/**
 * API Client for F1 Sculpture Gallery - Async Edition
 * Handles all HTTP requests to the backend API
 */

class F1API {
    constructor(baseUrl = null) {
        // Auto-detect: use relative URL for production, localhost:8000 for local dev
        if (!baseUrl) {
            const isLocalDev = window.location.hostname === 'localhost' && window.location.port === '3000';
            baseUrl = isLocalDev ? 'http://localhost:8000/api' : '/api';
        }
        this.baseUrl = baseUrl;
    }

    /**
     * Generic fetch wrapper with error handling
     */
    async request(endpoint, options = {}) {
        try {
            const url = `${this.baseUrl}${endpoint}`;
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    // ========================================================================
    // Metadata Endpoints (Synchronous - Fast)
    // ========================================================================

    /**
     * Get all F1 events for a year
     */
    async getEvents(year) {
        return this.request(`/events/${year}`);
    }

    /**
     * Get available sessions for an event
     */
    async getSessions(year, round) {
        return this.request(`/sessions/${year}/${round}`);
    }

    /**
     * Get drivers in a session (deprecated but still works)
     */
    async getDrivers(year, round, session) {
        return this.request(`/drivers/${year}/${round}/${session}`);
    }

    // ========================================================================
    // Async Task Endpoints (Background Processing)
    // ========================================================================

    /**
     * Submit a sculpture generation task
     * Returns task ID for tracking progress
     */
    async submitSculptureTask(year, round, session, driver) {
        return this.request('/tasks/sculpture', {
            method: 'POST',
            body: JSON.stringify({ year, round, session, driver })
        });
    }

    /**
     * Submit a multi-driver comparison task
     */
    async submitCompareTask(year, round, session, drivers) {
        return this.request('/tasks/compare', {
            method: 'POST',
            body: JSON.stringify({ year, round, session, drivers })
        });
    }

    /**
     * Get task status (polling fallback)
     */
    async getTaskStatus(taskId) {
        return this.request(`/tasks/${taskId}`);
    }

    /**
     * Get task result (when completed)
     */
    async getTaskResult(taskId) {
        return this.request(`/tasks/${taskId}/result`);
    }

    /**
     * Cancel a running task
     */
    async cancelTask(taskId) {
        return this.request(`/tasks/${taskId}`, {
            method: 'DELETE'
        });
    }

    // ========================================================================
    // Cache Management
    // ========================================================================

    /**
     * Get cache statistics
     */
    async getCacheStats() {
        return this.request('/cache/stats');
    }

    /**
     * Clear sculpture cache (admin)
     */
    async clearSculptureCache() {
        return this.request('/cache/sculptures', {
            method: 'DELETE'
        });
    }

    // ========================================================================
    // Health Check
    // ========================================================================

    /**
     * Check API health
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl.replace('/api', '')}/health`);
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            return { api: 'unhealthy', redis: 'unknown', celery: 'unknown' };
        }
    }
}

export default F1API;

import { apiRequest } from './api';

export const notificationService = {
  /**
   * List notifications with pagination and filters
   */
  async getNotifications(limit = 50, offset = 0, unreadOnly = false, type = null) {
    let url = `/notifications?limit=${limit}&offset=${offset}&unread_only=${unreadOnly}`;
    if (type) {
      url += `&type=${encodeURIComponent(type)}`;
    }
    return apiRequest(url);
  },

  /**
   * Mark a single notification as read
   */
  async markNotificationRead(notificationId) {
    return apiRequest(`/notifications/${notificationId}/read`, {
      method: 'PATCH',
    });
  },

  /**
   * Mark all unread notifications for current user as read
   */
  async markAllNotificationsRead() {
    return apiRequest('/notifications/read-all', {
      method: 'POST',
    });
  },

  /**
   * Fetch total unread notification count
   */
  async getUnreadNotificationCount() {
    return apiRequest('/notifications/unread-count');
  },

  /**
   * Fetch summary of unread messages and notifications in a single call
   */
  async getUnreadSummary() {
    return apiRequest('/notifications/unread-summary');
  },

  /**
   * Get authenticated user's notification preferences
   */
  async getNotificationPreferences() {
    return apiRequest('/notifications/preferences');
  },

  /**
   * Update authenticated user's notification preferences
   */
  async updateNotificationPreferences(preferences) {
    return apiRequest('/notifications/preferences', {
      method: 'PATCH',
      body: JSON.stringify(preferences),
    });
  },
};

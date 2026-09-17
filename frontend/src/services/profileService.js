import { apiRequest } from './api';

export const profileService = {
  /**
   * Fetch current authenticated user's full profile, role details, and completion stats.
   */
  async getMyProfile() {
    return apiRequest('/profiles/me');
  },

  /**
   * Update current authenticated user's profile fields.
   */
  async updateMyProfile(updateData) {
    return apiRequest('/profiles/me', {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  },

  /**
   * Get public profile by @username or user ID.
   */
  async getPublicProfile(identifier) {
    return apiRequest(`/profiles/${identifier}`);
  },

  /**
   * Get profile completion progress and tips.
   */
  async getCompletion() {
    return apiRequest('/profiles/completion/me');
  },
};

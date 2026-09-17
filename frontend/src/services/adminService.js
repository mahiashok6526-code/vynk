import { apiRequest } from './api';

export const adminService = {
  // Dashboard & stats
  async getDashboard() {
    return await apiRequest('/admin/dashboard');
  },

  // Users
  async getUsers(params = {}) {
    const query = new URLSearchParams();
    if (params.search) query.append('search', params.search);
    if (params.role) query.append('role', params.role);
    if (params.is_verified !== undefined && params.is_verified !== '') {
      query.append('is_verified', params.is_verified);
    }
    if (params.is_suspended !== undefined && params.is_suspended !== '') {
      query.append('is_suspended', params.is_suspended);
    }
    if (params.page) query.append('page', params.page);
    if (params.limit) query.append('limit', params.limit);

    const queryString = query.toString();
    return await apiRequest(`/admin/users${queryString ? `?${queryString}` : ''}`);
  },

  async getUserDetail(userId) {
    return await apiRequest(`/admin/users/${userId}`);
  },

  async verifyUser(userId, data = {}) {
    return await apiRequest(`/admin/users/${userId}/verify`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async revokeVerification(userId, data = {}) {
    return await apiRequest(`/admin/users/${userId}/revoke-verification`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async suspendUser(userId, data) {
    return await apiRequest(`/admin/users/${userId}/suspend`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async unsuspendUser(userId) {
    return await apiRequest(`/admin/users/${userId}/unsuspend`, {
      method: 'POST',
    });
  },

  // Projects
  async getProjects(params = {}) {
    const query = new URLSearchParams();
    if (params.search) query.append('search', params.search);
    if (params.status) query.append('status', params.status);
    if (params.category) query.append('category', params.category);
    if (params.moderation_status) query.append('moderation_status', params.moderation_status);
    if (params.page) query.append('page', params.page);
    if (params.limit) query.append('limit', params.limit);

    const queryString = query.toString();
    return await apiRequest(`/admin/projects${queryString ? `?${queryString}` : ''}`);
  },

  async getProjectDetail(projectId) {
    return await apiRequest(`/admin/projects/${projectId}`);
  },

  async approveProject(projectId, data = {}) {
    return await apiRequest(`/admin/projects/${projectId}/approve`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async rejectProject(projectId, data) {
    return await apiRequest(`/admin/projects/${projectId}/reject`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Reports
  async getReports(params = {}) {
    const query = new URLSearchParams();
    if (params.status) query.append('status', params.status);
    if (params.category) query.append('category', params.category);
    if (params.page) query.append('page', params.page);
    if (params.limit) query.append('limit', params.limit);

    const queryString = query.toString();
    return await apiRequest(`/admin/reports${queryString ? `?${queryString}` : ''}`);
  },

  async getReportDetail(reportId) {
    return await apiRequest(`/admin/reports/${reportId}`);
  },

  async reviewReport(reportId) {
    return await apiRequest(`/admin/reports/${reportId}/review`, {
      method: 'POST',
    });
  },

  async resolveReport(reportId, data) {
    return await apiRequest(`/admin/reports/${reportId}/resolve`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async dismissReport(reportId, data = {}) {
    return await apiRequest(`/admin/reports/${reportId}/dismiss`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Disputes
  async getDisputes(params = {}) {
    const query = new URLSearchParams();
    if (params.status) query.append('status', params.status);
    if (params.reason) query.append('reason', params.reason);
    if (params.page) query.append('page', params.page);
    if (params.limit) query.append('limit', params.limit);

    const queryString = query.toString();
    return await apiRequest(`/admin/disputes${queryString ? `?${queryString}` : ''}`);
  },

  async getDisputeDetail(disputeId) {
    return await apiRequest(`/admin/disputes/${disputeId}`);
  },

  async reviewDispute(disputeId) {
    return await apiRequest(`/admin/disputes/${disputeId}/review`, {
      method: 'POST',
    });
  },

  async resolveDispute(disputeId, data) {
    return await apiRequest(`/admin/disputes/${disputeId}/resolve`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async dismissDispute(disputeId, data = {}) {
    return await apiRequest(`/admin/disputes/${disputeId}/dismiss`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Audit Logs
  async getAuditLogs(params = {}) {
    const query = new URLSearchParams();
    if (params.action) query.append('action', params.action);
    if (params.entity_type) query.append('entity_type', params.entity_type);
    if (params.admin_id) query.append('admin_id', params.admin_id);
    if (params.page) query.append('page', params.page);
    if (params.limit) query.append('limit', params.limit);

    const queryString = query.toString();
    return await apiRequest(`/admin/audit-logs${queryString ? `?${queryString}` : ''}`);
  },

  // User-facing reporting & dispute creation
  async submitReport(payload) {
    return await apiRequest('/reports', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async initiateDispute(payload) {
    return await apiRequest('/disputes', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};

/**
 * Vynk API Client with JWT Bearer Token Injection and Error Normalization.
 */

const API_BASE_URL = '/api/v1';

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('vynk_token');

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    // If 401, clear stored auth if not already on login/register
    if (response.status === 401 && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/register')) {
      localStorage.removeItem('vynk_token');
      localStorage.removeItem('vynk_user');
      window.dispatchEvent(new CustomEvent('vynk:unauthorized'));
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMessage = data?.detail || data?.message || `Request failed with status ${response.status}`;
      const error = new Error(errorMessage);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  } catch (err) {
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('Unable to connect to Vynk server. Please check your network or try again.');
    }
    throw err;
  }
}

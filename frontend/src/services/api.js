import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const verifyPin = async (pin) => {
  try {
    const response = await api.post('/verify-pin', { pin });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to verify PIN');
  }
};

export const changePin = async (oldPin, newPin) => {
  try {
    const response = await api.post('/change-pin', { old_pin: oldPin, new_pin: newPin });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to change PIN');
  }
};

export const addEntry = async (content) => {
  try {
    const response = await api.post('/add-entry', { content });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to add entry');
  }
};

export const getEntries = async () => {
  try {
    const response = await api.get('/entries');
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch entries');
  }
};

export const deleteEntry = async (id) => {
  try {
    const response = await api.delete(`/entries/${id}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to delete entry');
  }
};

export const updateEntry = async (id, content) => {
  try {
    const response = await api.put(`/entries/${id}`, { content });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to update entry');
  }
}; 
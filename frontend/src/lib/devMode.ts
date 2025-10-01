/**
 * Development Mode Utilities
 * Provides mock authentication and data for testing without Gmail
 */

import api from './api';

export const DEV_MODE = process.env.NODE_ENV === 'development';

export interface DevUser {
  id: string;
  email: string;
  name: string;
  picture?: string;
}

export const DEV_USER: DevUser = {
  id: '00000000-0000-0000-0000-000000000001',
  email: 'dev@example.com',
  name: 'Development User',
  picture: undefined,
};

export const DEV_TOKEN = 'dev-token-12345-abcde';

/**
 * Enable development mode with mock authentication
 */
export function enableDevMode() {
  if (!DEV_MODE) {
    console.warn('Dev mode only available in development environment');
    return false;
  }

  console.log('%c🚀 Development Mode Enabled', 'color: #10b981; font-weight: bold; font-size: 14px');
  console.log('Using mock authentication and data');

  api.setAuthToken(DEV_TOKEN);
  localStorage.setItem('user', JSON.stringify(DEV_USER));
  localStorage.setItem('dev_mode', 'true');

  return true;
}

/**
 * Disable development mode
 */
export function disableDevMode() {
  api.setAuthToken(null);
  localStorage.removeItem('user');
  localStorage.removeItem('dev_mode');
  console.log('Dev mode disabled');
}

/**
 * Check if dev mode is active
 */
export function isDevModeActive(): boolean {
  return DEV_MODE && localStorage.getItem('dev_mode') === 'true';
}

/**
 * Seed test data using the backend /dev/seed endpoint
 */
export async function seedTestData() {
  if (!DEV_MODE) {
    throw new Error('Seed data only available in development');
  }

  try {
    const result = await api.dev.seedData();
    console.log('✅ Test data seeded:', result);
    return result;
  } catch (error) {
    console.error('Failed to seed test data:', error);
    throw error;
  }
}

/**
 * Clear all test data
 */
export async function clearTestData() {
  if (!DEV_MODE) {
    throw new Error('Clear data only available in development');
  }

  try {
    const result = await api.dev.clearData();
    console.log('✅ Test data cleared:', result);
    return result;
  } catch (error) {
    console.error('Failed to clear test data:', error);
    throw error;
  }
}

// Expose dev utilities to window for easy console access
if (typeof window !== 'undefined' && DEV_MODE) {
  (window as any).devMode = {
    enable: enableDevMode,
    disable: disableDevMode,
    seed: seedTestData,
    clear: clearTestData,
    user: DEV_USER,
  };

  console.log('%cDev Tools Available:', 'color: #8b5cf6; font-weight: bold');
  console.log('  devMode.enable()  - Enable dev mode with mock auth');
  console.log('  devMode.disable() - Disable dev mode');
  console.log('  devMode.seed()    - Seed test data');
  console.log('  devMode.clear()   - Clear test data');
}

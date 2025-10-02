/**
 * Sync Google OAuth tokens from Supabase to backend
 * This is needed so the backend can access Gmail API
 */

import { supabase } from './supabase';
import api from './api';

export async function syncGoogleTokensToBackend(): Promise<boolean> {
  try {
    // Get current session
    const { data: { session }, error: sessionError } = await supabase.auth.getSession();

    if (sessionError || !session) {
      console.error('No active session:', sessionError);
      return false;
    }

    // Get provider token (Google OAuth token)
    const providerToken = session.provider_token;
    const providerRefreshToken = session.provider_refresh_token;

    if (!providerToken) {
      console.warn('No provider token available - user may need to re-authenticate');
      return false;
    }

    console.log('Syncing Google tokens to backend...');

    // Call backend endpoint to save tokens
    // We'll need to create this endpoint
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/sync-google-tokens`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session.access_token}`,
      },
      body: JSON.stringify({
        google_access_token: providerToken,
        google_refresh_token: providerRefreshToken,
      }),
    });

    if (!response.ok) {
      console.error('Failed to sync tokens:', await response.text());
      return false;
    }

    console.log('✅ Google tokens synced successfully');
    return true;

  } catch (error) {
    console.error('Error syncing Google tokens:', error);
    return false;
  }
}

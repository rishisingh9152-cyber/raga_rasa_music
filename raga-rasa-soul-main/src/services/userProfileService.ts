import { API_BASE_URL } from "@/lib/apiBase";

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface SessionSummary {
  session_id: string;
  emotion: string | null;
  rasa: string | null;
  duration_minutes: number;
  status: string;
  songs_played: number;
  songs_rated: number;
  average_rating: number;
  images_captured: number;
  tests_completed: number;
  created_at: string;
  ended_at: string | null;
  feedback: any;
}

export interface SessionHistory {
  session_id: string;
  user_id: string | null;
  created_at: string;
  emotion: string | null;
  rasa: string | null;
  status: string;
}

export interface UserStats {
  total_sessions: number;
  completed_sessions: number;
  average_mood_rating: number;
  most_used_rasa: string | null;
  total_songs_played: number;
  total_songs_rated: number;
  average_session_duration: number;
}

export interface MoodTrend {
  date: string;
  emotion: string;
  session_count: number;
}

// ============================================================================
// 1. GET USER'S SESSION HISTORY
// ============================================================================

/**
 * Fetch the authenticated user's complete session history
 * @param token JWT authentication token
 * @returns Array of session history records
 */
export async function getUserSessionHistory(token: string): Promise<SessionHistory[]> {
  try {
    console.log("[UserProfileService] Fetching user session history");
    
    const response = await fetch(`${API_BASE_URL}/sessions`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[UserProfileService] Error ${response.status}: ${errorText}`);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log(`[UserProfileService] Retrieved ${data.sessions?.length || 0} sessions`);
    
    return data.sessions || [];
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    console.error(`[UserProfileService] getUserSessionHistory error: ${errorMsg}`);
    throw new Error(`Failed to fetch session history: ${errorMsg}`);
  }
}

// ============================================================================
// 2. GET SESSION SUMMARY
// ============================================================================

/**
 * Fetch detailed summary for a specific session
 * @param token JWT authentication token
 * @param sessionId The session ID to fetch
 * @returns Session summary with statistics
 */
export async function getSessionSummary(token: string, sessionId: string): Promise<SessionSummary> {
  try {
    console.log(`[UserProfileService] Fetching summary for session: ${sessionId}`);
    
    const response = await fetch(`${API_BASE_URL}/session/${sessionId}/summary`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[UserProfileService] Error ${response.status}: ${errorText}`);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log(`[UserProfileService] Retrieved session summary: ${JSON.stringify(data)}`);
    
    return data;
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    console.error(`[UserProfileService] getSessionSummary error: ${errorMsg}`);
    throw new Error(`Failed to fetch session summary: ${errorMsg}`);
  }
}

// ============================================================================
// 3. GET COMPLETED SESSIONS (for history)
// ============================================================================

/**
 * Fetch only completed sessions for the authenticated user
 * @param token JWT authentication token
 * @param limit Maximum number of sessions to return
 * @returns Array of completed session history records
 */
export async function getCompletedSessions(token: string, limit: number = 10): Promise<SessionHistory[]> {
  try {
    console.log(`[UserProfileService] Fetching completed sessions (limit: ${limit})`);
    
    const response = await fetch(`${API_BASE_URL}/sessions?status=completed&limit=${limit}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[UserProfileService] Error ${response.status}: ${errorText}`);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log(`[UserProfileService] Retrieved ${data.sessions?.length || 0} completed sessions`);
    
    return data.sessions || [];
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    console.error(`[UserProfileService] getCompletedSessions error: ${errorMsg}`);
    throw new Error(`Failed to fetch completed sessions: ${errorMsg}`);
  }
}

// ============================================================================
// 4. CALCULATE USER STATS (aggregated from sessions)
// ============================================================================

/**
 * Calculate aggregated user statistics from all their sessions
 * @param token JWT authentication token
 * @returns User statistics object
 */
export async function calculateUserStats(token: string): Promise<UserStats> {
  try {
    console.log("[UserProfileService] Calculating user stats");
    
    // Fetch all sessions for this user
    const sessions = await getUserSessionHistory(token);
    
    if (sessions.length === 0) {
      return {
        total_sessions: 0,
        completed_sessions: 0,
        average_mood_rating: 0,
        most_used_rasa: null,
        total_songs_played: 0,
        total_songs_rated: 0,
        average_session_duration: 0
      };
    }

    // Calculate stats
    const completedSessions = sessions.filter(s => s.status === 'completed');
    
    // Get summaries for completed sessions to get detailed stats
    const summaries = await Promise.all(
      completedSessions.slice(0, 20).map(s => getSessionSummary(token, s.session_id).catch(() => null))
    );

    const validSummaries = summaries.filter((s): s is SessionSummary => s !== null);
    
    const totalSongsPlayed = validSummaries.reduce((sum, s) => sum + (s.songs_played || 0), 0);
    const totalSongsRated = validSummaries.reduce((sum, s) => sum + (s.songs_rated || 0), 0);
    const averageRating = validSummaries.length > 0 
      ? validSummaries.reduce((sum, s) => sum + (s.average_rating || 0), 0) / validSummaries.length
      : 0;
    const averageDuration = validSummaries.length > 0
      ? validSummaries.reduce((sum, s) => sum + (s.duration_minutes || 0), 0) / validSummaries.length
      : 0;

    // Find most used rasa
    const rasaFreq: Record<string, number> = {};
    sessions.forEach(s => {
      if (s.rasa) {
        rasaFreq[s.rasa] = (rasaFreq[s.rasa] || 0) + 1;
      }
    });
    const mostUsedRasa = Object.entries(rasaFreq).sort((a, b) => b[1] - a[1])[0]?.[0] || null;

    const stats: UserStats = {
      total_sessions: sessions.length,
      completed_sessions: completedSessions.length,
      average_mood_rating: Math.round(averageRating * 100) / 100,
      most_used_rasa: mostUsedRasa,
      total_songs_played: totalSongsPlayed,
      total_songs_rated: totalSongsRated,
      average_session_duration: Math.round(averageDuration * 100) / 100
    };

    console.log(`[UserProfileService] Calculated stats: ${JSON.stringify(stats)}`);
    return stats;
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    console.error(`[UserProfileService] calculateUserStats error: ${errorMsg}`);
    throw new Error(`Failed to calculate user stats: ${errorMsg}`);
  }
}

// ============================================================================
// 5. GET MOOD TRENDS (over time)
// ============================================================================

/**
 * Calculate mood trends over the past 30 days
 * @param token JWT authentication token
 * @returns Array of mood trends by date
 */
export async function getMoodTrends(token: string): Promise<MoodTrend[]> {
  try {
    console.log("[UserProfileService] Calculating mood trends");
    
    const sessions = await getUserSessionHistory(token);
    
    if (sessions.length === 0) {
      return [];
    }

    // Group sessions by date and emotion
    const trendsByDate: Record<string, Record<string, number>> = {};
    
    sessions.forEach(session => {
      const date = new Date(session.created_at).toISOString().split('T')[0];
      const emotion = session.emotion || 'Unknown';
      
      if (!trendsByDate[date]) {
        trendsByDate[date] = {};
      }
      
      trendsByDate[date][emotion] = (trendsByDate[date][emotion] || 0) + 1;
    });

    // Convert to array format
    const trends: MoodTrend[] = Object.entries(trendsByDate).flatMap(([date, emotions]) =>
      Object.entries(emotions).map(([emotion, count]) => ({
        date,
        emotion,
        session_count: count
      }))
    );

    console.log(`[UserProfileService] Calculated ${trends.length} mood trend entries`);
    return trends;
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    console.error(`[UserProfileService] getMoodTrends error: ${errorMsg}`);
    throw new Error(`Failed to calculate mood trends: ${errorMsg}`);
  }
}

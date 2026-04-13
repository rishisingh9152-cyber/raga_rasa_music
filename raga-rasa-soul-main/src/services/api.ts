// API Base URL - configurable via environment variable
// IMPORTANT: Must include /api suffix or full URL with /api
// In production: use VITE_API_BASE_URL env variable
// Fallback for dev: uses relative /api (proxied in vite.config.ts to http://localhost:8000/api)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface CognitiveData {
  memory_score: number;    // 0-6
  reaction_time: number;   // milliseconds
  accuracy_score: number;  // 0-100 percentage
}

export interface Song {
  song_id: string;
  title: string;
  audio_url: string;
  rasa: string;
  confidence: number;
}

export interface FeedbackData {
  mood_after: string;
  session_rating: number;  // 1-5
  comment: string;
}

// ============================================================================
// 1. START SESSION
// ============================================================================

export async function startSession(): Promise<{ session_id: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/session/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (err) {
    console.error("startSession error:", err);
    throw new Error("Failed to start session");
  }
}

// ============================================================================
// 2. DETECT EMOTION
// ============================================================================

export async function detectEmotion(
  image_base64: string,
  session_id: string
): Promise<{ emotion: string }> {
  try {
    console.log(`[API] Calling detect-emotion endpoint for session: ${session_id}`);
    console.log(`[API] Image base64 length: ${image_base64.length}`);
    
    const response = await fetch(`${API_BASE_URL}/detect-emotion`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        image_base64,
        session_id
      })
    });

    console.log(`[API] detect-emotion response status: ${response.status}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[API] detect-emotion error response: ${errorText}`);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log(`[API] detect-emotion returned: ${JSON.stringify(data)}`);
    return data;
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    console.error(`[API] detectEmotion error: ${errorMsg}`);
    throw new Error(`Emotion detection failed: ${errorMsg}`);
  }
}

// ============================================================================
// 3. RECOMMEND LIVE (with cognitive_data)
// ============================================================================

export async function recommendLive(
  emotion: string,
  session_id: string,
  cognitive_data: CognitiveData
): Promise<Song[]> {
  try {
    console.log(`[API] Calling recommend/live with emotion: ${emotion}, session: ${session_id}`);
    console.log(`[API] Cognitive data: ${JSON.stringify(cognitive_data)}`);
    
    const response = await fetch(`${API_BASE_URL}/recommend/live`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        emotion,
        session_id,
        cognitive_data
      })
    });

    console.log(`[API] recommend/live response status: ${response.status}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[API] recommend/live error response: ${errorText}`);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log(`[API] recommend/live returned ${Array.isArray(data) ? data.length : 0} songs`);
    return Array.isArray(data) ? data : [];
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    console.error(`[API] recommendLive error: ${errorMsg}`);
    throw new Error(`Recommendations failed: ${errorMsg}`);
  }
}

// ============================================================================
// 4. RECOMMEND FINAL (with cognitive_data + feedback)
// ============================================================================

export async function recommendFinal(
  emotion: string,
  session_id: string,
  cognitive_data: CognitiveData,
  feedback: FeedbackData
): Promise<Song[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/recommend/final`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        emotion,
        session_id,
        cognitive_data,
        feedback
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return Array.isArray(data) ? data : [];
  } catch (err) {
    console.error("recommendFinal error:", err);
    throw new Error("Failed to get final recommendations");
  }
}

// ============================================================================
// 5. RATE SONG
// ============================================================================

export async function rateSong(
  user_id: string,
  song_id: string,
  rating: number,
  session_id: string,
  feedback: FeedbackData
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/rate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id,
        song_id,
        rating,
        session_id,
        feedback
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (err) {
    console.error("rateSong error:", err);
    throw new Error("Failed to submit rating");
  }
}

// ============================================================================
// 6. GET SONGS BY RASA
// ============================================================================

export async function getSongsByRasa(): Promise<{ [key: string]: Song[] }> {
  try {
    console.log(`[API] Fetching songs by rasa from: ${API_BASE_URL}/songs/by-rasa`);
    
    const response = await fetch(`${API_BASE_URL}/songs/by-rasa`, {
      method: "GET",
      headers: { "Content-Type": "application/json" }
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log(`[API] Received response with keys:`, Object.keys(data));
    
    // Extract the by_rasa object from the response
    // The backend returns { songs: [...], by_rasa: { Shaant: [...], ... }, total: N }
    // We need to extract just the by_rasa part for the frontend
    const songsByRasa = data.by_rasa || data;
    console.log(`[API] Extracted songs by rasa - keys:`, Object.keys(songsByRasa));
    
    // Validate that we have proper structure
    if (!songsByRasa || Object.keys(songsByRasa).length === 0) {
      console.warn(`[API] Warning: songsByRasa is empty`);
      return {};
    }
    
    return songsByRasa;
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    console.error(`[API] getSongsByRasa error: ${errorMsg}`);
    throw new Error(`Failed to fetch songs: ${errorMsg}`);
  }
}

// ============================================================================
// 7. SUBMIT SONG RATING (Simple)
// ============================================================================

export async function submitSongRating(
  song_id: string,
  song_title: string,
  rasa: string,
  rating: number,
  comments?: string
): Promise<void> {
  try {
    console.log(`[API] Submitting rating for song: ${song_title}`);
    
    const response = await fetch(`${API_BASE_URL}/rate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        song_id,
        song_title,
        rasa,
        rating,
        comments: comments || ""
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    console.log(`[API] Rating submitted successfully for: ${song_title}`);
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    console.error(`[API] submitSongRating error: ${errorMsg}`);
    throw new Error(`Failed to submit rating: ${errorMsg}`);
  }
}

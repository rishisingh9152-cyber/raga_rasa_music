import React, { createContext, useContext, useState, ReactNode } from "react";

// ============================================================================
// INTERFACES
// ============================================================================

export interface CognitiveData {
  memory_score: number;
  reaction_time: number;
  accuracy_score: number;
}

export interface Song {
  song_id: string;
  title: string;
  audio_url: string;
  rasa: string;
  confidence: number;
}

export interface TestResults {
  reactionTime: number;
  memoryScore: number;
  moodLevel: number;
}

export interface SessionState {
  // EXISTING FIELDS
  step: "pre-test" | "live" | "post-test" | "feedback";
  preTestResults: TestResults | null;
  postTestResults: TestResults | null;
  currentEmotion: string;
  currentRaga: string;
  sessionRating: number;
  sessionComment: string;
  isActive: boolean;

  // NEW FIELDS FOR API INTEGRATION
  session_id: string | null;
  detected_emotion: string | null;
  cognitive_data: CognitiveData | null;
  recommended_songs: Song[] | null;
  currentAudio: HTMLAudioElement | null;
}

export interface SessionContextType {
  session: SessionState;
  // EXISTING METHODS
  setStep: (step: SessionState["step"]) => void;
  setPreTestResults: (results: TestResults) => void;
  setPostTestResults: (results: TestResults) => void;
  setCurrentEmotion: (emotion: string) => void;
  setCurrentRaga: (raga: string) => void;
  setSessionRating: (rating: number) => void;
  setSessionComment: (comment: string) => void;
  resetSession: () => void;
  skipToLive: () => void;

  // NEW METHODS
  setSessionId: (id: string) => void;
  setDetectedEmotion: (emotion: string) => void;
  setCognitiveData: (data: CognitiveData) => void;
  setRecommendedSongs: (songs: Song[]) => void;
  setCurrentAudio: (audio: HTMLAudioElement | null) => void;
}

// ============================================================================
// DEFAULT STATE
// ============================================================================

const defaultCognitiveData: CognitiveData = {
  memory_score: 0,
  reaction_time: 0,
  accuracy_score: 0
};

const defaultSession: SessionState = {
  step: "pre-test",
  preTestResults: null,
  postTestResults: null,
  currentEmotion: "Neutral",
  currentRaga: "Raga Darbari",
  sessionRating: 0,
  sessionComment: "",
  isActive: false,

  session_id: null,
  detected_emotion: null,
  cognitive_data: defaultCognitiveData,
  recommended_songs: null,
  currentAudio: null
};

// ============================================================================
// CONTEXT & PROVIDER
// ============================================================================

const SessionContext = createContext<SessionContextType | null>(null);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<SessionState>(defaultSession);

  // EXISTING METHODS
  const setStep = (step: SessionState["step"]) =>
    setSession(s => ({ ...s, step, isActive: step === "live" }));

  const setPreTestResults = (results: TestResults) =>
    setSession(s => ({ ...s, preTestResults: results }));

  const setPostTestResults = (results: TestResults) =>
    setSession(s => ({ ...s, postTestResults: results }));

  const setCurrentEmotion = (emotion: string) =>
    setSession(s => ({ ...s, currentEmotion: emotion }));

  const setCurrentRaga = (raga: string) =>
    setSession(s => ({ ...s, currentRaga: raga }));

  const setSessionRating = (rating: number) =>
    setSession(s => ({ ...s, sessionRating: rating }));

  const setSessionComment = (comment: string) =>
    setSession(s => ({ ...s, sessionComment: comment }));

  const resetSession = () => setSession(defaultSession);

  const skipToLive = () =>
    setSession(s => ({
      ...s,
      step: "live",
      isActive: true,
      preTestResults: { reactionTime: 0, memoryScore: 0, moodLevel: 5 }
    }));

  // NEW METHODS
  const setSessionId = (id: string) =>
    setSession(s => ({ ...s, session_id: id }));

  const setDetectedEmotion = (emotion: string) =>
    setSession(s => ({ ...s, detected_emotion: emotion }));

  const setCognitiveData = (data: CognitiveData) =>
    setSession(s => ({ ...s, cognitive_data: data }));

  const setRecommendedSongs = (songs: Song[]) =>
    setSession(s => ({ ...s, recommended_songs: songs }));

  const setCurrentAudio = (audio: HTMLAudioElement | null) =>
    setSession(s => ({ ...s, currentAudio: audio }));

  return (
    <SessionContext.Provider
      value={{
        session,
        setStep,
        setPreTestResults,
        setPostTestResults,
        setCurrentEmotion,
        setCurrentRaga,
        setSessionRating,
        setSessionComment,
        resetSession,
        skipToLive,
        setSessionId,
        setDetectedEmotion,
        setCognitiveData,
        setRecommendedSongs,
        setCurrentAudio
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error("useSession must be used within SessionProvider");
  return ctx;
}

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { useSession } from "@/context/SessionContext";
import { Camera, Music, Square } from "lucide-react";
import { startSession, detectEmotion, recommendLive } from "@/services/api";
import { AudioPlayer } from "@/components/AudioPlayer";

const LiveSession = () => {
  const {
    session,
    setStep,
    setSessionId,
    setDetectedEmotion,
    setRecommendedSongs,
    setCurrentAudio
  } = useSession();

  // Refs
  const audioRef = useRef<HTMLAudioElement>(null);

  // Webcam state
  const [webcamActive, setWebcamActive] = useState(false);
  const [videoStream, setVideoStream] = useState<MediaStream | null>(null);
  const [videoRef, setVideoRef] = useState<HTMLVideoElement | null>(null);
  const [canvasRef, setCanvasRef] = useState<HTMLCanvasElement | null>(null);

  // API state
  const [emotionLoading, setEmotionLoading] = useState(false);
  const [songsLoading, setSongsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  // Playback state
  const [currentPlayingSongId, setCurrentPlayingSongId] = useState<string | null>(null);
  const [currentPlayingSong, setCurrentPlayingSong] = useState<any | null>(null);

  const getSongId = (song: any): string => {
    if (!song) return "";
    return song.song_id || song._id || "";
  };

  // useEffect 1: Start session on mount
  useEffect(() => {
    const initSession = async () => {
      try {
        const { session_id } = await startSession();
        setSessionId(session_id);
      } catch (err) {
        setApiError("Failed to start session. Please try again.");
        console.error("Session start error:", err);
      }
    };

    if (session.step === "live" && !session.session_id) {
      initSession();
    }
  }, [session.step, session.session_id]);

  // useEffect 2: Request camera access
  useEffect(() => {
    const requestCamera = async () => {
      if (session.detected_emotion) return;

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user" }
        });
        setVideoStream(stream);
        setWebcamActive(true);
      } catch (err) {
        setApiError("Camera access required. Please allow access and try again.");
        console.error("Camera access error:", err);
        setWebcamActive(false);
      }
    };

    requestCamera();

    return () => {
      videoStream?.getTracks().forEach(track => track.stop());
    };
  }, [session.detected_emotion]);

  // useEffect 3: Set video element source
  useEffect(() => {
    if (videoRef && videoStream) {
      videoRef.srcObject = videoStream;
    }
  }, [videoRef, videoStream]);

  // Function: Capture emotion
  const handleCaptureEmotion = async () => {
    // Validate prerequisites
    if (!videoRef) {
      console.error("[Capture] Video ref not available");
      setApiError("Video source not ready. Please wait and try again.");
      return;
    }
    
    if (!canvasRef) {
      console.error("[Capture] Canvas ref not available");
      setApiError("Canvas not available. Please try again.");
      return;
    }
    
    if (!session.session_id) {
      console.error("[Capture] Session ID not available");
      setApiError("Session not initialized. Please refresh the page.");
      return;
    }
    
    if (!session.cognitive_data) {
      console.error("[Capture] Cognitive data not available");
      setApiError("Cognitive data not available. Please complete the pre-test.");
      return;
    }

    console.log("[Capture] All prerequisites met, starting emotion capture...");
    setEmotionLoading(true);
    setApiError(null);

    try {
      console.log("[Capture] Getting canvas context...");
      const context = canvasRef.getContext("2d");
      if (!context) throw new Error("Canvas context unavailable");
      
      console.log("[Capture] Drawing video frame to canvas...");
      context.drawImage(videoRef, 0, 0, canvasRef.width, canvasRef.height);

      console.log("[Capture] Converting canvas to base64 JPEG...");
      const imageDataUrl = canvasRef.toDataURL("image/jpeg");
      // Remove data URI prefix to get just the base64 string
      const imageBase64 = imageDataUrl.replace(/^data:image\/jpeg;base64,/, "");
      console.log(`[Capture] Image base64 size: ${imageBase64.length} bytes`);

      console.log(`[Capture] Calling detectEmotion API with session: ${session.session_id}`);
      const { emotion } = await detectEmotion(imageBase64, session.session_id);
      console.log(`[Capture] Emotion detected: ${emotion}`);
      
      setDetectedEmotion(emotion);

      console.log("[Capture] Stopping video tracks...");
      videoStream?.getTracks().forEach(track => track.stop());
      setWebcamActive(false);

      console.log("[Capture] Requesting song recommendations...");
      setSongsLoading(true);
      const songs = await recommendLive(emotion, session.session_id, session.cognitive_data);
      console.log(`[Capture] Received ${songs.length} song recommendations`);
      
      setRecommendedSongs(songs);
      setSongsLoading(false);
      
      console.log("[Capture] Emotion capture complete!");
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      console.error("[Capture] Error:", errorMsg);
      console.error("[Capture] Full error:", err);
      setApiError(`Error: ${errorMsg}. Please try again.`);
    } finally {
      setEmotionLoading(false);
    }
  };

  // Function: Play song
  const playSong = (song: any) => {
    try {
      if (audioRef.current) {
        audioRef.current.pause();
      }

      // Convert relative URL to absolute URL for audio playback
      let audioUrl = song.audio_url;
      if (audioUrl.startsWith("/")) {
        // Relative URL - make it absolute
        const baseUrl = window.location.origin;
        audioUrl = baseUrl + audioUrl;
        console.log(`[Playback] Converted relative URL to absolute: ${audioUrl}`);
      }
      console.log(`[Playback] Playing song: ${song.title} from ${audioUrl}`);

      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play();
        
        audioRef.current.onerror = () => {
          console.error(`[Playback] Failed to load audio: ${audioUrl}`);
          setCurrentPlayingSongId(null);
          setCurrentPlayingSong(null);
          setCurrentAudio(null);
        };

        audioRef.current.onended = () => {
          console.log(`[Playback] Song ended: ${song.title}`);
          setCurrentPlayingSongId(null);
          setCurrentPlayingSong(null);
          setCurrentAudio(null);
        };
      }

      setCurrentAudio(audioRef.current);
      setCurrentPlayingSongId(getSongId(song));
      setCurrentPlayingSong(song);
    } catch (err) {
      console.error("[Playback] Error:", err);
    }
  };

  // Function: Pause song
  const pauseSong = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setCurrentPlayingSongId(null);
      setCurrentPlayingSong(null);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-4 sm:space-y-6 pb-6">
      {/* Top: Current emotion */}
      <div className="grid grid-cols-1 sm:grid-cols-1 gap-3 sm:gap-4">
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.3 }} className="glass-card p-4 sm:p-6 text-center">
          <p className="text-[10px] sm:text-xs text-muted-foreground uppercase tracking-wider mb-2">Detected Emotion</p>
          {session.detected_emotion ? (
            <motion.p
              key={session.detected_emotion}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-2xl sm:text-4xl font-display font-bold gradient-text"
            >
              {session.detected_emotion}
            </motion.p>
          ) : (
            <p className="text-2xl sm:text-4xl font-display font-bold text-muted-foreground">Waiting...</p>
          )}
        </motion.div>
      </div>

      {/* Main panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Camera / Emotion detection */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card p-4 sm:p-5 space-y-3 sm:space-y-4">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Camera className="w-4 h-4" />
            <span className="text-xs sm:text-sm font-medium">Live Emotion Detection</span>
            {session.detected_emotion && <span className="ml-auto w-2 h-2 rounded-full bg-success" />}
          </div>

          {!session.detected_emotion && (
            <div className="aspect-video rounded-lg bg-muted/30 border border-border overflow-hidden">
              <video ref={setVideoRef} autoPlay playsInline className="w-full h-full object-cover" />
            </div>
          )}
          
          {/* Canvas always available for capture, hidden by default */}
          <canvas ref={setCanvasRef} className="hidden" width={640} height={480} />

          {apiError && (
            <div className="p-3 rounded-lg bg-destructive/10 text-destructive text-xs">
              {apiError}
              <button onClick={() => setApiError(null)} className="ml-2 text-xs underline">
                Dismiss
              </button>
            </div>
          )}

          {!session.detected_emotion && (
            <button
              onClick={handleCaptureEmotion}
              disabled={emotionLoading || !webcamActive || !session.session_id}
              className="glow-button w-full"
            >
              {emotionLoading ? "Detecting..." : session.session_id ? "Capture Emotion" : "Initializing Session..."}
            </button>
          )}
        </motion.div>

        {/* Songs playlist */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-card p-4 sm:p-5 space-y-3 sm:space-y-4">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Music className="w-4 h-4" />
            <span className="text-xs sm:text-sm font-medium">Recommended Songs</span>
          </div>

          {songsLoading ? (
            <p className="text-xs text-muted-foreground">Loading recommendations...</p>
          ) : session.recommended_songs && session.recommended_songs.length > 0 ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
               {session.recommended_songs.filter(Boolean).map(song => (
                 <div
                   key={getSongId(song)}
                   className={`flex items-center gap-3 p-3 rounded-lg border transition-colors ${
                     currentPlayingSongId === getSongId(song)
                       ? "bg-primary/10 border-primary"
                       : "bg-muted/30 border-border hover:border-primary/50"
                   }`}
                 >
                   <button
                     onClick={() =>
                       currentPlayingSongId === getSongId(song) ? pauseSong() : playSong(song)
                     }
                    className="flex-shrink-0 w-8 h-8 rounded-lg bg-primary/20 hover:bg-primary/30 flex items-center justify-center text-primary transition-colors"
                  >
                     {currentPlayingSongId === getSongId(song) ? "⏸" : "▶"}
                  </button>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs sm:text-sm font-medium truncate">{song.title}</p>
                    <p className="text-[10px] text-muted-foreground">
                      {song.rasa} • {(song.confidence * 100).toFixed(0)}% match
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground">Capture your emotion to get recommendations</p>
          )}
        </motion.div>
      </div>

      {/* Bottom player + controls */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="space-y-4">
        {/* Audio Player */}
        <AudioPlayer
          song={currentPlayingSong}
          isPlaying={currentPlayingSongId !== null}
          onPlay={playSong}
          onPause={pauseSong}
          audioRef={audioRef}
        />

        {/* End Session Button */}
        <div className="glass-card p-3 sm:p-4 flex justify-between items-center">
          <div className="flex items-center gap-2 flex-1">
            <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
            <p className="text-xs sm:text-sm text-muted-foreground">Session Active</p>
          </div>
          <button
            onClick={() => setStep("post-test")}
            className="flex items-center gap-1 text-[10px] sm:text-xs px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg bg-destructive/10 text-destructive hover:bg-destructive/20 transition-colors"
          >
            <Square className="w-3 h-3" />
            End Session
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default LiveSession;

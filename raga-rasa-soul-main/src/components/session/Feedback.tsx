import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useSession } from "@/context/SessionContext";
import { rateSong, recommendFinal } from "@/services/api";
import { getUserId } from "@/utils/userIdentity";
import { Star, MessageSquare } from "lucide-react";

const Feedback = () => {
  const navigate = useNavigate();
  const { session, setSessionRating, setSessionComment, resetSession } = useSession();
  const [rating, setRating] = useState(0);
  const [hoveredStar, setHoveredStar] = useState(0);
  const [comment, setComment] = useState("");
  const [songRatings, setSongRatings] = useState<{ [key: string]: number }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const getSongId = (song: any): string => {
    if (!song) return "";
    return song.song_id || song._id || "";
  };

  const handleSubmit = async () => {
    if (rating === 0) return;

    setIsSubmitting(true);
    setApiError(null);

    try {
      const userId = getUserId();

      const feedback = {
        mood_after: comment || "No comment",
        session_rating: rating,
        comment: comment
      };

      if (session.detected_emotion && session.session_id && session.cognitive_data) {
        // Persist session-level feedback and final recommendations server-side
        await recommendFinal(
          session.detected_emotion,
          session.session_id,
          session.cognitive_data,
          feedback
        );
      }

      const ratingPromises = Object.entries(songRatings)
        .filter(([songId]) => !!songId)
        .map(([songId, songRating]) =>
          rateSong(userId, songId, songRating as number, session.session_id!, feedback)
        );

      await Promise.all(ratingPromises);

      setSessionRating(rating);
      setSessionComment(comment);

      resetSession();
      navigate("/dashboard/profile");
    } catch (err) {
      setApiError("Failed to submit feedback. Please try again.");
      console.error("Feedback submission error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto space-y-5 sm:space-y-6 pb-6">
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="text-center">
        <h1 className="section-title text-xl sm:text-2xl">Session Complete! 🎉</h1>
        <p className="text-muted-foreground text-sm mt-1">How was your experience?</p>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="glass-card p-6 sm:p-8 space-y-6 sm:space-y-8">
        {/* Star rating */}
        <div className="text-center space-y-3">
          <p className="text-xs sm:text-sm text-muted-foreground">How helpful was this session?</p>
          <div className="flex justify-center gap-1.5 sm:gap-2">
            {[1, 2, 3, 4, 5].map(s => (
              <motion.button
                key={s}
                whileHover={{ scale: 1.15 }}
                whileTap={{ scale: 0.95 }}
                onMouseEnter={() => setHoveredStar(s)}
                onMouseLeave={() => setHoveredStar(0)}
                onClick={() => setRating(s)}
              >
                <Star
                  className={`w-8 h-8 sm:w-10 sm:h-10 transition-colors duration-200 ${
                    s <= (hoveredStar || rating) ? "fill-warning text-warning" : "text-muted"
                  }`}
                />
              </motion.button>
            ))}
          </div>
          {rating > 0 && (
            <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-xs text-muted-foreground">
              {["", "Poor", "Fair", "Good", "Great", "Excellent"][rating]}
            </motion.p>
          )}
        </div>

        {/* Song ratings */}
        {session.recommended_songs && session.recommended_songs.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass-card p-6 space-y-4 bg-muted/20"
          >
            <h3 className="font-display font-semibold text-foreground">Rate the songs:</h3>
            <div className="space-y-3 max-h-48 overflow-y-auto">
              {session.recommended_songs.filter(Boolean).map(song => (
                <div
                  key={getSongId(song)}
                  className="flex items-center justify-between gap-3 p-3 rounded-lg bg-muted/20"
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium text-foreground">{song.title}</p>
                    <p className="text-xs text-muted-foreground">{song.rasa}</p>
                  </div>
                  <div className="flex gap-1">
                    {[1, 2, 3, 4, 5].map(star => (
                      <button
                        key={star}
                        onClick={() =>
                            setSongRatings(prev => ({
                              ...prev,
                              [getSongId(song)]: star
                            }))
                          }
                        className={`w-6 h-6 rounded text-xs font-bold transition-colors ${
                          star <= (songRatings[getSongId(song)] || 0)
                            ? "bg-warning text-white"
                            : "bg-muted text-muted-foreground hover:bg-muted/80"
                        }`}
                      >
                        ★
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Comment */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-muted-foreground">
            <MessageSquare className="w-4 h-4" />
            <span className="text-xs sm:text-sm">Comments (optional)</span>
          </div>
          <textarea
            value={comment}
            onChange={e => setComment(e.target.value)}
            placeholder="Share your thoughts about the session..."
            className="w-full h-24 sm:h-28 p-3 rounded-lg bg-muted border border-border text-foreground text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none transition-shadow"
          />
        </div>

        {/* Error message */}
        {apiError && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="p-3 rounded-lg bg-destructive/10 text-destructive text-xs"
          >
            {apiError}
          </motion.div>
        )}

        <button
          onClick={handleSubmit}
          disabled={rating === 0 || isSubmitting}
          className={`glow-button w-full transition-all duration-300 ${rating === 0 || isSubmitting ? "opacity-40 cursor-not-allowed !shadow-none" : ""}`}
        >
          {isSubmitting ? "Submitting..." : "Finish Session"}
        </button>
      </motion.div>
    </div>
  );
};

export default Feedback;

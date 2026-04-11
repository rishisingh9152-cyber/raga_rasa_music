import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { useSession } from "@/context/SessionContext";
import { COLOR_OPTIONS, MEMORY_WORDS } from "@/data/testConstants";
import { recommendFinal } from "@/services/api";
import { Zap, Brain, Smile, ArrowRight, TrendingUp, TrendingDown, SkipForward } from "lucide-react";

const PostTest = () => {
  const { session, setStep, setPostTestResults, setRecommendedSongs } = useSession();
  const [phase, setPhase] = useState<"reaction" | "memory-show" | "memory-recall" | "mood" | "results">("reaction");

  const [targetColor, setTargetColor] = useState("");
  const [reactionStart, setReactionStart] = useState(0);
  const [reactionTimes, setReactionTimes] = useState<number[]>([]);
  const [reactionRound, setReactionRound] = useState(0);
  const [memoryInput, setMemoryInput] = useState("");
  const [memoryScore, setMemoryScore] = useState(0);
  const [mood, setMood] = useState(5);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const startReactionRound = useCallback(() => {
    const target = COLOR_OPTIONS[Math.floor(Math.random() * COLOR_OPTIONS.length)];
    setTargetColor(target.name);
    setReactionStart(Date.now());
  }, []);

  useEffect(() => {
    if (phase === "reaction" && reactionRound < 3) {
      const t = setTimeout(startReactionRound, 500);
      return () => clearTimeout(t);
    }
    if (phase === "reaction" && reactionRound >= 3) setPhase("memory-show");
  }, [phase, reactionRound, startReactionRound]);

  const handleColorClick = (name: string) => {
    if (name === targetColor) {
      setReactionTimes(prev => [...prev, Date.now() - reactionStart]);
      setReactionRound(r => r + 1);
    }
  };

  useEffect(() => {
    if (phase === "memory-show") {
      const t = setTimeout(() => setPhase("memory-recall"), 4000);
      return () => clearTimeout(t);
    }
  }, [phase]);

  const handleMemorySubmit = () => {
    const recalled = memoryInput.toLowerCase().split(/[,\s]+/).filter(Boolean);
    const score = MEMORY_WORDS.filter(w => recalled.includes(w.toLowerCase())).length;
    setMemoryScore(score);
    setPhase("mood");
  };

  const handleMoodSubmit = async () => {
    const avgReaction = reactionTimes.length > 0 ? Math.round(reactionTimes.reduce((a, b) => a + b, 0) / reactionTimes.length) : 0;
    setPostTestResults({ reactionTime: avgReaction, memoryScore, moodLevel: mood });

    try {
      setIsSubmitting(true);

      const feedback = {
        mood_after: `${mood}`,
        session_rating: 0,
        comment: ""
      };

      const finalSongs = await recommendFinal(
        session.detected_emotion!,
        session.session_id!,
        session.cognitive_data!,
        feedback
      );

      setRecommendedSongs(finalSongs);
      setPhase("results");
    } catch (err) {
      console.error("Final recommendations error:", err);
      setPhase("results");
    } finally {
      setIsSubmitting(false);
    }
  };

  const pre = session.preTestResults;
  const post = { reactionTime: reactionTimes.length > 0 ? Math.round(reactionTimes.reduce((a, b) => a + b, 0) / reactionTimes.length) : 0, memoryScore, moodLevel: mood };

  const Comparison = ({ label, before, after, unit, better }: { label: string; before: number; after: number; unit: string; better: "lower" | "higher" }) => {
    const improved = better === "lower" ? after < before : after > before;
    return (
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 p-3 sm:p-4 rounded-lg bg-muted/30">
        <span className="text-xs sm:text-sm text-muted-foreground">{label}</span>
        <div className="flex items-center gap-2 sm:gap-3">
          <span className="text-xs sm:text-sm text-foreground">{before}{unit}</span>
          <ArrowRight className="w-3 h-3 sm:w-4 sm:h-4 text-muted-foreground" />
          <span className={`text-xs sm:text-sm font-bold ${improved ? "text-success" : "text-destructive"}`}>{after}{unit}</span>
          {improved ? <TrendingUp className="w-3 h-3 sm:w-4 sm:h-4 text-success" /> : <TrendingDown className="w-3 h-3 sm:w-4 sm:h-4 text-destructive" />}
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-2xl mx-auto space-y-5 sm:space-y-6 pb-6">
      <div className="flex items-start sm:items-center justify-between gap-3">
        <div>
          <h1 className="section-title text-lg sm:text-2xl">Post-Session Assessment</h1>
          <p className="text-muted-foreground text-xs sm:text-sm mt-0.5">Let's measure your improvement.</p>
        </div>
        <button onClick={() => setStep("feedback")} className="flex items-center gap-1 text-[10px] sm:text-xs text-muted-foreground hover:text-primary transition-colors px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-lg bg-muted/50 whitespace-nowrap flex-shrink-0">
          <SkipForward className="w-3 h-3" />
          Skip Test (Admin)
        </button>
      </div>

      {/* Progress */}
      <div className="flex gap-2">
        {["reaction", "memory", "mood", "results"].map((p, i) => (
          <div key={p} className={`h-1 flex-1 rounded-full transition-all duration-500 ${
            (phase === "reaction" && i === 0) || (phase.startsWith("memory") && i === 1) || (phase === "mood" && i === 2) || (phase === "results" && i === 3)
              ? "gradient-bg" : "bg-muted"
          }`} />
        ))}
      </div>

      <motion.div key={phase} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="glass-card p-5 sm:p-6">
        {phase === "reaction" && (
          <div className="text-center space-y-5 sm:space-y-6">
            <div className="flex items-center justify-center gap-2 text-primary">
              <Zap className="w-5 h-5" />
              <h2 className="font-display font-semibold text-sm sm:text-base">Reaction Test ({reactionRound + 1}/3)</h2>
            </div>
            <p className="text-xs sm:text-sm text-muted-foreground">Click <span className="font-bold text-foreground">{targetColor}</span>!</p>
            <div className="grid grid-cols-2 gap-3 sm:gap-4 max-w-xs mx-auto">
              {COLOR_OPTIONS.map(c => (
                <motion.button key={c.name} whileTap={{ scale: 0.92 }} onClick={() => handleColorClick(c.name)}
                  className="h-16 sm:h-20 rounded-xl font-semibold text-sm sm:text-base text-primary-foreground transition-transform hover:scale-105"
                  style={{ backgroundColor: c.color }}>{c.name}</motion.button>
              ))}
            </div>
          </div>
        )}

        {phase === "memory-show" && (
          <div className="text-center space-y-5 sm:space-y-6">
            <div className="flex items-center justify-center gap-2 text-primary"><Brain className="w-5 h-5" /><h2 className="font-display font-semibold text-sm sm:text-base">Memory Test</h2></div>
            <div className="flex flex-wrap justify-center gap-2 sm:gap-3">
              {MEMORY_WORDS.map((w, i) => (
                <motion.span key={w} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.1 }}
                  className="px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg bg-primary/10 text-primary font-medium text-base sm:text-lg">{w}</motion.span>
              ))}
            </div>
            <p className="text-[10px] sm:text-xs text-muted-foreground animate-pulse">Memorize these words...</p>
          </div>
        )}

        {phase === "memory-recall" && (
          <div className="text-center space-y-5 sm:space-y-6">
            <div className="flex items-center justify-center gap-2 text-primary"><Brain className="w-5 h-5" /><h2 className="font-display font-semibold text-sm sm:text-base">Recall</h2></div>
            <textarea value={memoryInput} onChange={e => setMemoryInput(e.target.value)} placeholder="Type remembered words..."
              className="w-full h-20 sm:h-24 p-3 rounded-lg bg-muted border border-border text-foreground text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none transition-shadow" />
            <button onClick={handleMemorySubmit} className="glow-button">Submit</button>
          </div>
        )}

        {phase === "mood" && (
          <div className="text-center space-y-5 sm:space-y-6">
            <div className="flex items-center justify-center gap-2 text-primary"><Smile className="w-5 h-5" /><h2 className="font-display font-semibold text-sm sm:text-base">Current Mood</h2></div>
            <div className="px-2">
              <input type="range" min={1} max={10} value={mood} onChange={e => setMood(Number(e.target.value))} className="w-full accent-primary" />
              <div className="flex justify-between text-xs text-muted-foreground mt-2"><span>😔 1</span><span className="text-xl sm:text-2xl font-display font-bold text-primary">{mood}</span><span>😊 10</span></div>
            </div>
            <button onClick={handleMoodSubmit} disabled={isSubmitting} className="glow-button">{isSubmitting ? "Loading..." : "See Results"}</button>
          </div>
        )}

        {phase === "results" && pre && (
          <div className="space-y-3 sm:space-y-4">
            <h2 className="font-display font-semibold text-center text-foreground text-base sm:text-lg">Session Comparison</h2>
            <Comparison label="Reaction Time" before={pre.reactionTime} after={post.reactionTime} unit="ms" better="lower" />
            <Comparison label="Memory Score" before={pre.memoryScore} after={post.memoryScore} unit={`/${MEMORY_WORDS.length}`} better="higher" />
            <Comparison label="Mood Level" before={pre.moodLevel} after={post.moodLevel} unit="/10" better="higher" />
            <div className="text-center pt-2">
              <button onClick={() => setStep("feedback")} className="glow-button">Continue to Feedback</button>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default PostTest;

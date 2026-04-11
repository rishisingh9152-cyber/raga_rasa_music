import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { useSession } from "@/context/SessionContext";
import { COLOR_OPTIONS, MEMORY_WORDS } from "@/data/testConstants";
import { Zap, Brain, Smile, SkipForward } from "lucide-react";

const PreTest = () => {
  const { setStep, setPreTestResults, setCognitiveData, skipToLive } = useSession();
  const [phase, setPhase] = useState<"reaction" | "memory-show" | "memory-recall" | "mood">("reaction");

  const [targetColor, setTargetColor] = useState("");
  const [reactionStart, setReactionStart] = useState(0);
  const [reactionTimes, setReactionTimes] = useState<number[]>([]);
  const [reactionRound, setReactionRound] = useState(0);
  const [totalColorAttempts, setTotalColorAttempts] = useState(0);

  const [memoryInput, setMemoryInput] = useState("");
  const [memoryScore, setMemoryScore] = useState(0);
  const [mood, setMood] = useState(5);

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
    if (phase === "reaction" && reactionRound >= 3) {
      setPhase("memory-show");
    }
  }, [phase, reactionRound, startReactionRound]);

  const handleColorClick = (name: string) => {
    setTotalColorAttempts(prev => prev + 1);
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

  const handleSubmit = () => {
    const avgReaction = reactionTimes.length > 0 ? Math.round(reactionTimes.reduce((a, b) => a + b, 0) / reactionTimes.length) : 0;
    setPreTestResults({ reactionTime: avgReaction, memoryScore, moodLevel: mood });

    // Compute cognitive data
    const accuracy_score = totalColorAttempts > 0
      ? (reactionTimes.length / totalColorAttempts) * 100
      : 0;

    const cognitiveData = {
      memory_score: memoryScore,
      reaction_time: avgReaction,
      accuracy_score: accuracy_score
    };

    // Store cognitive data in context
    setCognitiveData(cognitiveData);

    setStep("live");
  };

  return (
    <div className="max-w-2xl mx-auto space-y-5 sm:space-y-6 pb-6">
      <div className="flex items-start sm:items-center justify-between gap-3">
        <div>
          <h1 className="section-title text-lg sm:text-2xl">Pre-Session Assessment</h1>
          <p className="text-muted-foreground text-xs sm:text-sm mt-0.5">Complete these tests to establish your baseline.</p>
        </div>
        <button onClick={skipToLive} className="flex items-center gap-1 text-[10px] sm:text-xs text-muted-foreground hover:text-primary transition-colors px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-lg bg-muted/50 whitespace-nowrap flex-shrink-0">
          <SkipForward className="w-3 h-3" />
          Skip (Admin)
        </button>
      </div>

      {/* Progress */}
      <div className="flex gap-2">
        {["reaction", "memory-show", "mood"].map((p, i) => (
          <div key={p} className={`h-1 flex-1 rounded-full transition-all duration-500 ${
            (phase === "reaction" && i === 0) || (phase.startsWith("memory") && i === 1) || (phase === "mood" && i === 2)
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
            <p className="text-xs sm:text-sm text-muted-foreground">Click the <span className="font-bold text-foreground">{targetColor}</span> button as fast as you can!</p>
            <div className="grid grid-cols-2 gap-3 sm:gap-4 max-w-xs mx-auto">
              {COLOR_OPTIONS.map(c => (
                <motion.button
                  key={c.name}
                  whileTap={{ scale: 0.92 }}
                  onClick={() => handleColorClick(c.name)}
                  className="h-16 sm:h-20 rounded-xl font-semibold text-sm sm:text-base text-primary-foreground transition-transform hover:scale-105"
                  style={{ backgroundColor: c.color }}
                >
                  {c.name}
                </motion.button>
              ))}
            </div>
          </div>
        )}

        {phase === "memory-show" && (
          <div className="text-center space-y-5 sm:space-y-6">
            <div className="flex items-center justify-center gap-2 text-primary">
              <Brain className="w-5 h-5" />
              <h2 className="font-display font-semibold text-sm sm:text-base">Memory Test</h2>
            </div>
            <p className="text-xs sm:text-sm text-muted-foreground">Memorize these words:</p>
            <div className="flex flex-wrap justify-center gap-2 sm:gap-3">
              {MEMORY_WORDS.map((w, i) => (
                <motion.span
                  key={w}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.1 }}
                  className="px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg bg-primary/10 text-primary font-medium text-base sm:text-lg"
                >
                  {w}
                </motion.span>
              ))}
            </div>
            <p className="text-[10px] sm:text-xs text-muted-foreground animate-pulse">Disappearing in a few seconds...</p>
          </div>
        )}

        {phase === "memory-recall" && (
          <div className="text-center space-y-5 sm:space-y-6">
            <div className="flex items-center justify-center gap-2 text-primary">
              <Brain className="w-5 h-5" />
              <h2 className="font-display font-semibold text-sm sm:text-base">Recall the Words</h2>
            </div>
            <textarea
              value={memoryInput}
              onChange={e => setMemoryInput(e.target.value)}
              placeholder="Type the words you remember, separated by commas..."
              className="w-full h-20 sm:h-24 p-3 rounded-lg bg-muted border border-border text-foreground text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none transition-shadow"
            />
            <button onClick={handleMemorySubmit} className="glow-button">Submit</button>
          </div>
        )}

        {phase === "mood" && (
          <div className="text-center space-y-5 sm:space-y-6">
            <div className="flex items-center justify-center gap-2 text-primary">
              <Smile className="w-5 h-5" />
              <h2 className="font-display font-semibold text-sm sm:text-base">Current Mood</h2>
            </div>
            <p className="text-xs sm:text-sm text-muted-foreground">How are you feeling right now? (1 = very low, 10 = excellent)</p>
            <div className="space-y-2 px-2">
              <input
                type="range"
                min={1}
                max={10}
                value={mood}
                onChange={e => setMood(Number(e.target.value))}
                className="w-full accent-primary"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>😔 1</span>
                <span className="text-xl sm:text-2xl font-display font-bold text-primary">{mood}</span>
                <span>😊 10</span>
              </div>
            </div>
            <button onClick={handleSubmit} className="glow-button">Start Session</button>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default PreTest;

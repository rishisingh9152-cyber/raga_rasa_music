import { motion } from "framer-motion";
import { Star, Clock, Music, AlertCircle } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell, ResponsiveContainer } from "recharts";
import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { getUserSessionHistory, getMoodTrends, calculateUserStats, getCompletedSessions } from "@/services/userProfileService";
import type { SessionHistory, UserStats, MoodTrend } from "@/services/userProfileService";

const anim = (i: number) => ({
  initial: { opacity: 0, y: 15 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-30px" },
  transition: { delay: i * 0.06, duration: 0.4 },
});

const Profile = () => {
  const { token, isAuthenticated } = useAuth();
  const [sessionHistory, setSessionHistory] = useState<SessionHistory[]>([]);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [moodTrends, setMoodTrends] = useState<MoodTrend[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load user data on component mount
  useEffect(() => {
    const loadUserData = async () => {
      const authToken = token || localStorage.getItem("auth_token") || "guest-token";

      try {
        setIsLoading(true);
        setError(null);

        // Fetch session history
        const sessions = await getUserSessionHistory(authToken);
        setSessionHistory(sessions);

        // Calculate user stats
        const stats = await calculateUserStats(authToken);
        setUserStats(stats);

        // Get mood trends
        const trends = await getMoodTrends(authToken);
        setMoodTrends(trends);
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : "Failed to load profile data";
        console.error("Profile load error:", errorMsg);
        setError(errorMsg);
      } finally {
        setIsLoading(false);
      }
    };

    loadUserData();
  }, [token, isAuthenticated]);

  // Prepare mood trend data for chart
  const moodTrendChartData = moodTrends.reduce((acc: any[], trend) => {
    const existing = acc.find(item => item.session === trend.date);
    if (existing) {
      existing[trend.emotion.toLowerCase()] = trend.session_count;
    } else {
      acc.push({
        session: trend.date,
        [trend.emotion.toLowerCase()]: trend.session_count
      });
    }
    return acc;
  }, []);

  // Prepare emotion distribution for pie chart
  const emotionCounts: Record<string, number> = {};
  sessionHistory.forEach(session => {
    if (session.emotion) {
      emotionCounts[session.emotion] = (emotionCounts[session.emotion] || 0) + 1;
    }
  });

  const emotionColors: Record<string, string> = {
    "Happy": "hsl(60, 100%, 50%)",
    "Sad": "hsl(240, 100%, 50%)",
    "Angry": "hsl(0, 100%, 50%)",
    "Calm": "hsl(120, 100%, 50%)",
    "Surprised": "hsl(30, 100%, 50%)",
    "Fearful": "hsl(270, 100%, 50%)",
    "Disgusted": "hsl(150, 100%, 50%)",
    "Neutral": "hsl(0, 0%, 50%)",
  };

  const emotionDistributionData = Object.entries(emotionCounts).map(([emotion, count]) => ({
    name: emotion,
    value: count,
    fill: emotionColors[emotion] || "hsl(220, 60%, 50%)"
  }));

  // Get top ragas from sessions
  const ragaCounts: Record<string, { count: number; emotion: string }> = {};
  sessionHistory.forEach(session => {
    if (session.rasa) {
      if (!ragaCounts[session.rasa]) {
        ragaCounts[session.rasa] = { count: 0, emotion: session.emotion || "Unknown" };
      }
      ragaCounts[session.rasa].count++;
    }
  });

  const topRagas = Object.entries(ragaCounts)
    .map(([name, data]) => ({ name, emotion: data.emotion, count: data.count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto space-y-6 sm:space-y-8 pb-6">
        <motion.div {...anim(0)}>
          <h1 className="section-title text-xl sm:text-2xl mb-1">Your Profile</h1>
          <p className="text-muted-foreground text-sm">Analytics and session history</p>
        </motion.div>
        <motion.div {...anim(1)} className="glass-card p-6 text-center">
          <p className="text-muted-foreground">Loading your profile data...</p>
        </motion.div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto space-y-6 sm:space-y-8 pb-6">
        <motion.div {...anim(0)}>
          <h1 className="section-title text-xl sm:text-2xl mb-1">Your Profile</h1>
          <p className="text-muted-foreground text-sm">Analytics and session history</p>
        </motion.div>
        <motion.div {...anim(1)} className="glass-card p-6 text-center border border-destructive/50">
          <AlertCircle className="w-8 h-8 mx-auto mb-4 text-destructive" />
          <p className="text-destructive mb-2">{error}</p>
          <p className="text-muted-foreground text-sm">Please try refreshing the page or logging in again</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 sm:space-y-8 pb-6">
      <motion.div {...anim(0)}>
        <h1 className="section-title text-xl sm:text-2xl mb-1">Your Profile</h1>
        <p className="text-muted-foreground text-sm">Analytics and session history</p>
      </motion.div>

      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {[
          { label: "Total Sessions", value: userStats?.total_sessions || 0 },
          { label: "Avg Rating", value: `${userStats?.average_mood_rating.toFixed(1) || 0} ★` },
          { label: "Total Time", value: `${Math.round((userStats?.average_session_duration || 0) * (userStats?.completed_sessions || 0))} min` },
          { label: "Top Raga", value: userStats?.most_used_rasa || "None" },
        ].map((s, i) => (
          <motion.div key={s.label} {...anim(i + 1)} className="stat-card text-center">
            <p className="text-xl sm:text-2xl font-display font-bold text-foreground">{s.value}</p>
            <p className="text-[10px] sm:text-xs text-muted-foreground mt-1">{s.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        <motion.div {...anim(5)} className="glass-card p-4 sm:p-5">
          <h3 className="font-display font-semibold mb-3 sm:mb-4 text-foreground text-sm sm:text-base">Mood Change Trend</h3>
          {moodTrendChartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={moodTrendChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(250,15%,18%)" />
                <XAxis dataKey="session" tick={{ fill: "hsl(220,10%,55%)", fontSize: 11 }} />
                <YAxis domain={[0, "dataMax"]} tick={{ fill: "hsl(220,10%,55%)", fontSize: 11 }} width={30} />
                <Tooltip contentStyle={{ background: "hsl(250,20%,12%)", border: "1px solid hsl(250,15%,22%)", borderRadius: 8, color: "hsl(220,20%,92%)" }} />
                {Object.keys(emotionCounts).map((emotion, idx) => (
                  <Line
                    key={emotion}
                    type="monotone"
                    dataKey={emotion.toLowerCase()}
                    stroke={emotionColors[emotion] || `hsl(${idx * 60}, 60%, 50%)`}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    name={emotion}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-muted-foreground text-center py-10">No mood data yet. Complete sessions to see trends.</p>
          )}
        </motion.div>

        <motion.div {...anim(6)} className="glass-card p-4 sm:p-5">
          <h3 className="font-display font-semibold mb-3 sm:mb-4 text-foreground text-sm sm:text-base">Emotional Distribution</h3>
          {emotionDistributionData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={emotionDistributionData} dataKey="value" cx="50%" cy="50%" outerRadius={70} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={false} fontSize={10}>
                  {emotionDistributionData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "hsl(250,20%,12%)", border: "1px solid hsl(250,15%,22%)", borderRadius: 8, color: "hsl(220,20%,92%)" }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-muted-foreground text-center py-10">No emotion data yet. Complete sessions to see distribution.</p>
          )}
        </motion.div>
      </div>

      {/* Top Ragas */}
      <motion.div {...anim(7)} className="glass-card p-4 sm:p-5">
        <h3 className="font-display font-semibold mb-3 sm:mb-4 text-foreground text-sm sm:text-base">Most Recommended Ragas</h3>
        {topRagas.length > 0 ? (
          <div className="space-y-2 sm:space-y-3">
            {topRagas.map((r, i) => (
              <div key={r.name} className="flex items-center gap-3 sm:gap-4">
                <span className="text-base sm:text-lg font-display font-bold text-primary w-6">#{i + 1}</span>
                <Music className="w-4 h-4 text-muted-foreground hidden sm:block" />
                <span className="flex-1 text-foreground text-xs sm:text-sm truncate">{r.name}</span>
                <span className="text-[10px] sm:text-xs px-2 py-0.5 sm:py-1 rounded-full bg-primary/10 text-primary">{r.emotion}</span>
                <span className="text-[10px] sm:text-xs text-muted-foreground whitespace-nowrap">{r.count} sessions</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground text-center py-4">No raga data yet. Complete sessions to see recommendations.</p>
        )}
      </motion.div>

      {/* Session History */}
      <motion.div {...anim(8)} className="glass-card p-4 sm:p-5">
        <h3 className="font-display font-semibold mb-3 sm:mb-4 text-foreground text-sm sm:text-base">Session History</h3>
        {sessionHistory.length > 0 ? (
          <div className="space-y-2 sm:space-y-3">
            {sessionHistory.map((s) => (
              <div key={s.session_id} className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 p-3 rounded-lg bg-muted/30">
                <div className="flex items-center gap-2 sm:gap-3">
                  <Clock className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                  <span className="text-xs sm:text-sm text-foreground whitespace-nowrap">
                    {new Date(s.created_at).toLocaleDateString()}
                  </span>
                  {s.emotion && (
                    <span className="text-[10px] sm:text-xs px-2 py-0.5 rounded-full bg-secondary/20 text-secondary">{s.emotion}</span>
                  )}
                </div>
                <span className="text-xs sm:text-sm text-muted-foreground flex-1 truncate">{s.rasa || "Unknown"} · {s.status}</span>
                <div className="flex items-center gap-2 sm:gap-3">
                  <span className={`text-[10px] sm:text-xs font-medium ${s.status === 'completed' ? "text-success" : "text-warning"}`}>
                    {s.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground text-center py-4">No sessions yet. Start a session to begin tracking your therapy journey.</p>
        )}
      </motion.div>
    </div>
  );
};

export default Profile;

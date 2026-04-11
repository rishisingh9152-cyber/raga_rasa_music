import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Music, Brain, Heart, Sparkles, LogIn, UserPlus, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const Landing = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <div className="min-h-screen gradient-hero-bg relative overflow-hidden flex flex-col">
      {/* Navigation Bar */}
      <div className="absolute top-0 left-0 right-0 z-20 flex justify-between items-center px-6 py-4">
        <div className="flex items-center gap-2">
          <Music className="w-8 h-8 text-primary" />
          <span className="text-xl font-bold text-white">Raga-Rasa-Laya</span>
        </div>
        <div className="flex gap-3">
          {!isAuthenticated ? (
            <>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate("/login")}
                className="flex items-center gap-2 px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition text-sm"
              >
                <LogIn className="w-4 h-4" />
                Login
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate("/register")}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg transition text-sm"
              >
                <UserPlus className="w-4 h-4" />
                Register
              </motion.button>
            </>
           ) : (
             <>
               <span className="text-purple-200 text-sm">{user?.email}</span>
               <motion.button
                 whileHover={{ scale: 1.05 }}
                 whileTap={{ scale: 0.95 }}
                 onClick={() => navigate(user?.role === 'admin' ? '/admin' : '/dashboard')}
                 className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition text-sm"
               >
                 {user?.role === 'admin' ? 'Admin' : 'Dashboard'}
               </motion.button>
               <motion.button
                 whileHover={{ scale: 1.05 }}
                 whileTap={{ scale: 0.95 }}
                 onClick={() => {
                   logout();
                   navigate('/');
                 }}
                 className="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition text-sm"
               >
                 <LogOut className="w-4 h-4" />
                 Logout
               </motion.button>
             </>
           )}
        </div>
      </div>

      {/* Animated orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-64 sm:w-96 h-64 sm:h-96 rounded-full bg-primary/5 blur-3xl animate-float" />
        <div className="absolute bottom-1/4 right-1/4 w-56 sm:w-80 h-56 sm:h-80 rounded-full bg-secondary/5 blur-3xl animate-float" style={{ animationDelay: "3s" }} />
        <div className="absolute top-1/2 left-1/2 w-48 sm:w-64 h-48 sm:h-64 rounded-full bg-accent/5 blur-3xl animate-float" style={{ animationDelay: "1.5s" }} />
      </div>

      <div className="flex-1 flex flex-col items-center justify-center px-4 sm:px-6 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-3xl w-full"
        >
          <div className="flex items-center justify-center gap-2 sm:gap-3 mb-4 sm:mb-6">
            <Music className="w-6 h-6 sm:w-8 sm:h-8 text-primary" />
            <span className="text-muted-foreground text-[10px] sm:text-sm tracking-[0.2em] sm:tracking-[0.3em] uppercase font-medium">
              AI Music Therapy
            </span>
          </div>

          <h1 className="text-4xl sm:text-6xl md:text-8xl font-bold font-display gradient-text mb-3 sm:mb-4 leading-tight">
            Raga-Rasa-Laya
          </h1>

          <p className="text-sm sm:text-lg md:text-xl text-muted-foreground mb-8 sm:mb-10 max-w-xl mx-auto leading-relaxed px-2">
            AI-powered Emotion-Based Music Therapy using Indian Classical Music
          </p>

          {/* Concepts */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mb-8 sm:mb-12 max-w-2xl mx-auto">
            {[
              { icon: Music, title: "Raga", desc: "Melodic framework that evokes specific emotions" },
              { icon: Heart, title: "Rasa", desc: "The emotional essence experienced through art" },
              { icon: Brain, title: "Laya", desc: "Rhythmic tempo that regulates mental state" },
            ].map((item, i) => (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 + i * 0.15, duration: 0.5 }}
                className="glass-card p-4 sm:p-5 text-center"
              >
                <item.icon className="w-5 h-5 sm:w-6 sm:h-6 text-primary mx-auto mb-2" />
                <h3 className="font-display font-semibold text-foreground mb-1 text-sm sm:text-base">{item.title}</h3>
                <p className="text-[10px] sm:text-xs text-muted-foreground">{item.desc}</p>
              </motion.div>
            ))}
          </div>

          <motion.button
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.9, duration: 0.4 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => isAuthenticated ? navigate(user?.role === 'admin' ? '/admin' : '/dashboard') : navigate('/login')}
            className="glow-button text-sm sm:text-lg flex items-center gap-2 mx-auto animate-pulse-glow"
          >
            <Sparkles className="w-4 h-4 sm:w-5 sm:h-5" />
            {isAuthenticated ? 'Go to Dashboard' : 'Enter Experience'}
          </motion.button>
        </motion.div>
      </div>

      <footer className="text-center py-4 sm:py-6 text-muted-foreground text-[10px] sm:text-xs relative z-10">
        Raga-Rasa-Laya — Where Ancient Wisdom Meets Modern AI
      </footer>
    </div>
  );
};

export default Landing;

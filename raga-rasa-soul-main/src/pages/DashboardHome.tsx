import { motion } from "framer-motion";
import { Music, Brain, Heart, Zap, Scan, Sparkles } from "lucide-react";

const card = (i: number) => ({
  initial: { opacity: 0, y: 20 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-40px" },
  transition: { delay: i * 0.08, duration: 0.4 },
});

const DashboardHome = () => {
  return (
    <div className="max-w-5xl mx-auto space-y-8 sm:space-y-10 pb-6">
      <motion.div {...card(0)}>
        <h1 className="section-title text-xl sm:text-2xl mb-1">
          Welcome to <span className="gradient-text">RagaRasa</span>
        </h1>
        <p className="text-muted-foreground text-sm sm:text-base">
          Discover the science of emotion-based Indian classical music therapy.
        </p>
      </motion.div>

      {/* Core Concepts */}
      <section>
        <h2 className="text-base sm:text-lg font-display font-semibold mb-3 sm:mb-4 text-foreground">Core Concepts</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4">
          {[
            { icon: Music, title: "Raga", desc: "A melodic framework in Indian classical music designed to evoke specific emotional states through precise note patterns and progressions." },
            { icon: Heart, title: "Rasa", desc: "The aesthetic emotional flavor or essence experienced by the listener — the bridge between sound and feeling." },
            { icon: Zap, title: "Laya", desc: "The rhythmic tempo that regulates the listener's mental state, from slow (Vilambit) to fast (Drut)." },
          ].map((item, i) => (
            <motion.div key={item.title} {...card(i + 1)} className="glass-card-hover p-5 sm:p-6">
              <item.icon className="w-7 h-7 sm:w-8 sm:h-8 text-primary mb-3" />
              <h3 className="font-display font-semibold text-foreground mb-2">{item.title}</h3>
              <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section>
        <h2 className="text-base sm:text-lg font-display font-semibold mb-3 sm:mb-4 text-foreground">How It Works</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4">
          {[
            { icon: Scan, step: "01", title: "Detect", desc: "AI analyzes your facial expressions and physiological signals to detect your current emotional state." },
            { icon: Brain, step: "02", title: "Analyze", desc: "Our ML model maps detected emotions to the Navarasa framework and determines optimal Raga-Rasa pairing." },
            { icon: Sparkles, step: "03", title: "Recommend", desc: "A personalized Raga is recommended and played to guide your emotional state toward balance and wellbeing." },
          ].map((item, i) => (
            <motion.div key={item.title} {...card(i + 4)} className="glass-card-hover p-5 sm:p-6 relative overflow-hidden">
              <span className="absolute top-3 right-3 sm:top-4 sm:right-4 text-3xl sm:text-4xl font-display font-bold text-primary/10">{item.step}</span>
              <item.icon className="w-7 h-7 sm:w-8 sm:h-8 text-secondary mb-3" />
              <h3 className="font-display font-semibold text-foreground mb-2">{item.title}</h3>
              <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Benefits */}
      <section>
        <h2 className="text-base sm:text-lg font-display font-semibold mb-3 sm:mb-4 text-foreground">Benefits</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
          {[
            { title: "Stress Relief", desc: "Scientifically curated ragas reduce cortisol levels and promote relaxation." },
            { title: "Emotional Balance", desc: "Restore emotional equilibrium through targeted musical interventions." },
            { title: "Therapeutic Aid", desc: "Complement existing therapy with non-invasive, culturally rich sound healing." },
            { title: "Self-Awareness", desc: "Track your emotional patterns over time and build deeper self-understanding." },
          ].map((item, i) => (
            <motion.div key={item.title} {...card(i + 7)} className="glass-card p-4 sm:p-5 flex gap-3 sm:gap-4">
              <div className="w-1.5 sm:w-2 rounded-full gradient-bg flex-shrink-0" />
              <div>
                <h3 className="font-display font-semibold text-foreground mb-1 text-sm sm:text-base">{item.title}</h3>
                <p className="text-xs sm:text-sm text-muted-foreground">{item.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default DashboardHome;

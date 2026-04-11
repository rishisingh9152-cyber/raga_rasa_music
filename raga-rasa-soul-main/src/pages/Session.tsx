import { AnimatePresence, motion } from "framer-motion";
import { useSession } from "@/context/SessionContext";
import PreTest from "@/components/session/PreTest";
import LiveSession from "@/components/session/LiveSession";
import PostTest from "@/components/session/PostTest";
import Feedback from "@/components/session/Feedback";

const Session = () => {
  const { session } = useSession();

  const Component = {
    "pre-test": PreTest,
    live: LiveSession,
    "post-test": PostTest,
    feedback: Feedback,
  }[session.step];

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={session.step}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -12 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
      >
        <Component />
      </motion.div>
    </AnimatePresence>
  );
};

export default Session;

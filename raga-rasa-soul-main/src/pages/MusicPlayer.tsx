import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, Pause, SkipBack, SkipForward, Music, Star, X, ChevronDown } from "lucide-react";
import { AudioPlayer } from "@/components/AudioPlayer";

interface Song {
  _id: string;
  title: string;
  filename: string;
  audio_url: string;
  duration: string;
  rasa: string;
}

interface SongsByRasa {
  [key: string]: Song[];
}

const RASA_MAP: { [key: string]: string } = {
  "shaant": "Shaant",
  "shringar": "Shringar",
  "veer": "Veer",
  "shok": "Shok"
};

const SONGS_PER_PAGE = 15;

const MusicPlayer = () => {
   const [songsByRasa, setSongsByRasa] = useState<SongsByRasa>({});
    const [filter, setFilter] = useState("All");
    const [currentSong, setCurrentSong] = useState<Song | null>(null);
    const [playing, setPlaying] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showRatingModal, setShowRatingModal] = useState(false);
    const [rating, setRating] = useState(0);
    const [comments, setComments] = useState("");
    const [submittingRating, setSubmittingRating] = useState(false);
    const [currentPage, setCurrentPage] = useState(0);
    const [recommendedSongIds, setRecommendedSongIds] = useState<Set<string>>(new Set());
    const audioRef = useRef<HTMLAudioElement>(null);

  // Fetch songs from backend API
  useEffect(() => {
    const fetchSongs = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch("/api/songs/by-rasa");
        if (!response.ok) {
          throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
         console.log("API Response keys:", Object.keys(data));
         console.log("Song counts:", {
           Shaant: data.Shaant?.length || 0,
           Shringar: data.Shringar?.length || 0,
           Veer: data.Veer?.length || 0,
           Shok: data.Shok?.length || 0
         });
         setSongsByRasa(data);
      } catch (error) {
         const errorMsg = error instanceof Error ? error.message : "Unknown error";
         console.error("Error fetching songs:", errorMsg);
         setError(`Failed to load songs: ${errorMsg}. Make sure the backend is running on http://localhost:8080`);
         setSongsByRasa({});
      } finally {
        setLoading(false);
      }
    };

    fetchSongs();
  }, []);

  // Check for recommended songs from session/context
  useEffect(() => {
    const checkRecommendations = async () => {
      try {
        // Try to get recommended songs from session storage or backend
        const sessionData = sessionStorage.getItem("currentSession");
        if (sessionData) {
          const session = JSON.parse(sessionData);
          if (session.recommended_songs) {
            const ids = new Set(session.recommended_songs.map((s: any) => s._id || s.id));
            setRecommendedSongIds(ids);
          }
        }
      } catch (error) {
        console.error("Error checking recommendations:", error);
      }
    };

    checkRecommendations();
  }, []);

    // Handle audio playback
    useEffect(() => {
      const audio = audioRef.current;
      if (!audio || !currentSong) return;

      // Explicitly set the src before attempting to play
      if (audio.src !== currentSong.audio_url) {
        console.log('Setting audio src to:', currentSong.audio_url);
        audio.src = currentSong.audio_url;
      }

      console.log('Audio effect triggered - playing:', playing, 'song:', currentSong.title, 'src:', audio.src);
      console.log('Audio element state:', {
        src: audio.src,
        currentTime: audio.currentTime,
        duration: audio.duration,
        readyState: audio.readyState,
        networkState: audio.networkState,
        paused: audio.paused
      });

      if (playing) {
        // Ensure the audio has loaded before trying to play
        console.log('Attempting to play audio...');
        const playPromise = audio.play();
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              console.log('Audio started playing successfully');
            })
            .catch(err => {
              console.error("Play error:", err.name, err.message);
            });
        }
      } else {
        console.log('Pausing audio...');
        audio.pause();
      }
    }, [playing, currentSong]);

   // Handle audio end
   const handleAudioEnded = () => {
     navigate(1);
   };

     const playSong = (song: Song) => {
       // Always pause first when changing songs
       if (audioRef.current) {
         audioRef.current.pause();
         audioRef.current.currentTime = 0;
       }
       setCurrentSong(song);
       setPlaying(true);
       setRating(0);
       setComments("");
     };

    const handlePlay = (song: Song) => {
      playSong(song);
    };

    const handlePause = () => {
      setPlaying(false);
    };

  const navigate = (dir: 1 | -1) => {
    if (!currentSong) return;

    const filteredSongs = filter === "All" 
      ? Object.values(songsByRasa).flat()
      : songsByRasa[filter] || [];

    if (filteredSongs.length === 0) return;

    const idx = filteredSongs.findIndex(s => s._id === currentSong._id);
    const next = filteredSongs[(idx + dir + filteredSongs.length) % filteredSongs.length];
    playSong(next);
  };

  const submitRating = async () => {
    if (!currentSong || rating === 0) return;

    setSubmittingRating(true);
    try {
      const response = await fetch("/api/rate-song", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          song_id: currentSong._id,
          song_title: currentSong.title,
          rasa: currentSong.rasa,
          rating: rating,
          comments: comments || undefined
        })
      });

      if (!response.ok) throw new Error("Failed to submit rating");
      
      setShowRatingModal(false);
      setRating(0);
      setComments("");
    } catch (error) {
      console.error("Error submitting rating:", error);
    } finally {
      setSubmittingRating(false);
    }
  };

   // Sort and paginate songs
   const allFilteredSongs = filter === "All" 
     ? Object.values(songsByRasa).flat()
     : songsByRasa[filter] || [];

   console.log(`Filter: ${filter}, allFilteredSongs.length: ${allFilteredSongs.length}, songsByRasa keys:`, Object.keys(songsByRasa));

  // Sort: recommended songs first, then by title
  const sortedSongs = [...allFilteredSongs].sort((a, b) => {
    const aRecommended = recommendedSongIds.has(a._id);
    const bRecommended = recommendedSongIds.has(b._id);
    if (aRecommended !== bRecommended) {
      return aRecommended ? -1 : 1;
    }
    return a.title.localeCompare(b.title);
  });

  const paginatedSongs = sortedSongs.slice(
    currentPage * SONGS_PER_PAGE,
    (currentPage + 1) * SONGS_PER_PAGE
  );

  const totalPages = Math.ceil(sortedSongs.length / SONGS_PER_PAGE);

  const rasaOptions = ["All", ...Object.values(RASA_MAP)];

  return (
    <div className={`max-w-4xl mx-auto space-y-5 sm:space-y-6 ${currentSong ? "pb-24 lg:pb-20" : "pb-6"}`}>
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="section-title text-xl sm:text-2xl mb-1">Music Player</h1>
        <p className="text-muted-foreground text-sm">Explore ragas and rate songs</p>
      </motion.div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {rasaOptions.map(rasa => (
          <button
            key={rasa}
            onClick={() => {
              setFilter(rasa);
              setCurrentPage(0);
            }}
            className={`px-3 sm:px-4 py-1.5 sm:py-2 rounded-full text-xs sm:text-sm transition-all duration-200 ${
              filter === rasa ? "gradient-bg text-primary-foreground shadow-lg" : "bg-muted text-muted-foreground hover:text-foreground"
            }`}
          >
            {rasa}
          </button>
        ))}
      </div>

      {/* Song count and pagination info */}
      {!loading && sortedSongs.length > 0 && (
        <div className="text-xs sm:text-sm text-muted-foreground">
          <p>Showing {paginatedSongs.length} of {sortedSongs.length} songs{recommendedSongIds.size > 0 ? " (recommended songs first)" : ""}</p>
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="text-center py-8 text-muted-foreground">
          Loading songs...
        </div>
      )}

      {/* Error state */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-sm text-red-400"
        >
          <p className="font-semibold mb-2">Connection Error</p>
          <p>{error}</p>
          <p className="text-xs mt-2 text-red-300">
            To fix: Start the backend with <code className="bg-black/30 px-2 py-1 rounded">cd Backend && python main.py</code>
          </p>
        </motion.div>
      )}

      {/* Playlist */}
      {!loading && !error && (
        <AnimatePresence mode="popLayout">
          <div className="space-y-2">
            {paginatedSongs.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                {sortedSongs.length === 0 ? "No songs found for this rasa" : "No more songs to display"}
              </div>
            ) : (
              paginatedSongs.map((song, i) => (
                <motion.div
                  key={song._id}
                  layout
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 10 }}
                  transition={{ delay: i * 0.03, duration: 0.3 }}
                  onClick={() => playSong(song)}
                  className={`flex items-center gap-3 sm:gap-4 p-3 sm:p-4 rounded-xl cursor-pointer transition-all duration-200 ${
                    currentSong?._id === song._id ? "bg-primary/10 border border-primary/30" : "glass-card-hover"
                  }`}
                >
                  {/* Recommended badge */}
                  {recommendedSongIds.has(song._id) && (
                    <div className="w-1 h-1 rounded-full bg-primary flex-shrink-0" title="Recommended" />
                  )}
                  
                  <div className={`w-9 h-9 sm:w-10 sm:h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    currentSong?._id === song._id ? "gradient-bg" : "bg-muted"
                  }`}>
                    {currentSong?._id === song._id && playing ? (
                      <Pause className="w-4 h-4 text-primary-foreground" />
                    ) : (
                      <Music className="w-4 h-4 text-muted-foreground" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs sm:text-sm font-medium text-foreground truncate">{song.title}</p>
                    <p className="text-[10px] sm:text-xs text-muted-foreground truncate">{song.rasa}</p>
                  </div>
                  <span className="text-[10px] sm:text-xs px-2 py-0.5 sm:py-1 rounded-full bg-primary/10 text-primary hidden sm:block">{song.rasa}</span>
                  <span className="text-[10px] sm:text-xs text-muted-foreground flex-shrink-0">{song.duration}</span>
                </motion.div>
              ))
            )}
          </div>
        </AnimatePresence>
      )}

      {/* Pagination */}
      {!loading && totalPages > 1 && (
        <div className="flex items-center justify-between pt-4">
          <button
            onClick={() => setCurrentPage(p => Math.max(0, p - 1))}
            disabled={currentPage === 0}
            className="px-3 py-2 rounded-lg bg-muted text-muted-foreground disabled:opacity-50 disabled:cursor-not-allowed hover:bg-muted/80 transition-colors"
          >
            Previous
          </button>
          <span className="text-xs sm:text-sm text-muted-foreground">
            Page {currentPage + 1} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(p => Math.min(totalPages - 1, p + 1))}
            disabled={currentPage === totalPages - 1}
            className="px-3 py-2 rounded-lg bg-muted text-muted-foreground disabled:opacity-50 disabled:cursor-not-allowed hover:bg-muted/80 transition-colors"
          >
            Next
          </button>
        </div>
      )}

       {/* Hidden audio element */}
       <audio
         ref={audioRef}
         onEnded={handleAudioEnded}
         crossOrigin="anonymous"
       />
       {currentSong && console.log('Current song object:', currentSong)}

        {/* Enhanced Audio Player */}
        <AnimatePresence>
          {currentSong && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              className="fixed bottom-0 left-0 right-0 lg:left-64 p-3 sm:p-4 z-30"
              style={{ pointerEvents: 'auto' }}
            >
              <AudioPlayer
                song={currentSong ? {
                  song_id: currentSong._id,
                  title: currentSong.title,
                  rasa: currentSong.rasa,
                  audio_url: currentSong.audio_url
                } : null}
                isPlaying={playing}
                onPlay={handlePlay}
                onPause={handlePause}
                onNext={() => navigate(1)}
                onPrevious={() => navigate(-1)}
                onRate={() => setShowRatingModal(true)}
                audioRef={audioRef}
              />
            </motion.div>
          )}
        </AnimatePresence>

      {/* Rating Modal */}
      <AnimatePresence>
        {showRatingModal && currentSong && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowRatingModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-card border border-primary/20 rounded-xl p-6 w-full max-w-sm"
            >
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold">Rate "{currentSong.title}"</h2>
                <button
                  onClick={() => setShowRatingModal(false)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Star rating */}
              <div className="flex justify-center gap-2 mb-6">
                {[1, 2, 3, 4, 5].map(star => (
                  <button
                    key={star}
                    onClick={() => setRating(star)}
                    className="transition-transform hover:scale-110"
                  >
                    <Star
                      className={`w-8 h-8 ${
                        star <= rating
                          ? "fill-primary text-primary"
                          : "text-muted-foreground"
                      }`}
                    />
                  </button>
                ))}
              </div>

              {/* Comments */}
              <textarea
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                placeholder="Add optional comments about this song..."
                className="w-full bg-muted border border-primary/10 rounded-lg p-3 text-sm text-foreground placeholder-muted-foreground resize-none mb-4 focus:outline-none focus:border-primary/30"
                rows={3}
              />

              {/* Submit button */}
              <button
                onClick={submitRating}
                disabled={rating === 0 || submittingRating}
                className={`w-full py-2 rounded-lg font-medium transition-all ${
                  rating === 0 || submittingRating
                    ? "bg-muted text-muted-foreground cursor-not-allowed"
                    : "gradient-bg text-primary-foreground hover:shadow-lg"
                }`}
              >
                {submittingRating ? "Submitting..." : "Submit Rating"}
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default MusicPlayer;

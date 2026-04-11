import { useState, useEffect, useRef } from "react";
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, Star } from "lucide-react";
import { Slider } from "@/components/ui/slider";

interface AudioPlayerProps {
  song: {
    song_id: string;
    title: string;
    rasa: string;
    audio_url: string;
    confidence?: number;
  } | null;
  isPlaying: boolean;
  onPlay: (song: any) => void;
  onPause: () => void;
  onNext?: () => void;
  onPrevious?: () => void;
  onRate?: () => void;
  audioRef: React.RefObject<HTMLAudioElement>;
}

export const AudioPlayer = ({ song, isPlaying, onPlay, onPause, onNext, onPrevious, onRate, audioRef }: AudioPlayerProps) => {
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [volume, setVolume] = useState(70);
  const [isSeeking, setIsSeeking] = useState(false);
  const progressRef = useRef<HTMLDivElement>(null);
  const clickDebounceRef = useRef<NodeJS.Timeout | null>(null);

  const handleButtonClick = (callback: () => void, delay = 0) => {
    if (clickDebounceRef.current) {
      clearTimeout(clickDebounceRef.current);
    }
    clickDebounceRef.current = setTimeout(callback, delay);
  };

  // Update current time
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => {
      if (!isSeeking) {
        setCurrentTime(audio.currentTime);
      }
    };

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
    };

    const handleEnded = () => {
      onPause();
    };

    audio.addEventListener("timeupdate", handleTimeUpdate);
    audio.addEventListener("loadedmetadata", handleLoadedMetadata);
    audio.addEventListener("ended", handleEnded);

    return () => {
      audio.removeEventListener("timeupdate", handleTimeUpdate);
      audio.removeEventListener("loadedmetadata", handleLoadedMetadata);
      audio.removeEventListener("ended", handleEnded);
    };
  }, [isSeeking, onPause, audioRef]);

  // Update volume
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume / 100;
    }
  }, [volume, audioRef]);

  const formatTime = (time: number): string => {
    if (!time || !isFinite(time)) return "0:00";
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = progressRef.current?.getBoundingClientRect();
    if (!rect || !audioRef.current) return;

    const percent = (e.clientX - rect.left) / rect.width;
    const newTime = percent * duration;
    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleSeek = (value: number[]) => {
    const newTime = value[0];
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  if (!song) {
    return (
      <div className="w-full bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 rounded-xl p-6 border border-slate-700/50 backdrop-blur-xl">
        <p className="text-sm text-slate-400 text-center">Select a song to start playing</p>
      </div>
    );
  }

  const progress = duration ? (currentTime / duration) * 100 : 0;

  return (
    <div className="w-full max-w-4xl mx-auto bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6 border border-slate-700/50 backdrop-blur-xl shadow-2xl space-y-6">
      {/* Song Info */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg sm:text-xl font-bold text-white truncate mb-1">
            {song.title}
          </h3>
          <p className="text-sm text-slate-400">
            <span className="text-purple-400 font-medium">{song.rasa}</span>
            {song.confidence && (
              <>
                <span className="mx-2 text-slate-600">•</span>
                <span>{(song.confidence * 100).toFixed(0)}% match</span>
              </>
            )}
          </p>
        </div>
      </div>

      {/* Progress Bar with Slider */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-slate-400 w-10">
            {formatTime(currentTime)}
          </span>

          {/* Interactive Progress Slider */}
          <div className="flex-1 px-1">
            <Slider
              value={[currentTime]}
              max={duration || 100}
              step={0.1}
              onValueChange={handleSeek}
              className="w-full cursor-pointer"
            />
          </div>

          <span className="text-xs font-mono text-slate-400 w-10 text-right">
            {formatTime(duration)}
          </span>
        </div>

        {/* Visual Progress Bar */}
        <div
          ref={progressRef}
          onClick={handleProgressClick}
          className="relative h-1.5 bg-slate-700/50 rounded-full overflow-hidden cursor-pointer group hover:h-2 transition-all"
        >
          <div
            className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
          {/* Hover indicator */}
          <div
            className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
            style={{ left: `${progress}%`, transform: "translate(-50%, -50%)" }}
          />
        </div>
      </div>

       {/* Controls */}
       <div className="flex items-center justify-between gap-4">
         {/* Left: Play Controls */}
         <div className="flex items-center gap-3">
           <button
             onClick={() => {
               console.log('Skip back clicked');
               handleButtonClick(() => onPrevious?.());
             }}
             className="p-2 rounded-lg bg-slate-700/30 hover:bg-slate-700/50 text-slate-300 hover:text-white transition-colors"
             title="Previous"
           >
             <SkipBack className="w-5 h-5" />
           </button>

           <button
             onClick={() => {
               console.log('Play/Pause clicked, isPlaying:', isPlaying);
               handleButtonClick(() => isPlaying ? onPause() : onPlay(song));
             }}
             className="p-3 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg hover:shadow-xl transition-all transform hover:scale-105 active:scale-95"
           >
             {isPlaying ? (
               <Pause className="w-6 h-6" fill="currentColor" />
             ) : (
               <Play className="w-6 h-6 ml-0.5" fill="currentColor" />
             )}
           </button>

           <button
             onClick={() => {
               console.log('Skip forward clicked');
               handleButtonClick(() => onNext?.());
             }}
             className="p-2 rounded-lg bg-slate-700/30 hover:bg-slate-700/50 text-slate-300 hover:text-white transition-colors"
             title="Next"
           >
             <SkipForward className="w-5 h-5" />
           </button>
         </div>

         {/* Middle: Rating Button */}
         {onRate && (
           <button
             onClick={() => onRate?.()}
             className="p-2 rounded-lg bg-slate-700/30 hover:bg-slate-700/50 text-slate-300 hover:text-yellow-400 transition-colors"
             title="Rate this song"
           >
             <Star className="w-5 h-5" />
           </button>
         )}

         {/* Right: Volume Control */}
         <div className="flex items-center gap-3">
           {volume === 0 ? (
             <VolumeX className="w-5 h-5 text-slate-400" />
           ) : (
             <Volume2 className="w-5 h-5 text-slate-400" />
           )}
            <div className="w-20 sm:w-24">
              <Slider
                value={[volume]}
                max={100}
                step={1}
                onValueChange={(value) => {
                  console.log('Volume changed to:', value[0]);
                  setVolume(value[0]);
                }}
                className="w-full"
              />
            </div>
           <span className="text-xs text-slate-400 w-8 text-right">{volume}%</span>
         </div>
       </div>

      {/* Hidden Audio Element */}
      <audio ref={audioRef} crossOrigin="anonymous" />
    </div>
  );
};

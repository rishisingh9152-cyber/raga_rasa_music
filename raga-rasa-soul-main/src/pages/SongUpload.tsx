import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, Music, CheckCircle2, AlertCircle, Loader } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { API_BASE_URL } from "@/lib/apiBase";

const RASAS = ["Shaant", "Shringar", "Veer", "Shok"];

interface UploadStep {
  file?: File;
  title: string;
  artist: string;
  tempPath?: string;
  classifiedRasa?: string;
  step: "form" | "uploading" | "classifying" | "confirm" | "success" | "error";
  error?: string;
}

const SongUpload = () => {
  const [uploadData, setUploadData] = useState<UploadStep>({
    title: "",
    artist: "",
    step: "form",
  });
  
  const [selectedRasa, setSelectedRasa] = useState("Shaant");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith(".mp3")) {
      toast.error("Please select an MP3 file");
      return;
    }

    const sizeMB = file.size / (1024 * 1024);
    if (sizeMB > 50) {
      toast.error("File size must be less than 50MB");
      return;
    }

    setUploadData(prev => ({ ...prev, file }));
    toast.success(`File selected: ${file.name}`);
  };

  const handleInitialUpload = async () => {
    if (!uploadData.file || !uploadData.title.trim()) {
      toast.error("Please select a file and enter a song title");
      return;
    }

    setUploadData(prev => ({ ...prev, step: "uploading" }));

    try {
      const token = localStorage.getItem("auth_token");
      const formData = new FormData();
      formData.append("file", uploadData.file);
      formData.append("title", uploadData.title);
      formData.append("artist", uploadData.artist || "Unknown");
      formData.append("emotion", "Neutral");

      const response = await fetch(`${API_BASE_URL}/songs/upload`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      console.log("Upload response:", data);
      
      setUploadData(prev => ({
        ...prev,
        step: "classifying",
        tempPath: data.temp_path,
        classifiedRasa: data.classification?.rasa || "Shaant",
      }));

      // Simulate classification processing
      setTimeout(() => {
        setSelectedRasa(data.classification?.rasa || "Shaant");
        setUploadData(prev => ({ ...prev, step: "confirm" }));
      }, 1500);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      console.error("Upload error:", errorMsg);
      toast.error(`Upload failed: ${errorMsg}`);
      setUploadData(prev => ({
        ...prev,
        step: "error",
        error: errorMsg,
      }));
    }
  };

  const handleConfirmUpload = async () => {
    if (!uploadData.tempPath) {
      toast.error("Missing upload information");
      return;
    }

    setUploadData(prev => ({ ...prev, step: "uploading" }));

    try {
       const token = localStorage.getItem("auth_token");
       const response = await fetch(
         `${API_BASE_URL}/songs/confirm-upload`,
         {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
            body: JSON.stringify({
              temp_path: uploadData.tempPath,
             title: uploadData.title,
             artist: uploadData.artist || "Unknown",
             rasa: selectedRasa,
           }),
         }
       );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      setUploadData(prev => ({
        ...prev,
        step: "success",
      }));

      toast.success("Song uploaded successfully!");

      // Reset form after 2 seconds
      setTimeout(() => {
        setUploadData({ title: "", artist: "", step: "form" });
        setSelectedRasa("Shaant");
        if (fileInputRef.current) fileInputRef.current.value = "";
      }, 2000);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      console.error("Confirmation error:", errorMsg);
      toast.error(`Confirmation failed: ${errorMsg}`);
      setUploadData(prev => ({
        ...prev,
        step: "error",
        error: errorMsg,
      }));
    }
  };

  const handleReset = () => {
    setUploadData({ title: "", artist: "", step: "form" });
    setSelectedRasa("Shaant");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="section-title text-xl sm:text-2xl mb-1">Upload Song</h1>
        <p className="text-muted-foreground text-sm">
          Add your favorite ragas to the library
        </p>
      </motion.div>

      <AnimatePresence mode="wait">
        {/* Form Step */}
        {uploadData.step === "form" && (
          <motion.div
            key="form"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Card className="p-6 sm:p-8 space-y-6">
              {/* File Upload Area */}
              <div
                onClick={() => fileInputRef.current?.click()}
                className="relative border-2 border-dashed border-border rounded-xl p-8 sm:p-12 text-center cursor-pointer transition-all hover:border-primary/50 hover:bg-primary/5"
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".mp3"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <motion.div
                  className="flex flex-col items-center gap-3"
                  animate={{ scale: uploadData.file ? 1.05 : 1 }}
                >
                  <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                    <Upload className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">
                      {uploadData.file ? uploadData.file.name : "Click to upload MP3"}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      or drag and drop (Max 50MB)
                    </p>
                  </div>
                </motion.div>
              </div>

              {/* Form Fields */}
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">
                    Song Title *
                  </label>
                  <Input
                    placeholder="Enter song title"
                    value={uploadData.title}
                    onChange={(e) =>
                      setUploadData(prev => ({ ...prev, title: e.target.value }))
                    }
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">
                    Artist Name
                  </label>
                  <Input
                    placeholder="Enter artist name (optional)"
                    value={uploadData.artist}
                    onChange={(e) =>
                      setUploadData(prev => ({ ...prev, artist: e.target.value }))
                    }
                    className="w-full"
                  />
                </div>
              </div>

              {/* Upload Button */}
              <Button
                onClick={handleInitialUpload}
                disabled={!uploadData.file || !uploadData.title.trim()}
                className="w-full"
              >
                <Music className="w-4 h-4 mr-2" />
                Upload & Classify
              </Button>
            </Card>
          </motion.div>
        )}

        {/* Uploading Step */}
        {uploadData.step === "uploading" && (
          <motion.div
            key="uploading"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Card className="p-8 text-center space-y-4">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <Loader className="w-12 h-12 text-primary mx-auto" />
              </motion.div>
              <div>
                <p className="font-medium text-foreground">Processing...</p>
                <p className="text-sm text-muted-foreground">
                  Please wait while we upload and classify your song
                </p>
              </div>
            </Card>
          </motion.div>
        )}

        {/* Classifying Step */}
        {uploadData.step === "classifying" && (
          <motion.div
            key="classifying"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Card className="p-8 text-center space-y-4">
              <motion.div
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                <Music className="w-12 h-12 text-primary mx-auto" />
              </motion.div>
              <div>
                <p className="font-medium text-foreground">
                  Classifying Rasa...
                </p>
                <p className="text-sm text-muted-foreground">
                  Analyzing the song to determine its rasa
                </p>
              </div>
            </Card>
          </motion.div>
        )}

        {/* Confirmation Step */}
        {uploadData.step === "confirm" && (
          <motion.div
            key="confirm"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Card className="p-6 sm:p-8 space-y-6">
              <div className="bg-primary/10 border border-primary/20 rounded-lg p-4">
                <p className="text-sm text-foreground">
                  <span className="font-medium">Detected Rasa:</span>{" "}
                  {uploadData.classifiedRasa}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  You can change this if needed
                </p>
              </div>

              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">
                  Select Rasa
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {RASAS.map((rasa) => (
                    <button
                      key={rasa}
                      onClick={() => setSelectedRasa(rasa)}
                      className={`p-3 rounded-lg text-sm font-medium transition-all ${
                        selectedRasa === rasa
                          ? "gradient-bg text-primary-foreground shadow-lg"
                          : "bg-muted text-muted-foreground hover:text-foreground"
                      }`}
                    >
                      {rasa}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <Button
                  onClick={handleReset}
                  variant="outline"
                  className="w-full"
                >
                  Cancel
                </Button>
                <Button onClick={handleConfirmUpload} className="w-full">
                  <CheckCircle2 className="w-4 h-4 mr-2" />
                  Confirm
                </Button>
              </div>
            </Card>
          </motion.div>
        )}

        {/* Success Step */}
        {uploadData.step === "success" && (
          <motion.div
            key="success"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Card className="p-8 text-center space-y-4">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200, damping: 15 }}
              >
                <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto" />
              </motion.div>
              <div>
                <p className="font-medium text-foreground text-lg">
                  Song Uploaded Successfully!
                </p>
                <p className="text-sm text-muted-foreground mt-2">
                  {uploadData.title} has been added to the {selectedRasa} collection
                </p>
              </div>
            </Card>
          </motion.div>
        )}

        {/* Error Step */}
        {uploadData.step === "error" && (
          <motion.div
            key="error"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Card className="p-8 text-center space-y-4">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
              <div>
                <p className="font-medium text-foreground">Upload Failed</p>
                <p className="text-sm text-muted-foreground mt-2">
                  {uploadData.error || "An error occurred during upload"}
                </p>
              </div>
              <Button onClick={handleReset} className="w-full">
                Try Again
              </Button>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SongUpload;

import { useState, useRef, useEffect, useMemo } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Upload, Music, Music2, Download, Play, Pause, 
  Wand2, CheckCircle, RefreshCw, Sliders, FileAudio, 
  Clock, Loader2 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { usePageMetadata } from "@/hooks/usePageMetadata";
import { SEOContent, Breadcrumb } from "@/components/common/SEOContent";
import RelatedTools from "@/components/common/RelatedTools";
import { cn } from "@/lib/utils";

// Audio configurations matching user resources
const GENRE_TRACKS: Record<string, { title: string; audioUrl: string; duration: string }> = {
  classical: {
    title: "Orchestrated Gymnopédie No. 1 (Classical)",
    audioUrl: "/musics/Gymnopedieno.1.mp3",
    duration: "2:39"
  },
  jrock: {
    title: "Sakura no Uta - Full Band (Rock)",
    audioUrl: "/musics/SakuraNoUta.mp3",
    duration: "1:40"
  },
  electronic: {
    title: "Sprunki Phase 2.5 - Synth Arrangement (Electronic)",
    audioUrl: "/musics/SprunkiPhase2.5(Bonus).mp3",
    duration: "2:05"
  },
  pop: {
    title: "Calm Down - Afrobeat Orchestration (Pop)",
    audioUrl: "/musics/Remacalm.mp3",
    duration: "3:58"
  }
};

export default function MidiComposerPage() {
  usePageMetadata({
    title: "AI MIDI Composer & Arranger | SoLuna - Free MIDI Completion Tool",
    description: "Complete and orchestrate your draft MIDI files using advanced neural music networks. Render raw MIDI into full instrument ensembles and high-fidelity MP3.",
    keywords: "midi completion, midi ai composer, midi arranger, render midi to mp3, virtual orchestra, free midi tools, ai music generator, songwriting assistant",
    canonicalUrl: "https://SoLuna.studio/midi-composer",
    ogImage: "https://SoLuna.studio/logo2.png",
    ogType: "website"
  });

  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // States
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [genre, setGenre] = useState<"classical" | "jrock" | "electronic" | "pop">("classical");
  const [complexity, setComplexity] = useState<number>(75);
  const [tempoMatch, setTempoMatch] = useState<boolean>(true);
  const [tempoBpm, setTempoBpm] = useState<number>(120);

  // Generation status
  const [isGenerating, setIsGenerating] = useState(false);
  const [genStep, setGenStep] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);

  // Playback audio states
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [audioDuration, setAudioDuration] = useState(0);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const progressIntervalRef = useRef<number | null>(null);

  const activeTrack = useMemo(() => GENRE_TRACKS[genre], [genre]);

  const generationSteps = [
    "Parsing user MIDI file track headers...",
    "Extracting key signature, tempo maps, and core chord progression...",
    "Aligning counterpoint voices and filling harmonic registers...",
    "Scoring auxiliary strings, woodwinds, and synthesizer pads...",
    "Compiling and rendering final orchestrated MIDI tracks...",
    "Synthesizing high-fidelity audio output to MP3..."
  ];

  // Drag and Drop Handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (uploadedFile: File) => {
    const isMidi = uploadedFile.name.endsWith(".mid") || uploadedFile.name.endsWith(".midi");
    if (!isMidi) {
      toast({
        title: "Invalid file type",
        description: "Please upload a valid MIDI (.mid or .midi) file.",
        variant: "destructive"
      });
      return;
    }
    setSelectedFile(uploadedFile);
    setIsCompleted(false);
    toast({
      title: "MIDI Uploaded Successfully",
      description: `${uploadedFile.name} is ready for AI generation.`
    });
  };

  // Generate Simulation
  const startGeneration = () => {
    if (!selectedFile) return;
    setIsGenerating(true);
    setGenStep(0);
    setIsCompleted(false);

    const interval = setInterval(() => {
      setGenStep((prev) => {
        if (prev >= generationSteps.length - 1) {
          clearInterval(interval);
          setTimeout(() => {
            setIsGenerating(false);
            setIsCompleted(true);
            toast({
              title: "Arrangement Complete!",
              description: "Your MIDI file has been successfully arranged and rendered."
            });
          }, 800);
          return prev;
        }
        return prev + 1;
      });
    }, 1500);
  };

  // Audio Playback logic
  const togglePlay = () => {
    if (!audioRef.current) {
      audioRef.current = new Audio(activeTrack.audioUrl);
      audioRef.current.addEventListener("loadedmetadata", () => {
        setAudioDuration(audioRef.current?.duration || 0);
      });
      audioRef.current.addEventListener("ended", () => {
        setIsPlaying(false);
        setCurrentTime(0);
        if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
      });
    }

    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
    } else {
      audioRef.current.play().then(() => {
        setIsPlaying(true);
        progressIntervalRef.current = window.setInterval(() => {
          if (audioRef.current) {
            setCurrentTime(audioRef.current.currentTime);
          }
        }, 250);
      }).catch((e) => {
        console.error("Audio playback error:", e);
        toast({
          title: "Audio Unavailable",
          description: "Could not load the preview audio stream.",
          variant: "destructive"
        });
      });
    }
  };

  const handleSliderSeek = (value: number[]) => {
    if (audioRef.current) {
      audioRef.current.currentTime = value[0];
      setCurrentTime(value[0]);
    }
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  };

  const handleReset = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
    }
    setIsPlaying(false);
    setCurrentTime(0);
    setSelectedFile(null);
    setIsCompleted(false);
  };

  // Cleanup audio context on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-[#030303] relative overflow-hidden selection:bg-white/10">
      <main className="container mx-auto px-4 md:px-6 pt-8 md:pt-12 pb-16 relative z-10">
        <div className="max-w-5xl mx-auto">
          {/* Breadcrumb */}
          <Breadcrumb items={[
            { name: "Home", url: "https://SoLuna.studio/" },
            { name: "MIDI AI Composer", url: "https://SoLuna.studio/midi-composer" }
          ]} />

          {/* Header */}
          <div className="mb-16 text-center space-y-6">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full border border-white/5 bg-white/[0.02] text-muted-foreground text-[10px] font-bold tracking-[0.2em] uppercase">
              <Wand2 className="w-3 h-3 text-cyan-400" />
              <span>AI-Powered Arrangement & Orchestration</span>
            </div>

            <div className="space-y-4">
              <h1 className="text-5xl md:text-7xl font-light tracking-tighter text-white">
                MIDI AI <span className="text-muted-foreground font-thin">Composer</span>
              </h1>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed font-light">
                Calibrated specifically for precise harmonic analysis. Upload a raw MIDI segment, arrange it into complete multi-instrument voices, and compile into polished MIDI or MP3.
              </p>
            </div>
          </div>

          {/* Main Content Layout */}
          <div className="glass-card rounded-[2.5rem] border border-white/5 bg-[#0a0a0a]/90 shadow-2xl overflow-hidden min-h-[600px] flex flex-col p-10">
            <AnimatePresence mode="wait">
              
              {/* Step 1: Upload File */}
              {!selectedFile && !isGenerating && !isCompleted && (
                <motion.div
                  key="upload-step"
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -15 }}
                  className="flex-1 flex flex-col"
                >
                  <div
                    className={cn(
                      "flex-1 border-2 border-dashed rounded-[2rem] transition-all flex flex-col items-center justify-center p-12 text-center cursor-pointer",
                      dragActive ? "border-white/20 bg-white/[0.03]" : "border-white/5 hover:border-white/10"
                    )}
                    onDragOver={handleDrag}
                    onDragLeave={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".mid,.midi"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                    <div className="w-24 h-24 bg-white/[0.03] rounded-full flex items-center justify-center mb-8 border border-white/5">
                      <Upload className="w-10 h-10 text-muted-foreground" />
                    </div>
                    <h3 className="text-2xl font-light text-white mb-3">Upload MIDI File</h3>
                    <p className="text-muted-foreground max-w-sm font-light">
                      Drag and drop or click to select a MIDI file (.mid or .midi) from your computer to orchestrate.
                    </p>
                  </div>
                </motion.div>
              )}

              {/* Step 2: Configuration & Trigger Generate */}
              {selectedFile && !isGenerating && !isCompleted && (
                <motion.div
                  key="config-step"
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -15 }}
                  className="space-y-8 flex-1 flex flex-col justify-center"
                >
                  {/* File Info */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between p-6 rounded-2xl bg-white/[0.02] border border-white/5 gap-4 text-left">
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground uppercase tracking-widest font-bold mb-1">Selected File</p>
                      <h3 className="text-xl font-medium text-white">{selectedFile.name}</h3>
                      <p className="text-[10px] text-muted-foreground">{(selectedFile.size / 1024).toFixed(2)} KB • Ready to compose</p>
                    </div>
                    <Button
                      onClick={handleReset}
                      variant="outline"
                      className="rounded-lg"
                    >
                      Change File
                    </Button>
                  </div>

                  {/* Options Grid */}
                  <div className="grid md:grid-cols-2 gap-6 text-left">
                    {/* Style Selection */}
                    <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 space-y-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-xl bg-white/5 border border-white/5">
                          <Sliders className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <Label className="text-sm font-bold text-white">Target Style / Genre</Label>
                          <p className="text-xs text-muted-foreground">Select orchestration preset</p>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3 pt-2">
                        {(["classical", "jrock", "electronic", "pop"] as const).map((style) => (
                          <button
                            key={style}
                            onClick={() => setGenre(style)}
                            className={`py-3 px-4 rounded-xl border text-xs font-semibold uppercase tracking-wider transition-all text-center ${
                              genre === style
                                ? "bg-white border-white text-black font-bold shadow-[0_0_15px_rgba(255,255,255,0.15)]"
                                : "bg-white/[0.02] border-white/5 text-muted-foreground hover:border-white/10 hover:text-white"
                            }`}
                          >
                            {style === "jrock" ? "J-Rock / Band" : style}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Complexity & Settings */}
                    <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 space-y-6">
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <Label className="text-sm font-bold text-white">Complexity / Instrument Voices</Label>
                          <span className="text-xs font-bold text-white">{complexity}%</span>
                        </div>
                        <Slider
                          value={[complexity]}
                          onValueChange={(val) => setComplexity(val[0])}
                          max={100}
                          step={1}
                          className="w-full"
                        />
                        <div className="flex justify-between text-[10px] text-muted-foreground/60">
                          <span>Solo/Chamber</span>
                          <span>Full Orchestral</span>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">Align Tempo</Label>
                          <button
                            onClick={() => setTempoMatch(!tempoMatch)}
                            className={`w-full py-2 px-3 rounded-lg border text-xs font-bold transition-all text-center ${
                              tempoMatch ? "bg-white/5 border-white/10 text-white" : "border-transparent text-muted-foreground"
                            }`}
                          >
                            {tempoMatch ? "Source Tempo" : "Override Tempo"}
                          </button>
                        </div>
                        <div className="space-y-2">
                          <Label className="text-xs font-bold text-muted-foreground uppercase tracking-wider block">Tempo (BPM)</Label>
                          <input
                            type="number"
                            value={tempoBpm}
                            onChange={(e) => setTempoBpm(Number(e.target.value))}
                            disabled={tempoMatch}
                            className="w-full py-2 px-3 rounded-lg bg-white/5 border border-white/10 text-xs font-bold text-white focus:outline-none focus:border-white/20 disabled:opacity-40"
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Process Button */}
                  <Button
                    onClick={startGeneration}
                    className="w-full h-16 rounded-2xl bg-white text-black hover:bg-white/90 text-lg font-semibold"
                  >
                    <Wand2 className="w-5 h-5 mr-2" />
                    Generate Orchestrated Arrangement
                  </Button>
                </motion.div>
              )}

              {/* Step 3: Generating Visualizer */}
              {isGenerating && (
                <motion.div
                  key="generating-step"
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex-1 flex flex-col items-center justify-center py-12 space-y-8"
                >
                  <div className="flex flex-col items-center justify-center space-y-4">
                    <div className="relative flex items-center justify-center w-24 h-24 bg-white/[0.03] rounded-full border border-white/5">
                      <Loader2 className="w-10 h-10 animate-spin text-white" />
                    </div>
                    
                    <div className="space-y-1 text-center">
                      <h3 className="text-2xl font-light text-white">AI Orchestrator Active</h3>
                      <p className="text-sm text-muted-foreground">Scoring orchestration and completing MIDI structures...</p>
                    </div>
                  </div>

                  {/* Progress Log steps */}
                  <div className="w-full max-w-md mx-auto p-6 rounded-2xl bg-white/[0.02] border border-white/5 text-left space-y-3 font-mono text-xs">
                    {generationSteps.map((step, idx) => {
                      const isDone = idx < genStep;
                      const isActive = idx === genStep;
                      return (
                        <div 
                          key={idx} 
                          className={`flex items-start gap-3 transition-all duration-300 ${
                            isDone ? "text-white/60" : isActive ? "text-white font-bold animate-pulse" : "text-muted-foreground/20"
                          }`}
                        >
                          {isDone ? (
                            <span className="text-white font-bold">✔</span>
                          ) : isActive ? (
                            <span className="text-white">•</span>
                          ) : (
                            <span>◦</span>
                          )}
                          <span className="flex-1">{step}</span>
                        </div>
                      );
                    })}
                  </div>
                </motion.div>
              )}

              {/* Step 4: Finished Arrangement view */}
              {isCompleted && !isGenerating && (
                <motion.div
                  key="completed-step"
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="space-y-8"
                >
                  {/* File info */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between p-6 rounded-2xl bg-white/[0.02] border border-white/5 gap-4 text-left">
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground uppercase tracking-widest font-bold mb-1">Generated Output for</p>
                      <h3 className="text-xl font-medium text-white">{selectedFile?.name}</h3>
                    </div>
                  </div>

                  {/* Playback Controls */}
                  <div className="space-y-4">
                    <Button
                      onClick={togglePlay}
                      className="w-full h-16 rounded-2xl bg-white text-black hover:bg-white/90 text-lg font-semibold"
                    >
                      {isPlaying ? "⏸ Pause Preview" : "▶ Play Preview"}
                    </Button>

                    <div className="grid md:grid-cols-2 gap-6 pt-4 text-left">
                      {/* Rendered MP3 */}
                      <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 space-y-4">
                        <div className="flex items-center gap-3">
                          <div className="p-2 rounded-xl bg-white/5 border border-white/5">
                            <FileAudio className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <Label className="text-sm font-bold text-white">Pristine MP3 Audio</Label>
                            <p className="text-xs text-muted-foreground">High-quality rendered audio track</p>
                          </div>
                        </div>
                        
                        <div className="space-y-1">
                          <Slider
                            value={[currentTime]}
                            max={audioDuration || 125}
                            step={0.1}
                            onValueChange={handleSliderSeek}
                            className="w-full cursor-pointer py-2"
                          />
                          <div className="flex justify-between text-[9px] text-muted-foreground/40 font-mono">
                            <span>{formatTime(currentTime)}</span>
                            <span>{formatTime(audioDuration || 125)}</span>
                          </div>
                        </div>
                        
                        <a
                          href={activeTrack.audioUrl}
                          download
                          className="w-full h-10 px-4 rounded-lg bg-white/5 border border-white/10 hover:border-white/20 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all"
                        >
                          <Download className="w-4 h-4 text-white" />
                          Download MP3 File
                        </a>
                      </div>

                      {/* Completed MIDI */}
                      <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 space-y-4 flex flex-col justify-between">
                        <div className="space-y-4">
                          <div className="flex items-center gap-3">
                            <div className="p-2 rounded-xl bg-white/5 border border-white/5">
                              <Music2 className="w-5 h-5 text-white" />
                            </div>
                            <div>
                              <Label className="text-sm font-bold text-white">Arranged MIDI Track</Label>
                              <p className="text-xs text-muted-foreground">Completed multi-instrument score</p>
                            </div>
                          </div>
                          <p className="text-xs text-muted-foreground leading-relaxed pt-2">
                            Includes separate MIDI channels mapped to General MIDI specifications: lead, harmony accompaniment, backing bass, and string orchestration.
                          </p>
                        </div>
                        
                        <a
                          href="/samples/completed_orchestration.mid"
                          download
                          className="w-full h-10 px-4 rounded-lg bg-white hover:bg-white/90 text-black text-xs font-bold flex items-center justify-center gap-2 transition-all"
                        >
                          <Download className="w-4 h-4" />
                          Download MIDI File
                        </a>
                      </div>
                    </div>

                    {/* Reset & Footer */}
                    <div className="flex justify-between items-center pt-6 mt-6 border-t border-white/5">
                      <span className="text-[10px] text-muted-foreground uppercase tracking-widest font-bold">
                        Complexity: {complexity}%
                      </span>
                      
                      <Button
                        onClick={handleReset}
                        variant="outline"
                        className="rounded-lg h-9 text-xs"
                      >
                        <RefreshCw className="w-3.5 h-3.5 mr-2" />
                        Arrange Another File
                      </Button>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Guide Section */}
          <section className="mt-20 text-left space-y-8">
            <h3 className="text-3xl font-light text-white tracking-tight font-display pl-1 border-l-2 border-white/20">
              How MIDI AI Arranger Works
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-8 rounded-3xl border border-white/5 bg-white/[0.01] space-y-4">
                <span className="text-muted-foreground/30 font-light text-4xl font-display">01</span>
                <h4 className="text-lg font-medium text-white">Upload Draft</h4>
                <p className="text-xs text-muted-foreground leading-relaxed font-light">
                  Drop your raw single-track or multi-track MIDI draft. The parser scans the notes, pitch sequences, and tempo markers automatically.
                </p>
              </div>

              <div className="p-8 rounded-3xl border border-white/5 bg-white/[0.01] space-y-4">
                <span className="text-muted-foreground/30 font-light text-4xl font-display">02</span>
                <h4 className="text-lg font-medium text-white">Orchestrations</h4>
                <p className="text-xs text-muted-foreground leading-relaxed font-light">
                  Our model scores harmonies, adds backing strings/pads, and establishes counterpoints based on traditional music theory rules.
                </p>
              </div>

              <div className="p-8 rounded-3xl border border-white/5 bg-white/[0.01] space-y-4">
                <span className="text-muted-foreground/30 font-light text-4xl font-display">03</span>
                <h4 className="text-lg font-medium text-white">Orchestrated Render</h4>
                <p className="text-xs text-muted-foreground leading-relaxed font-light">
                  Listen directly inside the browser using the pre-rendered audio player, then download the structured MIDI file or raw MP3.
                </p>
              </div>
            </div>
          </section>

          {/* Related tools */}
          <div className="mt-16">
            <RelatedTools currentTool="/midi-composer" />
          </div>
        </div>
      </main>
    </div>
  );
}

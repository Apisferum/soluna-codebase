import { useState, useRef, useEffect } from "react";
import { ArrowRight, Music2, Layers, Disc, Music, BookOpen, Bot, Wand2, Headphones, Guitar, Trophy, Mic, FileText, Play, Pause, Clock, Tag, Star, ChevronLeft, ChevronRight } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import Footer from "@/components/layout/Footer";
import HeroSection from "@/components/common/HeroSection";
import WhyChoose from "@/components/common/WhyChoose";
import { usePageMetadata } from "@/hooks/usePageMetadata";

// Featured AI tools (first row: 3 cards side by side)
const featuredTools = [
  { 
    title: "Chord AI", 
    desc: "Neural audio chord detection and harmonic transcription.", 
    icon: Bot, 
    to: "/chord-ai", 
    color: "from-[#D4AF37]/20 to-[#8A6A16]/20",
    image: "/images/download(3).jpe",
    category: "Harmonics"
  },
  { 
    title: "Stem Separator", 
    desc: "AI 6-stem separation: vocals, drums, bass, guitar, piano, other.", 
    icon: Mic, 
    to: "/stem-separator", 
    color: "from-[#D4AF37]/20 to-[#8A6A16]/20",
    image: "/images/download(4).jpe",
    category: "Isolation"
  },
  { 
    title: "Vocal Splitter", 
    desc: "AI-powered vocal and instrumental separation.", 
    icon: Wand2, 
    to: "/vocal-splitter", 
    color: "from-[#D4AF37]/20 to-[#8A6A16]/20",
    image: "/images/Pulse musical_ abstract of sound wave, light frequencies or bright equalizer  _ Premium Photo.jpe",
    category: "Vocal AI"
  },
  { 
    title: "MIDI AI Completion", 
    desc: "Complete raw draft MIDI segments into full compositions and render them directly into MP3 tracks.", 
    icon: Music2, 
    to: "/midi-composer",
    color: "from-amber-500/20 to-orange-500/20",
    image: "/images/Piano Amidst Books.jpe",
    category: "MIDI AI"
  },
];

// Standard tool cards (3 per row on large screens)
const toolCards = [
  { 
    title: "Fretboard", 
    desc: "Interactive neck with adaptive note labeling.", 
    icon: Music2, 
    to: "/fretboard", 
    color: "from-[#D4AF37]/20 to-[#8A6A16]/20",
    image: "/images/Close Up Black with Gold Guitar Abstract Background_ Musical instrument vertical backdro.jpe",
    rating: "4.9",
    category: "Practice"
  },
  { 
    title: "Chord Library", 
    desc: "1,000+ voicings with interactive diagrams.", 
    icon: Layers, 
    to: "/chords", 
    color: "from-[#D4AF37]/20 to-[#8A6A16]/20",
    image: "/images/Painted picture of a Jazz Band.jpe",
    rating: "4.8",
    category: "Reference"
  },
  { 
    title: "Scale Explorer", 
    desc: "Visualize modes and exotic scales instantly.", 
    icon: Disc, 
    to: "/scales", 
    color: "from-[#D4AF37]/20 to-[#8A6A16]/20",
    image: "/images/download.jpe",
    rating: "4.9",
    category: "Theory"
  },
  { 
    title: "Theory Wheel", 
    desc: "Interactive Circle of Fifths and key logic.", 
    icon: BookOpen, 
    to: "/theory", 
    color: "from-amber-500/20 to-orange-500/20",
    image: "/images/Circle of Fifths _ Art Print _ Frame Option _ With or Without the Frame - Etsy.jpe",
    rating: "4.9",
    category: "Interactive"
  },
  { 
    title: "Metronome", 
    desc: "High-precision timing with visual pulse.", 
    icon: Music, 
    to: "/metronome", 
    color: "from-[#D4AF37]/20 to-[#8A6A16]/20",
    image: "/images/Metronome is an installation that _creates an altar to the senses_.jpe",
    rating: "4.7",
    category: "Timing"
  },
  { 
    title: "Ear Training", 
    desc: "Gamified interval recognition and pitch training.", 
    icon: Trophy, 
    to: "/ear-training", 
    color: "from-[#D4AF37]/20 to-[#8A6A16]/20",
    image: "/images/Train your ear.jpe",
    rating: "4.9",
    category: "Training"
  },
  { 
    title: "Tuner", 
    desc: "Real-time chromatic tuner with cent precision.", 
    icon: Guitar, 
    to: "/tuner", 
    color: "from-[#D4AF37]/20 to-[#8A6A16]/20",
    image: "/images/download (1).jpe",
    rating: "4.8",
    category: "Utility"
  },
  { 
    title: "Jam Studio", 
    desc: "Loop chord progressions with piano & pad backing.", 
    icon: Headphones, 
    to: "/jam", 
    color: "from-[#D4AF37]/20 to-[#8A6A16]/20",
    image: "/images/Music Studio _ JGGL.jpe",
    rating: "4.9",
    category: "Studio"
  },
];

// AI-Generated Music Samples tracks
const musicTracks = [
  {
    id: "gymnopedie",
    title: "Gymnopédie No. 1",
    subtitle: "Erik Satie (Ambient Classical)",
    duration: "2:39",
    cover: "/images/Piano Amidst Books.jpe",
    audioUrl: "/musics/Gymnopedieno.1.mp3",
    tags: ["classical", "soft-piano", "ambient", "calm", "relaxing"],
    color: "from-[#D4AF37]/10 to-[#F4D06F]/10"
  },
  {
    id: "harry-potter",
    title: "Harry Potter Theme",
    subtitle: "Hedwig's Theme (Remix)",
    duration: "0:30",
    cover: "/images/Metronome is an installation that _creates an altar to the senses_.jpe",
    audioUrl: "/musics/Hp.mp3",
    tags: ["mystical", "orchestral", "celesta", "fantasy", "cinematic"],
    color: "from-[#D4AF37]/10 to-[#F4D06F]/10"
  },
  {
    id: "kanye-homecoming",
    title: "Homecoming",
    subtitle: "Kanye West ft. Chris Martin",
    duration: "3:28",
    cover: "/images/Painted picture of a Jazz Band.jpe",
    audioUrl: "/musics/KanyeWest-Homecoming(Ft.ChrisMartin).mp3",
    tags: ["hip-hop", "piano-led", "rap", "upbeat", "melodic"],
    color: "from-[#D4AF37]/10 to-[#F4D06F]/10"
  },
  {
    id: "rema-calm",
    title: "Calm Down",
    subtitle: "Rema (Afrobeat Pop)",
    duration: "3:58",
    cover: "/images/Mid Century Modern Cat Jazz Band Poster, Retro Black Cats Music Illustration (Digital Download).jpe",
    audioUrl: "/musics/Remacalm.mp3",
    tags: ["afrobeat", "pop", "smooth-groove", "dance", "rhythm"],
    color: "from-[#D4AF37]/10 to-[#F4D06F]/10"
  },
  {
    id: "sakura-uta",
    title: "Sakura no Uta",
    subtitle: "J-Rock Instrumental",
    duration: "1:40",
    cover: "/images/Classical music for VPRO - tsjisse talsma.jpe",
    audioUrl: "/musics/SakuraNoUta.mp3",
    tags: ["j-rock", "melodic", "anime-style", "synth", "energetic"],
    color: "from-[#D4AF37]/10 to-[#F4D06F]/10"
  },
  {
    id: "sprunki",
    title: "Sprunki Phase 2.5",
    subtitle: "Bonus Electronic Track",
    duration: "2:05",
    cover: "/images/fading_echoes_cover.png",
    audioUrl: "/musics/SprunkiPhase2.5(Bonus).mp3",
    tags: ["chiptune", "electronic", "gaming", "synth-wave", "upbeat"],
    color: "from-[#D4AF37]/10 to-[#F4D06F]/10"
  },
  {
    id: "daft-technologic",
    title: "Technologic",
    subtitle: "Daft Punk (Robotic Remix)",
    duration: "4:53",
    cover: "/images/Vinyls _ Poster for Shopiq_ - Joanna Gniady.jpe",
    audioUrl: "/musics/Technolgic.mp3",
    tags: ["electronic", "synth-groove", "house", "vocoder", "rhythm"],
    color: "from-[#D4AF37]/10 to-[#F4D06F]/10"
  }
];

// Floating Musical Assets (inspired by premium origami and dandelion elements)
const FloatingTrebleClef = ({ className, delay = "0s" }: { className?: string, delay?: string }) => (
  <div className={`absolute z-0 golden-music-note animate-float-y pointer-events-auto select-none ${className}`} style={{ animationDelay: delay }}>
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-10 h-10">
      <path d="M12 21V5c0-1.5 1-3 3-3s2 1.5 2 2.5S15 7 12 7c-3 0-5 2-5 4.5s2 4.5 5 4.5c2.5 0 4-1.5 4-3s-1.5-2.5-3.5-2.5-3.5 1.5-3.5 3c0 2 2 3.5 4.5 3.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  </div>
);

const FloatingVinyl = ({ className, delay = "0s" }: { className?: string, delay?: string }) => (
  <div className={`absolute z-0 golden-music-note animate-float-x pointer-events-auto select-none ${className}`} style={{ animationDelay: delay }}>
    <div className="relative w-14 h-14 rounded-full border border-amber-500/30 flex items-center justify-center animate-[spin_15s_linear_infinite]">
      <div className="absolute inset-2.5 rounded-full border border-dashed border-amber-500/20" />
      <div className="absolute inset-5 rounded-full border border-amber-500/30" />
      <div className="w-3 h-3 rounded-full bg-amber-500/40" />
    </div>
  </div>
);

const FloatingCard = ({ image, className, delay = "0s" }: { image: string, className?: string, delay?: string }) => (
  <div className={`absolute z-0 pointer-events-auto select-none animate-float-diagonal ${className}`} style={{ animationDelay: delay }}>
    <div className="w-20 h-20 md:w-28 md:h-28 bg-zinc-950/80 backdrop-blur-sm border border-[#D4AF37]/20 p-1.5 rounded-2xl shadow-2xl transform rotate-6 hover:rotate-12 transition-transform duration-500">
      <img src={image} alt="Inspiration" className="w-full h-full object-cover rounded-xl opacity-55 hover:opacity-85 transition-opacity duration-300" />
    </div>
  </div>
);

const DottedCircle = ({ className, size = "w-[320px] h-[320px]" }: { className?: string, size?: string }) => (
  <div className={`absolute pointer-events-none border border-dashed border-amber-500/10 rounded-full z-0 ${size} ${className}`} />
);

const FloatingGlitterGuitar = ({ className, delay = "0s" }: { className?: string, delay?: string }) => (
  <div className={`absolute z-0 pointer-events-auto select-none animate-float-y ${className}`} style={{ animationDelay: delay }}>
    <img
      src="/images/golden_guitar_glitter.png"
      alt="Glitter Guitar"
      className="w-24 h-48 md:w-32 md:h-64 object-contain opacity-65 hover:opacity-95 transition-opacity duration-300 filter drop-shadow-[0_0_20px_rgba(255,215,0,0.45)]"
    />
  </div>
);

const FloatingGlitterKeyboard = ({ className, delay = "0s" }: { className?: string, delay?: string }) => (
  <div className={`absolute z-0 pointer-events-auto select-none animate-float-x ${className}`} style={{ animationDelay: delay }}>
    <img
      src="/images/golden_keyboard_glitter.png"
      alt="Glitter Keyboard"
      className="w-28 h-28 md:w-36 md:h-36 object-contain opacity-60 hover:opacity-90 transition-opacity duration-300 filter drop-shadow-[0_0_20px_rgba(255,215,0,0.4)]"
    />
  </div>
);

const FloatingGlitterNodes = ({ className, delay = "0s" }: { className?: string, delay?: string }) => (
  <div className={`absolute z-0 golden-music-note animate-float-diagonal pointer-events-auto select-none ${className}`} style={{ animationDelay: delay }}>
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-12 h-12 md:w-16 md:h-16">
      <path d="M9 17V4l11 2v13" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="6.5" cy="17" r="2.5" fill="currentColor" fillOpacity="0.2" />
      <circle cx="17.5" cy="19" r="2.5" fill="currentColor" fillOpacity="0.2" />
      <path d="M9 9.5l11-2M13 5.5v12.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.6" />
    </svg>
  </div>
);

const Index = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  const { toast } = useToast();
  const [playingTrackId, setPlayingTrackId] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const handlePlayToggle = (track: typeof musicTracks[0]) => {
    if (playingTrackId === track.id) {
      audioRef.current?.pause();
      setPlayingTrackId(null);
    } else {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      audioRef.current = new Audio(track.audioUrl);
      
      audioRef.current.play().then(() => {
        setPlayingTrackId(track.id);
      }).catch((err) => {
        console.error("Audio playback error:", err);
        toast({
          title: "Audio Placeholder Active",
          description: `To play, please place an MP3 file at public${track.audioUrl}`,
          variant: "destructive"
        });
      });

      audioRef.current.onended = () => {
        setPlayingTrackId(null);
      };
    }
  };

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  const [startIndex, setStartIndex] = useState(0);
  const [isMobile, setIsMobile] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  useEffect(() => {
    const maxIndex = isMobile ? musicTracks.length - 1 : musicTracks.length - 3;
    if (startIndex > maxIndex) {
      setStartIndex(maxIndex);
    }
  }, [isMobile, startIndex]);

  useEffect(() => {
    if (isHovered) return;
    const interval = setInterval(() => {
      setStartIndex((prev) => {
        const maxIndex = isMobile ? musicTracks.length - 1 : musicTracks.length - 3;
        return prev >= maxIndex ? 0 : prev + 1;
      });
    }, 4000);
    return () => clearInterval(interval);
  }, [isHovered, isMobile]);

  const handlePrev = (e: React.MouseEvent) => {
    e.stopPropagation();
    const maxIndex = isMobile ? musicTracks.length - 1 : musicTracks.length - 3;
    setStartIndex((prev) => (prev <= 0 ? maxIndex : prev - 1));
  };

  const handleNext = (e: React.MouseEvent) => {
    e.stopPropagation();
    const maxIndex = isMobile ? musicTracks.length - 1 : musicTracks.length - 3;
    setStartIndex((prev) => (prev >= maxIndex ? 0 : prev + 1));
  };

  usePageMetadata({
    title: "SoLuna - Chord AI Free, Stem Splitter AI & Music Studio Tools",
    description: "The ultimate free music studio: Chord AI free, stem splitter ai, vocal remover, interactive fretboard, and more. Professional AI music tools with no subscription.",
    keywords: "chord ai, chord ai free, stem splitter ai, vocal splitter, vocal remover, music theory, guitar chords, fretboard, scale explorer, music studio, free music tools",
    canonicalUrl: "https://SoLuna.studio",
    ogUrl: "https://SoLuna.studio",
    ogImage: "https://SoLuna.studio/logo.png",
    ogType: "website",
    jsonLd: {
      "@context": "https://schema.org",
      "@graph": [
        {
          "@type": "WebApplication",
          "name": "SoLuna Studio",
          "description": "Professional music theory and AI analysis tools for musicians.",
          "applicationCategory": "MusicApplication",
          "operatingSystem": "Any",
          "url": "https://SoLuna.studio",
          "screenshot": "https://SoLuna.studio/screenshot.png",
          "browserRequirements": "Requires JavaScript. Requires HTML5.",
          "softwareVersion": "1.7.0",
          "author": {
            "@type": "Organization",
            "name": "SoLuna Studio"
          },
          "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
          },
          "potentialAction": {
            "@type": "SearchAction",
            "target": {
              "@type": "EntryPoint",
              "urlTemplate": "https://SoLuna.studio/search?q={search_term_string}"
            },
            "query-input": "required name=search_term_string"
          },
          "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "reviewCount": "128"
          }
        },
        {
          "@type": "WebSite",
          "@id": "https://SoLuna.studio/#website",
          "url": "https://SoLuna.studio",
          "name": "SoLuna",
          "description": "Free Interactive AI Music Studio Tools",
          "potentialAction": {
            "@type": "SearchAction",
            "target": {
              "@type": "EntryPoint",
              "urlTemplate": "https://SoLuna.studio/search?q={search_term_string}"
            },
            "query-input": "required name=search_term_string"
          }
        },
        {
          "@type": "Organization",
          "name": "SoLuna Studio",
          "url": "https://SoLuna.studio",
          "logo": "https://SoLuna.studio/logo.png",
          "sameAs": [
            "https://x.com/SoLunaStudio",
            "https://github.com/SoLuna/SoLuna"
          ]
        }
      ]
    }
  });

  return (
    <div ref={containerRef} className="min-h-screen relative bg-background overflow-x-hidden selection:bg-white/10">
      {/* Aesthetic Background - Clean & Optimized */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute inset-0 bg-background" />
        {/* Subtle Vignette for depth without overhead */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.3)_100%)] light:bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.05)_100%)]" />
      </div>

      <main className="relative z-10">
        <HeroSection />

        {/* AI-Generated Music Samples Section */}
        <section className="px-6 py-8 md:py-16 relative overflow-hidden border-t border-[#D4AF37]/10">
          {/* Background Dotted Circular Lines & Premium Floating Assets */}
          <DottedCircle className="top-[-80px] left-[-80px]" />
          
          {/* Bleeding assets crossing transition from Hero video section */}
          <FloatingTrebleClef className="top-[-40px] left-[15%]" delay="0.5s" />
          <FloatingVinyl className="top-[-60px] right-[25%]" delay="1.5s" />
          <FloatingGlitterGuitar className="top-[-90px] left-[45%] w-14 h-28" delay="2.5s" />
          
          <FloatingTrebleClef className="top-[10%] left-[6%]" />
          <FloatingGlitterGuitar className="bottom-[12%] left-[4%]" delay="0.5s" />
          <FloatingVinyl className="bottom-[12%] right-[10%]" delay="2.5s" />
          
          {/* Central Assets - suspension between cards */}
          <FloatingGlitterNodes className="top-[48%] left-[28%] w-20 h-20 md:w-24 md:h-24" delay="0.9s" />
          <FloatingGlitterGuitar className="top-[52%] left-[62%] w-16 h-32 md:w-20 md:h-40" delay="1.8s" />

          <div className="container mx-auto max-w-6xl relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
              className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-6 md:mb-14 text-left"
            >
              <h2 className="text-4xl md:text-5xl font-semibold tracking-tight font-display max-w-lg bg-clip-text text-transparent bg-gradient-to-r from-[#e5c060] via-[#ffffff] to-[#e5c060]">
                AI-Generated Music Samples.
              </h2>
              <p className="text-white/90 max-w-sm md:text-right font-light leading-relaxed">
                Listen to music tracks created with our AI music generators. Click any card to play.
              </p>
            </motion.div>

            <div 
              className="relative group/carousel px-8 md:px-16"
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
            >
              {/* Carousel Viewport */}
              <div className="overflow-hidden py-4 w-full">
                <div 
                  className="flex transition-transform duration-500 ease-in-out"
                  style={{ 
                    transform: `translateX(-${startIndex * (isMobile ? 100 : 100 / 3)}%)` 
                  }}
                >
                  {musicTracks.map((track, i) => (
                    <div 
                      key={track.id} 
                      className="w-full md:w-1/3 flex-shrink-0 px-2 md:px-3 flex flex-col"
                    >
                      <motion.div
                        initial={{ opacity: 0, y: 24 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-60px" }}
                        transition={{ delay: (i % 3) * 0.05, duration: 0.5, ease: "easeOut" }}
                        className="flex flex-col h-full rounded-xl md:rounded-[1.75rem] overflow-hidden border border-border bg-card/25 backdrop-blur-sm transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:border-[#D4AF37]/30 group relative cursor-pointer shadow-sm select-none"
                        onClick={() => handlePlayToggle(track)}
                      >
                        <div className={`absolute inset-0 bg-gradient-to-br ${track.color} opacity-0 group-hover:opacity-40 transition-opacity duration-500 z-0`} />
                        
                        {/* Cover Image Container */}
                        <div className="relative aspect-[3/2] w-full overflow-hidden border-b border-border z-10">
                          <img
                            src={track.cover}
                            alt={track.title}
                            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                          />
                          
                          {/* Play/Pause Overlay */}
                          <div className="absolute inset-0 bg-black/45 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-20">
                            <div className="w-8 h-8 md:w-14 md:h-14 rounded-full bg-[#D4AF37]/10 backdrop-blur-md border border-[#D4AF37]/25 flex items-center justify-center shadow-lg transform transition-transform duration-300 group-hover:scale-110">
                              {playingTrackId === track.id ? (
                                <Pause className="w-4 h-4 md:w-6 md:h-6 text-white fill-white" />
                              ) : (
                                <Play className="w-4 h-4 md:w-6 md:h-6 text-white fill-white ml-0.5" />
                              )}
                            </div>
                          </div>
                          
                          {/* Playing Indicator */}
                          {playingTrackId === track.id && (
                            <div className="absolute bottom-2 right-2 md:bottom-3 md:right-3 bg-black/60 backdrop-blur-md border border-[#D4AF37]/20 px-1.5 py-1 md:px-2.5 md:py-1.5 rounded-md md:rounded-lg flex gap-0.5 md:gap-1 items-end h-5 md:h-7 z-20">
                              <span className="w-0.5 bg-[#D4AF37] rounded-full animate-[bounce_0.8s_infinite_100ms] h-2 md:h-3" />
                              <span className="w-0.5 bg-[#D4AF37] rounded-full animate-[bounce_0.8s_infinite_300ms] h-3 md:h-4" />
                              <span className="w-0.5 bg-[#D4AF37] rounded-full animate-[bounce_0.8s_infinite_200ms] h-2.5 md:h-3.5" />
                              <span className="w-0.5 bg-[#D4AF37] rounded-full animate-[bounce_0.8s_infinite_400ms] h-1.5 md:h-2" />
                            </div>
                          )}
                        </div>

                        {/* Text Info & Badges */}
                        <div className="p-3 md:p-6 flex-1 flex flex-col justify-between relative z-10">
                          <div>
                            <h3 className="text-white font-medium text-xs sm:text-sm md:text-lg leading-snug group-hover:text-[#F4D06F] transition-colors font-display line-clamp-2">
                              {track.title}
                            </h3>
                            <p className="text-white/40 text-[9px] md:text-xs font-normal mt-0.5">({track.subtitle})</p>
                            
                            <div className="flex items-center gap-1 text-white/50 text-[9px] md:text-[11px] mt-1.5 md:mt-2 font-medium">
                              <Clock className="w-3 h-3 md:w-3.5 md:h-3.5" />
                              <span>{track.duration}</span>
                            </div>
                          </div>

                          {/* Badges/Tags - hidden on mobile for clean fit */}
                          <div className="hidden sm:flex flex-wrap gap-1.5 mt-4">
                            {track.tags.slice(0, 3).map((tag) => (
                              <span
                                key={tag}
                                className="inline-flex items-center gap-1 text-[9px] px-2 py-0.5 rounded-full bg-[#D4AF37]/10 border border-[#D4AF37]/20 text-[#E8C75A] font-medium"
                              >
                                <Tag className="w-2 h-2" />
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      </motion.div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Navigation Arrows */}
              <button 
                onClick={handlePrev}
                className="absolute left-[-12px] md:left-0 top-1/2 -translate-y-1/2 z-30 w-10 h-10 md:w-12 md:h-12 rounded-full bg-black/50 hover:bg-black/75 md:bg-white/10 md:hover:bg-white/20 border border-[#D4AF37]/25 flex items-center justify-center text-white backdrop-blur-md transition-all duration-300 hover:scale-110 active:scale-95 cursor-pointer shadow-[0_0_20px_rgba(0,0,0,0.5)] opacity-100 md:opacity-90 hover:opacity-100 flex-shrink-0"
                aria-label="Previous tracks"
              >
                <ChevronLeft className="w-5 h-5 md:w-6 md:h-6" />
              </button>

              <button 
                onClick={handleNext}
                className="absolute right-[-12px] md:right-0 top-1/2 -translate-y-1/2 z-30 w-10 h-10 md:w-12 md:h-12 rounded-full bg-black/50 hover:bg-black/75 md:bg-white/10 md:hover:bg-white/20 border border-[#D4AF37]/25 flex items-center justify-center text-white backdrop-blur-md transition-all duration-300 hover:scale-110 active:scale-95 cursor-pointer shadow-[0_0_20px_rgba(0,0,0,0.5)] opacity-100 md:opacity-90 hover:opacity-100 flex-shrink-0"
                aria-label="Next tracks"
              >
                <ChevronRight className="w-5 h-5 md:w-6 md:h-6" />
              </button>
            </div>
          </div>
        </section>

        {/* Interactive Tools Suite Section */}
        <section className="px-6 py-8 md:py-16 relative overflow-hidden border-t border-[#D4AF37]/10">
          {/* Background Dotted Circular Lines & Premium Floating Assets */}
          <DottedCircle className="bottom-[-100px] right-[-100px]" />
          <FloatingVinyl className="top-[15%] right-[8%]" delay="0.5s" />
          <FloatingGlitterKeyboard className="bottom-[15%] right-[6%]" delay="1.2s" />
          <FloatingTrebleClef className="bottom-[10%] left-[10%]" delay="3s" />
          
          {/* Central Assets - suspension between cards */}
          <FloatingGlitterNodes className="top-[45%] left-[50%] w-24 h-24" delay="1.4s" />
          <FloatingGlitterGuitar className="top-[55%] left-[25%] w-16 h-32 md:w-20 md:h-40" delay="0.7s" />
          <FloatingGlitterNodes className="top-[38%] left-[75%] w-20 h-20" delay="2.1s" />

          <div className="container mx-auto max-w-6xl relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
              className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-6 md:mb-14 text-left"
            >
              <h2 className="text-4xl md:text-5xl font-semibold tracking-tight font-display max-w-lg bg-clip-text text-transparent bg-gradient-to-r from-[#e5c060] via-[#ffffff] to-[#e5c060]">
                Experiment with new sound.
              </h2>
              <p className="text-white/90 max-w-sm md:text-right font-light leading-relaxed">
                Interactive visualization tools designed to build muscle memory, pitch precision, and deep theoretical mastery.
              </p>
            </motion.div>

            <div className="grid grid-cols-3 lg:grid-cols-4 gap-2 sm:gap-4 md:gap-6">
              {toolCards.map((tool, i) => (
                <motion.div
                  key={tool.title}
                  initial={{ opacity: 0, y: 24 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-60px" }}
                  transition={{ delay: i * 0.05, duration: 0.5, ease: "easeOut" }}
                  className="group h-full"
                >
                  <Link
                    to={tool.to}
                    aria-label={`Open the ${tool.title} tool: ${tool.desc}`}
                    className="block rounded-xl md:rounded-[1.75rem] overflow-hidden border border-border bg-card/25 backdrop-blur-sm transition-all duration-300 hover:shadow-xl hover:-translate-y-1 hover:border-[#D4AF37]/30 group relative shadow-sm h-36 sm:h-52 lg:h-64 dark"
                  >
                    <div className={`absolute inset-0 bg-gradient-to-br ${tool.color} opacity-0 group-hover:opacity-10 transition-opacity duration-500 z-0`} />
                    
                    {/* Cover Image Container */}
                    <div className="relative h-full w-full overflow-hidden z-10">
                      <img
                        src={tool.image}
                        alt={tool.title}
                        className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                      />
                      {/* Premium Dark Gradient Overlay for text readability */}
                      <div className="absolute inset-0 bg-gradient-to-t from-black/95 via-black/45 to-black/10 transition-opacity duration-500" />
                      
                      {/* Category Badge on Top-Left */}
                      <div className="absolute top-2 left-2 sm:top-4 sm:left-4 px-1.5 py-0.5 sm:px-2.5 sm:py-1 rounded-full bg-black/60 backdrop-blur-md text-[7px] sm:text-[9px] uppercase tracking-wider text-white border border-[#D4AF37]/20 font-bold flex items-center gap-1 shadow-md">
                        <tool.icon className="w-2.5 h-2.5 sm:w-3 sm:h-3 text-[#E8C75A]" />
                        <span className="hidden sm:inline">{tool.category}</span>
                      </div>

                      {/* Title and Description at the bottom of the photo */}
                      <div className="absolute bottom-0 left-0 right-0 p-2 sm:p-4 lg:p-6 text-left space-y-0.5 sm:space-y-1">
                        <h3 className="text-[10px] sm:text-sm lg:text-lg font-medium text-white group-hover:text-[#F4D06F] transition-colors font-display truncate">
                          {tool.title}
                        </h3>
                        <p className="text-[8px] sm:text-xs text-white/70 leading-tight sm:leading-relaxed font-light line-clamp-2">
                          {tool.desc}
                        </p>
                      </div>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* AI Composer Suite Section */}
        <section className="px-6 py-8 md:py-16 relative overflow-hidden border-t border-[#D4AF37]/10">
          {/* Background Dotted Circular Lines & Premium Floating Assets */}
          <DottedCircle className="top-[-60px] right-[40px]" />
          <FloatingVinyl className="top-[10%] left-[8%]" delay="2.2s" />
          <FloatingGlitterNodes className="bottom-[12%] right-[40px]" delay="2s" />
          <FloatingTrebleClef className="bottom-[12%] right-[10%]" delay="0.8s" />
          
          {/* Central Assets - suspension between cards */}
          <FloatingGlitterNodes className="top-[48%] left-[33%] w-24 h-24" delay="1.1s" />

          <div className="container mx-auto max-w-6xl relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
              className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-6 md:mb-14 text-left"
            >
              <h2 className="text-4xl md:text-5xl font-semibold tracking-tight font-display max-w-lg bg-clip-text text-transparent bg-gradient-to-r from-[#e5c060] via-[#ffffff] to-[#e5c060]">
                SoLuna AI Suite
              </h2>
              <p className="text-white/90 max-w-sm md:text-right font-light leading-relaxed">
                Calibrated specifically for precise harmonic analysis and pristine stem isolation. Isolate tracks, extract pristine vocals, and transcribe complex chord structures instantly.
              </p>
            </motion.div>

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-4 md:gap-6">
              {featuredTools.map((tool, i) => (
                <motion.div
                  key={tool.title}
                  initial={{ opacity: 0, y: 24 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-60px" }}
                  transition={{ delay: i * 0.05, duration: 0.5, ease: "easeOut" }}
                  className="relative group rounded-xl md:rounded-[1.75rem] overflow-hidden border border-border h-40 sm:h-56 lg:h-[280px] cursor-pointer"
                >
                  <Link to={tool.to} className="block w-full h-full relative dark">
                    {/* Full height background image */}
                    <img
                      src={tool.image}
                      alt={tool.title}
                      className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                    />

                    {/* Dark overlay gradient */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/95 via-black/45 to-transparent z-10" />

                    {/* Category badge */}
                    <div className="absolute top-2 left-2 sm:top-4 sm:left-4 z-20 px-1.5 py-0.5 sm:px-2 sm:py-0.5 rounded-md bg-card/60 backdrop-blur-sm border border-border text-[7px] sm:text-[9px] font-bold text-white uppercase tracking-widest">
                      {tool.category}
                    </div>

                    {/* Title and Description at the bottom of the photo */}
                    <div className="absolute bottom-0 left-0 right-0 p-2 sm:p-4 lg:p-6 text-left space-y-0.5 sm:space-y-1 z-20">
                      <h3 className="text-[10px] sm:text-sm lg:text-lg font-medium text-white group-hover:text-[#F4D06F] transition-colors font-display truncate">
                        {tool.title}
                      </h3>
                      <p className="text-[8px] sm:text-xs text-white/70 leading-tight sm:leading-relaxed font-light line-clamp-2">
                        {tool.desc}
                      </p>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        <WhyChoose />
      </main>

      <Footer />
    </div>
  );
};

export default Index;
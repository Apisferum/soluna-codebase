import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

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
    <div className="w-20 h-20 md:w-28 md:h-28 bg-zinc-950/80 backdrop-blur-sm border border-white/10 p-1.5 rounded-2xl shadow-2xl transform rotate-6 hover:rotate-12 transition-transform duration-500">
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

const REASONS = [
  {
    title: "Structural Coherence",
    desc: "A dedicated planning pass keeps motifs, sections and cadences consistent across an entire piece — not just the next few bars.",
  },
  {
    title: "Multi-Adapter Fine-Tuning",
    desc: "LoRA adapters merged with TIES let you blend genres and playing styles instead of committing to a single trained sound.",
  },
  {
    title: "Motif Memory",
    desc: "A FAISS-backed memory recalls earlier themes so recapitulations and variations feel intentional, not repeated by accident.",
  },
  {
    title: "Plug & Play Export",
    desc: "Every generation exports to standard MIDI with correct GM program numbers, ready for your DAW of choice.",
  },
  {
    title: "Full Ensemble, Not Presets",
    desc: "Score across strings, brass, woodwinds, mallets and world instruments — arrangements sound like a real ensemble.",
  },
  {
    title: "Deterministic Evaluation",
    desc: "Every run is measured against reproducible metrics, so you can trust that a good result wasn't a lucky seed.",
  },
];

const WhyChoose = () => {
  return (
    <section className="hidden md:block px-6 py-16 relative overflow-hidden border-t border-white/[0.03]">
      {/* Background Dotted Circular Lines & Premium Floating Assets */}
      <DottedCircle className="top-[-100px] left-[50px]" />
      <FloatingTrebleClef className="top-[10%] left-[8%]" />
      <FloatingGlitterGuitar className="top-[22%] right-[5%]" delay="1.5s" />
      <FloatingGlitterNodes className="bottom-[20%] left-[15%]" delay="0.8s" />
      <FloatingVinyl className="bottom-[10%] left-[10%]" delay="1.5s" />
      
      {/* Central Assets - suspension between cards */}
      <FloatingGlitterNodes className="top-[45%] left-[50%] w-24 h-24" delay="1.3s" />
      <FloatingGlitterGuitar className="top-[55%] left-[68%] w-16 h-32 md:w-20 md:h-40" delay="2.1s" />

      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute -top-40 left-1/4 w-[30rem] h-[30rem] rounded-full bg-emerald-400/10 blur-[120px]" />
        <div className="absolute -top-20 right-1/4 w-[26rem] h-[26rem] rounded-full bg-indigo-400/10 blur-[120px]" />
      </div>

      <div className="container mx-auto max-w-6xl relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-14 text-left"
        >
          <h2 className="text-4xl md:text-5xl font-semibold tracking-tight font-display max-w-lg bg-clip-text text-transparent bg-gradient-to-r from-[#e5c060] via-[#ffffff] to-[#e5c060]">
            Why musicians choose SoLuna
          </h2>
          <p className="text-white/90 max-w-sm md:text-right font-light leading-relaxed">
            Stop fighting a black-box generator. Compose with a system built for structure and control.
          </p>
        </motion.div>

        <div className="grid grid-cols-2 gap-4 lg:gap-6">
          {REASONS.map((reason, i) => (
            <motion.div
              key={reason.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ delay: i * 0.05, duration: 0.5, ease: "easeOut" }}
              className="flex gap-2 lg:gap-4 items-center lg:items-start p-4 lg:p-8 rounded-2xl lg:rounded-[1.75rem] bg-card/45 backdrop-blur-sm border border-border relative overflow-hidden h-full text-left"
            >
              <div className="hidden lg:block flex-shrink-0 mt-1.5">
                <ArrowRight className="w-5 h-5 text-foreground/80" />
              </div>
              <div className="space-y-1 lg:space-y-2">
                <h3 className="text-sm lg:text-xl font-medium text-foreground font-display">
                  {reason.title}
                </h3>
                <p className="hidden lg:block text-xs lg:text-sm text-muted-foreground leading-relaxed font-light">
                  {reason.desc}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default WhyChoose;

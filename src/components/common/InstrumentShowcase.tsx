import { motion } from "framer-motion";
import { INSTRUMENT_CATEGORIES, TOTAL_INSTRUMENT_COUNT } from "@/data/instruments";
import { Piano, Guitar, Wind, Drum, Mic2, Radio, Globe2, Waves, SlidersHorizontal } from "lucide-react";

const ICONS: Record<string, typeof Piano> = {
  keys: Piano,
  "guitar-bass": Guitar,
  "organ-accordion": Radio,
  strings: Waves,
  brass: Wind,
  woodwinds: Wind,
  "mallets-percussion": Drum,
  voice: Mic2,
  world: Globe2,
  synth: SlidersHorizontal,
};

const InstrumentShowcase = () => {
  return (
    <section className="px-6 py-20">
      <div className="container mx-auto max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          className="text-center space-y-4 mb-14"
        >
          <span className="inline-flex items-center px-4 py-1.5 rounded-full border border-border bg-card/50 backdrop-blur-sm text-muted-foreground text-[10px] font-bold tracking-[0.3em] uppercase">
            {TOTAL_INSTRUMENT_COUNT}+ Voices, One Engine
          </span>
          <h2 className="text-4xl md:text-5xl font-light tracking-tight text-foreground font-display">
            Not just guitar and piano.
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto font-light">
            Every arrangement is scored across a full General MIDI palette — strings, brass,
            woodwinds, mallets, world instruments and synths — so a generated piece sounds like a
            real ensemble, not a demo.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {INSTRUMENT_CATEGORIES.map((cat, i) => {
            const Icon = ICONS[cat.id] ?? Piano;
            return (
              <motion.div
                key={cat.id}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ delay: i * 0.05, duration: 0.5, ease: "easeOut" }}
                className="p-6 rounded-[1.5rem] glass-card border border-border relative overflow-hidden group"
              >
                <div className="relative z-10 space-y-3">
                  <div className="w-11 h-11 rounded-xl bg-card border border-border flex items-center justify-center group-hover:bg-card/80 transition-all duration-300">
                    <Icon className="w-5 h-5 text-foreground" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-foreground font-display">{cat.label}</h3>
                    <p className="text-xs text-muted-foreground mt-1">{cat.description}</p>
                  </div>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {cat.instruments.slice(0, 5).map((name) => (
                      <span
                        key={name}
                        className="px-2 py-1 rounded-full bg-secondary text-secondary-foreground text-[11px] font-medium"
                      >
                        {name}
                      </span>
                    ))}
                    {cat.instruments.length > 5 && (
                      <span className="px-2 py-1 rounded-full bg-secondary text-secondary-foreground text-[11px] font-medium">
                        +{cat.instruments.length - 5} more
                      </span>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default InstrumentShowcase;

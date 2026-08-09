import { memo, useMemo } from "react";
import { useGlobalInstrument } from "@/hooks/useGlobalInstrument";
import PianoChordDiagram from "./PianoChordDiagram";

interface ChordDiagramProps {
  frets: number[];
  fingers: string[];
  chordName: string;
  compact?: boolean;
  layout?: "piano" | "bass" | "guitar";
}

const GUITAR_TUNING_MIDI = [40, 45, 50, 55, 59, 64]; // Standard tuning E2, A2, D3, G3, B3, E4

const ChordDiagram = memo(({ frets, fingers, chordName, compact = false, layout: forcedLayout }: ChordDiagramProps) => {
  const [globalInstrument] = useGlobalInstrument();

  const layout = useMemo(() => {
    if (forcedLayout) return forcedLayout;

    const name = globalInstrument.toLowerCase();
    if (
      name.includes("piano") ||
      name.includes("rhodes") ||
      name.includes("clavinet") ||
      name.includes("harpsichord") ||
      name.includes("celesta") ||
      name.includes("organ") ||
      name.includes("accordion") ||
      name.includes("harmonica") ||
      name.includes("keyboard") ||
      name.includes("synth") ||
      name.includes("choir") ||
      name.includes("voice") ||
      name.includes("pad") ||
      name.includes("bell") ||
      name.includes("music box") ||
      name.includes("glockenspiel") ||
      name.includes("vibraphone") ||
      name.includes("marimba") ||
      name.includes("xylophone") ||
      name.includes("timpani") ||
      name.includes("dulcimer") ||
      name.includes("harp")
    ) {
      return "piano";
    }
    if (name.includes("bass") || name.includes("contrabass") || name.includes("double bass")) {
      return "bass";
    }
    return "guitar";
  }, [globalInstrument, forcedLayout]);

  // Handle Piano representation
  const midiNotes = useMemo(() => {
    const notes: number[] = [];
    frets.forEach((fret, i) => {
      if (fret !== -1 && i < GUITAR_TUNING_MIDI.length) {
        notes.push(GUITAR_TUNING_MIDI[i] + fret);
      }
    });
    return notes;
  }, [frets]);

  if (layout === "piano") {
    return (
      <div className="flex flex-col items-center">
        {!compact && (
          <h4 className="text-sm font-semibold mb-3 text-foreground">{chordName}</h4>
        )}
        <PianoChordDiagram midiNotes={midiNotes} size={compact ? 200 : 280} />
      </div>
    );
  }

  // Handle Fretboard (Bass or Guitar) representations
  const isBass = layout === "bass";
  const strings = isBass ? 4 : 6;
  const numFrets = 5;
  const size = compact ? 200 : 280;
  const padding = compact ? 20 : 30;
  const stringSpacing = (size - 2 * padding) / (strings - 1);
  const fretSpacing = (size - 2 * padding) / numFrets;

  // Use sliced arrays for 4-string bass
  const activeFrets = isBass ? frets.slice(0, 4) : frets;
  const activeFingers = isBass ? fingers.slice(0, 4) : fingers;
  const stringLabels = isBass ? ["E", "A", "D", "G"] : ["E", "A", "D", "G", "B", "e"];

  return (
    <div className="flex flex-col items-center select-none animate-in fade-in zoom-in-95 duration-300">
      {!compact && (
        <h4 className="text-sm font-semibold mb-3 text-foreground">{chordName}</h4>
      )}
      
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="chord-diagram"
        role="img"
        aria-label={`${chordName} chord diagram`}
      >
        {/* Finger positions above nut */}
        <g className="finger-markers">
          {activeFingers.map((finger, i) => (
            <text
              key={`finger-${i}`}
              x={padding + i * stringSpacing}
              y={padding - 8}
              textAnchor="middle"
              className={`text-xs font-semibold ${
                finger === "x" ? "fill-destructive" : "fill-muted-foreground/60"
              }`}
            >
              {finger === "x" ? "✕" : finger}
            </text>
          ))}
        </g>

        {/* Fret lines (horizontal) */}
        <g className="fret-lines">
          {Array.from({ length: numFrets + 1 }).map((_, i) => (
            <line
              key={`fret-${i}`}
              x1={padding}
              y1={padding + i * fretSpacing}
              x2={size - padding}
              y2={padding + i * fretSpacing}
              stroke="hsl(var(--border))"
              strokeWidth={i === 0 ? 3 : 1.5}
              className="opacity-40"
            />
          ))}
        </g>

        {/* String lines (vertical) */}
        <g className="string-lines">
          {Array.from({ length: strings }).map((_, i) => (
            <line
              key={`string-${i}`}
              x1={padding + i * stringSpacing}
              y1={padding}
              x2={padding + i * stringSpacing}
              y2={size - padding}
              stroke="hsl(var(--border))"
              strokeWidth={isBass ? 2 : 1}
              className="opacity-30"
            />
          ))}
        </g>

        {/* Finger dots */}
        <g className="finger-dots">
          {activeFrets.map((fret, stringIndex) => {
            if (fret <= 0) return null;
            
            const x = padding + stringIndex * stringSpacing;
            const y = padding + (fret - 0.5) * fretSpacing;

            return (
              <circle
                key={`dot-${stringIndex}`}
                cx={x}
                cy={y}
                r={compact ? 8 : 10}
                className="fill-primary stroke-primary-foreground animate-scale-in"
                strokeWidth={2}
                style={{ 
                  filter: "drop-shadow(0 2px 4px hsl(var(--primary) / 0.4))",
                  animationDelay: `${stringIndex * 0.05}s`
                }}
              />
            );
          })}
        </g>

        {/* String labels at bottom */}
        <g className="string-labels">
          {stringLabels.map((note, i) => (
            <text
              key={`label-${i}`}
              x={padding + i * stringSpacing}
              y={size - padding + 16}
              textAnchor="middle"
              className="text-[10px] font-medium fill-muted-foreground/60"
            >
              {note}
            </text>
          ))}
        </g>
      </svg>
    </div>
  );
});

ChordDiagram.displayName = "ChordDiagram";

export default ChordDiagram;

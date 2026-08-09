import { memo, useMemo } from "react";

interface PianoChordDiagramProps {
  midiNotes: number[];
  size?: number;
}

export const PianoChordDiagram = memo(({ midiNotes, size = 200 }: PianoChordDiagramProps) => {
  const paddingX = 10;
  const paddingY = 15;
  const H = size * 0.45; // Height of white keys
  const W = (size - 2 * paddingX) / 14; // White key width (14 white keys for 2 octaves)
  const BW = W * 0.6; // Black key width
  const BH = H * 0.6; // Black key height

  // Transpose notes to range [48, 71] (C3 to B4)
  const activePitches = useMemo(() => {
    const pitches = new Set<number>();
    midiNotes.forEach((note) => {
      let pitch = note;
      while (pitch < 48) pitch += 12;
      while (pitch > 71) pitch -= 12;
      pitches.add(pitch - 48); // Store relative pitch (0 to 23)
    });
    return pitches;
  }, [midiNotes]);

  const whiteKeys = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23];
  
  const blackKeys = [
    { pitch: 1, relativeTo: 1 },  // C#
    { pitch: 3, relativeTo: 2 },  // D#
    { pitch: 6, relativeTo: 4 },  // F#
    { pitch: 8, relativeTo: 5 },  // G#
    { pitch: 10, relativeTo: 6 }, // A#
    { pitch: 13, relativeTo: 8 },  // C#
    { pitch: 15, relativeTo: 9 },  // D#
    { pitch: 18, relativeTo: 11 }, // F#
    { pitch: 20, relativeTo: 12 }, // G#
    { pitch: 22, relativeTo: 13 }  // A#
  ];

  return (
    <div className="flex flex-col items-center select-none animate-in fade-in zoom-in-95 duration-300">
      <svg
        width={size}
        height={H + 2 * paddingY}
        viewBox={`0 0 ${size} ${H + 2 * paddingY}`}
        className="piano-diagram"
      >
        {/* Render White Keys */}
        <g>
          {whiteKeys.map((pitch, idx) => {
            const x = paddingX + idx * W;
            const isActive = activePitches.has(pitch);
            return (
              <g key={`white-${pitch}`}>
                <rect
                  x={x}
                  y={paddingY}
                  width={W}
                  height={H}
                  rx={2}
                  className={`transition-all duration-300 ${
                    isActive 
                      ? "fill-primary/25 stroke-primary/60" 
                      : "fill-white/[0.03] stroke-white/10 hover:fill-white/[0.06]"
                  }`}
                  strokeWidth={1}
                />
                {isActive && (
                  <circle
                    cx={x + W / 2}
                    cy={paddingY + H - 12}
                    r={3.5}
                    className="fill-primary animate-pulse"
                    style={{ filter: "drop-shadow(0 0 4px hsl(var(--primary) / 0.8))" }}
                  />
                )}
              </g>
            );
          })}
        </g>

        {/* Render Black Keys */}
        <g>
          {blackKeys.map(({ pitch, relativeTo }) => {
            const x = paddingX + relativeTo * W - BW / 2;
            const isActive = activePitches.has(pitch);
            return (
              <g key={`black-${pitch}`}>
                <rect
                  x={x}
                  y={paddingY}
                  width={BW}
                  height={BH}
                  rx={1.5}
                  className={`transition-all duration-300 ${
                    isActive 
                      ? "fill-primary/45 stroke-primary/85" 
                      : "fill-[#0a0a0a]/95 stroke-white/[0.06] hover:fill-[#121212]/95"
                  }`}
                  strokeWidth={1}
                />
                {isActive && (
                  <circle
                    cx={x + BW / 2}
                    cy={paddingY + BH - 8}
                    r={2.5}
                    className="fill-primary animate-pulse"
                    style={{ filter: "drop-shadow(0 0 3px hsl(var(--primary) / 0.8))" }}
                  />
                )}
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
});

PianoChordDiagram.displayName = "PianoChordDiagram";
export default PianoChordDiagram;

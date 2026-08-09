import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";

interface Tool {
  name: string;
  path: string;
  description: string;
}

const ALL_TOOLS: Tool[] = [
  { name: "Chord AI", path: "/chord-ai", description: "Extract chords, key & tempo from any song with AI." },
  { name: "Vocal Splitter", path: "/vocal-splitter", description: "Isolate vocals and instrumentals from any track." },
  { name: "Stem Separator", path: "/stem-separator", description: "Split songs into 6 stems: vocals, drums, bass, guitar, piano & more." },
  { name: "Fretboard", path: "/fretboard", description: "Interactive guitar fretboard with scales, chords & sound." },
  { name: "Chord Library", path: "/chords", description: "Browse 1000+ chord diagrams with voicings and finger positions." },
  { name: "Scale Explorer", path: "/scales", description: "Visualize scales and modes across the guitar neck." },
  { name: "Jam Studio", path: "/jam", description: "Loop chord progressions with AI piano and pad accompaniment." },
  { name: "Music Theory", path: "/theory", description: "Interactive Circle of Fifths and harmonic analysis tools." },
  { name: "Metronome", path: "/metronome", description: "High-precision online metronome with adjustable tempo." },
  { name: "Tuner", path: "/tuner", description: "Chromatic tuner with cent-level accuracy for any instrument." },
  { name: "Ear Training", path: "/ear-training", description: "Gamified ear training for intervals, chords & pitch." },
];

interface RelatedToolsProps {
  /** The path of the current page (e.g. "/chord-ai") so it is excluded from the list. */
  currentPath: string;
  /** Maximum number of tools to show. Defaults to 4. */
  maxItems?: number;
}

const RelatedTools = ({ currentPath, maxItems = 4 }: RelatedToolsProps) => {
  return null;
};

export default RelatedTools;

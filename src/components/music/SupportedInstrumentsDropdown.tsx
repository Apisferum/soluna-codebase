import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectLabel,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { INSTRUMENT_CATEGORIES } from "@/data/instruments";
import { useGlobalInstrument } from "@/hooks/useGlobalInstrument";
import { Sparkles } from "lucide-react";

interface Props {
  className?: string;
  label?: string;
}

export default function SupportedInstrumentsDropdown({ className, label = "Playback Instrument" }: Props) {
  const [instrument, setInstrument] = useGlobalInstrument();

  return (
    <div className={`space-y-1.5 min-w-[200px] text-left ${className || ""}`}>
      <span className="text-[10px] uppercase tracking-widest text-muted-foreground/60 font-bold flex items-center gap-1.5">
        {/* <Sparkles className="w-3.5 h-3.5 text-primary" /> */}
        {label}
      </span>
      {/* <Select value={instrument} onValueChange={setInstrument}>
        <SelectTrigger className="h-9 rounded-xl border border-border bg-card/60 hover:bg-accent hover:text-accent-foreground text-xs text-foreground transition-all duration-300 shadow-sm">
          <SelectValue placeholder="Select instrument" />
        </SelectTrigger>
        <SelectContent className="max-h-[300px] shadow-xl rounded-xl backdrop-blur-md p-1.5 z-50">
          {INSTRUMENT_CATEGORIES.map((category) => (
            <SelectGroup key={category.id}>
              <SelectLabel className="text-[9px] uppercase tracking-widest text-muted-foreground/50 font-bold pl-3 py-1.5">
                {category.label}
              </SelectLabel>
              {category.instruments.map((inst) => (
                <SelectItem
                  key={inst}
                  value={inst}
                  className="text-xs cursor-pointer focus:bg-accent focus:text-accent-foreground transition-colors rounded-lg"
                >
                  {inst}
                </SelectItem>
              ))}
            </SelectGroup>
          ))}
        </SelectContent>
      </Select> */}
    </div>
  );
}

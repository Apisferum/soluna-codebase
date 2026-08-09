import { useState, useEffect } from "react";

export function useGlobalInstrument() {
    const [inst, setInst] = useState(() => {
        return localStorage.getItem("global_instrument") || "Grand Piano";
    });

    const setGlobalInstrument = (newInst: string) => {
        setInst(newInst);
        localStorage.setItem("global_instrument", newInst);
        // Dispatch event for local cross-component synchronization
        window.dispatchEvent(new Event("global_instrument_change"));
    };

    useEffect(() => {
        const handler = () => {
            setInst(localStorage.getItem("global_instrument") || "Grand Piano");
        };
        window.addEventListener("global_instrument_change", handler);
        return () => window.removeEventListener("global_instrument_change", handler);
    }, []);

    return [inst, setGlobalInstrument] as const;
}

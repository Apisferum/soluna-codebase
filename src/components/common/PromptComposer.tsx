import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

const PromptComposer = () => {
  const [prompt, setPrompt] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const navigate = useNavigate();

  const handleSubmit = () => {
    if (!prompt.trim()) {
      textareaRef.current?.focus();
      return;
    }
    navigate(`/generation?prompt=${encodeURIComponent(prompt)}`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
      className="max-w-3xl mx-auto w-full"
    >
      <div id="video-prompt-bar" className="flex items-center gap-1.5 sm:gap-2 w-full rounded-full pl-4 sm:pl-6 pr-1.5 sm:pr-2 py-1.5 sm:py-2">
        <textarea
          ref={textareaRef}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit();
            }
          }}
          placeholder="Describe your music..."
          rows={1}
          id="video-prompt-input"
          className="flex-1 outline-none ring-0 resize-none text-xs sm:text-base placeholder:text-xs sm:placeholder:text-base font-normal leading-normal py-1 sm:py-2"
        />

        <button
          type="button"
          onClick={handleSubmit}
          id="video-prompt-button"
          className="flex items-center gap-1 sm:gap-2 rounded-full text-xs sm:text-sm font-medium px-3 sm:px-5 py-2 sm:py-2.5 transition-colors shrink-0"
        >
          <Sparkles className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          <span id="video-prompt-button-text">Generate</span>
        </button>
      </div>
    </motion.div>
  );
};

export default PromptComposer;
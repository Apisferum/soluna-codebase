import { Link } from "react-router-dom";
import { Library, LogIn, UserPlus } from "lucide-react";

import PromptComposer from "@/components/common/PromptComposer";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";

const HeroSection = () => {
  const { isLoggedIn } = useAuth();

  return (
    <section className="dark relative h-screen min-h-[720px] w-full overflow-hidden">
      {/* Background video */}
      <video
        className="absolute inset-0 h-full w-full object-cover"
        src="/videos/hero-compose.mp4"
        poster="/images/hero-poster.jpg"
        autoPlay
        loop
        muted
        playsInline
      />

      {/* Scrim for text legibility */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "linear-gradient(to top, rgba(0,0,0,0.88) 0%, rgba(0,0,0,0.4) 40%, rgba(0,0,0,0.15) 65%, rgba(0,0,0,0.5) 100%), linear-gradient(to right, rgba(0,0,0,0.4) 0%, transparent 30%)",
        }}
      />

      {/* Breadcrumb */}
      <div className="absolute left-8 top-7 z-10 hidden items-center gap-2 text-sm text-white/60 sm:flex">
        <Link to="/" className="transition-colors hover:text-white">
          Home
        </Link>
        <span>/</span>
        <span className="font-medium text-white">Compose</span>
      </div>

      {/* Authentication actions */}
      <div className="absolute right-4 top-4 z-20 flex items-center gap-2 sm:right-8 sm:top-6">
        {!isLoggedIn ? (
          <>
            <Button
              asChild
              size="sm"
              variant="glass"
              className="h-9 rounded-full border-white/20 bg-black/30 px-3 text-white backdrop-blur-md hover:bg-white/15 sm:px-4"
            >
              <Link to="/login" aria-label="Log in to SoLuna">
                <LogIn className="h-4 w-4" />
                <span className="hidden sm:inline">Login</span>
              </Link>
            </Button>

            <Button
              asChild
              size="sm"
              className="h-9 rounded-full bg-white px-4 font-semibold text-black shadow-[0_0_24px_rgba(255,255,255,0.2)] hover:bg-white/90 sm:px-5"
            >
              <Link to="/register" aria-label="Create a free SoLuna account">
                <UserPlus className="h-4 w-4" />
                <span>Join for Free</span>
              </Link>
            </Button>
          </>
        ) : (
          <Button
            asChild
            size="sm"
            className="h-9 rounded-full bg-white px-4 font-semibold text-black shadow-[0_0_24px_rgba(255,255,255,0.2)] hover:bg-white/90 sm:px-5"
          >
            <Link to="/history" aria-label="Open your music history">
              <Library className="h-4 w-4" />
              <span>My Music</span>
            </Link>
          </Button>
        )}
      </div>

      {/* Content */}
      <div className="absolute inset-x-0 bottom-[16%] z-10 px-6">
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="bg-gradient-to-r from-[#e5c060] via-[#ffffff] to-[#e5c060] bg-clip-text text-[clamp(28px,4vw,46px)] font-semibold leading-tight tracking-tight text-transparent">
            The best AI composer for musicians
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-sm leading-relaxed text-white/90 md:text-base">
            Describe a piece in plain language. Neural composition meets
            architectural music theory along with AI-powered chord progressions.
          </p>

          <div className="mt-8">
            <PromptComposer />
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
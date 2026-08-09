import { Link } from "react-router-dom";

const Footer = () => {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="relative z-10 border-t border-white/5 bg-[#000000] pt-8 md:pt-16 pb-8 text-left px-6">
            <div className="container mx-auto max-w-6xl relative z-10">
                <div className="flex flex-col md:flex-row md:justify-between items-start gap-10 mb-12">
                    {/* About Product */}
                    <div className="space-y-4 max-w-md">
                        <div className="flex items-center gap-3">
                            <img src="/logo.png" alt="SoLuna Logo" className="w-8 h-8 object-contain" />
                            <span className="font-bold text-white tracking-tight font-display">SoLuna Studio</span>
                        </div>
                        <p className="text-xs text-muted-foreground leading-relaxed">
                            SoLuna Studio is an advanced AI composition suite where neural music networks meet architectural theory. Built for musicians who value absolute harmonic structure and isolation control.
                        </p>
                    </div>

                    {/* Created By - aligned to the far right, matching cards above */}
                    <div className="space-y-4 md:text-right md:ml-auto">
                        <h4 className="text-sm font-semibold text-white uppercase tracking-wider font-display">Created By</h4>
                        <ul className="space-y-2 text-xs text-muted-foreground">
                            <li className="hover:text-white transition-colors cursor-pointer">Mahigya Dahal</li>
                            <li className="hover:text-white transition-colors cursor-pointer">Daisy Rajbhandari</li>
                            <li className="hover:text-white transition-colors cursor-pointer">Aashish B.K</li>
                        </ul>
                    </div>
                </div>

                <div className="pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4">
                    <p className="text-xs text-muted-foreground text-center md:text-left">
                        © {currentYear} SoLuna Studio. MIT License.
                    </p>
                    <div className="flex items-center gap-6 text-xs text-muted-foreground">
                        <Link to="/" className="hover:text-white transition-colors">Privacy Policy</Link>
                        <Link to="/" className="hover:text-white transition-colors">Terms of Service</Link>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;

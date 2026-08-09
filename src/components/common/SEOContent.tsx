import { useEffect } from "react";
import { Link } from "react-router-dom";

interface FAQItem {
  question: string;
  answer: string;
}

interface SEOContentProps {
  faqs: FAQItem[];
  pageName: string;
}

export const SEOContent: React.FC<SEOContentProps> = ({ faqs, pageName }) => {
  useEffect(() => {
    // Add FAQ Schema
    const faqSchema = {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      mainEntity: faqs.map((faq) => ({
        "@type": "Question",
        name: faq.question,
        acceptedAnswer: {
          "@type": "Answer",
          text: faq.answer,
        },
      })),
    };

    const schemaId = `faq-schema-${pageName}`;
    let script = document.getElementById(schemaId) as HTMLScriptElement | null;
    if (!script) {
      script = document.createElement("script");
      script.type = "application/ld+json";
      script.id = schemaId;
      document.head.appendChild(script);
    }
    script.textContent = JSON.stringify(faqSchema);

    return () => {
      const el = document.getElementById(schemaId);
      if (el) el.remove();
    };
  }, [faqs, pageName]);

  return null;
};

interface BreadcrumbItem {
  name: string;
  url: string;
  forceRefresh?: boolean;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items }) => {
  useEffect(() => {
    const breadcrumbSchema = {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      itemListElement: items.map((item, idx) => ({
        "@type": "ListItem",
        position: idx + 1,
        name: item.name,
        item: item.url,
      })),
    };

    const schemaId = "breadcrumb-schema";
    let script = document.getElementById(schemaId) as HTMLScriptElement | null;
    if (!script) {
      script = document.createElement("script");
      script.type = "application/ld+json";
      script.id = schemaId;
      document.head.appendChild(script);
    }
    script.textContent = JSON.stringify(breadcrumbSchema);

    return () => {
      const el = document.getElementById(schemaId);
      if (el) el.remove();
    };
  }, [items]);

  return (
    <nav className="flex items-center gap-2 text-xs text-muted-foreground mb-8">
      {items.map((item, idx) => {
        const isInternal = item.url.startsWith("https://SoLuna.studio");
        const toPath = isInternal ? (item.url.replace("https://SoLuna.studio", "") || "/") : item.url;
        
        return (
          <div key={idx} className="flex items-center gap-2">
            {idx > 0 && <span className="opacity-40">/</span>}
            {isInternal && !item.forceRefresh ? (
              <Link
                to={toPath}
                className={idx === items.length - 1 ? "text-white font-medium" : "hover:text-white transition-colors"}
              >
                {item.name}
              </Link>
            ) : (
              <a
                href={toPath}
                className={idx === items.length - 1 ? "text-white font-medium" : "hover:text-white transition-colors"}
              >
                {item.name}
              </a>
            )}
          </div>
        );
      })}
    </nav>
  );
};

export default SEOContent;

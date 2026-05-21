"use client";

import { useState } from "react";
import Link from "next/link";

const langNames = {
  en: "English",
  es: "Español", 
  de: "Deutsch",
};

export function LanguageToggle({ currentLang = "en" }) {
  const [isOpen, setIsOpen] = useState(false);
  const langs = ["en", "es", "de"];

  return (
    <div className="lang-toggle" style={{ position: "relative", display: "inline-flex" }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          background: "transparent",
          border: "1px solid #333",
          padding: "4px 8px",
          borderRadius: "4px",
          color: "#fff",
          cursor: "pointer",
          fontSize: "12px",
        }}
        aria-label="Select language"
      >
        {langNames[currentLang] || "English"}
      </button>
      {isOpen && (
        <div
          style={{
            position: "absolute",
            top: "100%",
            right: 0,
            background: "#1a1a1a",
            border: "1px solid #333",
            borderRadius: "4px",
            overflow: "hidden",
            zIndex: 100,
          }}
        >
          {langs.map((code) => (
            <Link
              key={code}
              href={`/${code}`}
              onClick={() => setIsOpen(false)}
              style={{
                display: "block",
                padding: "6px 12px",
                color: code === currentLang ? "#00ff88" : "#ccc",
                textDecoration: "none",
                fontSize: "12px",
              }}
            >
              {langNames[code]}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export function SiteShell({ children, lang = "en" }) {
  const navItems = [
    { href: "/", label: "Product" },
    { href: "/pricing", label: "Pricing" },
    { href: "/docs", label: "Docs" },
    { href: "/beta", label: "Beta" },
  ];

  return (
    <div className="page-shell">
      <div className="ambient ambient-left"></div>
      <div className="ambient ambient-right"></div>

      <header className="site-header">
        <Link className="brand" href="/">
          <span className="brand-mark" aria-hidden="true"></span>
          <span>SentinelAPI</span>
        </Link>

        <nav className="site-nav" aria-label="Primary">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href}>
              {item.label}
            </Link>
          ))}
          <Link className="nav-cta" href="/beta">
            Join Beta
          </Link>
          <LanguageToggle currentLang={lang} />
        </nav>
      </header>

      <main>{children}</main>

      <footer className="site-footer">
        <p>SentinelAPI</p>
        <p>Runtime security monitoring for developer APIs.</p>
      </footer>
    </div>
  );
}


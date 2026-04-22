import Link from "next/link";

const navItems = [
  { href: "/", label: "Product" },
  { href: "/pricing", label: "Pricing" },
  { href: "/docs", label: "Docs" },
  { href: "/beta", label: "Beta" },
  { href: "/app", label: "Dashboard" },
];

export function SiteShell({ children }) {
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


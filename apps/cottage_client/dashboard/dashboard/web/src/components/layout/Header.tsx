import { useState } from 'react';
import { Menu, X, Sparkles } from 'lucide-react';

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className="landing-header">
      <div className="header-container">
        <div className="header-logo">
          <Sparkles size={24} />
          <span>Boggs Systems</span>
        </div>
        
        <nav className={`header-nav ${isMenuOpen ? 'nav-open' : ''}`}>
          <a href="#robots" className="nav-link">Robots</a>
          <a href="#features" className="nav-link">Features</a>
          <a href="#pricing" className="nav-link">Pricing</a>
          <a href="#contact" className="nav-link">Contact</a>
          <button className="nav-cta">Get Started</button>
        </nav>
        
        <button 
          className="nav-toggle"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>
    </header>
  );
}

import React from 'react';
import { Heart, ExternalLink, Mail, Github, Twitter, Linkedin, Sparkles } from 'lucide-react';
import {
  Link,
  Divider,
  Chip,
} from '@heroui/react';

interface FooterLink {
  label: string;
  href: string;
  external?: boolean;
}

interface AppFooterProps {
  showExtended?: boolean;
  companyName?: string;
  version?: string;
}

const quickLinks: FooterLink[] = [
  { label: 'Documentation', href: '/docs' },
  { label: 'API Reference', href: '/api', external: true },
  { label: 'Support', href: '/support' },
  { label: 'Status', href: '/status', external: true }
];

const legalLinks: FooterLink[] = [
  { label: 'Privacy', href: '/privacy' },
  { label: 'Terms', href: '/terms' },
  { label: 'Security', href: '/security' }
];

const socialLinks = [
  { icon: Github, href: 'https://github.com/vikkichatbot', label: 'GitHub' },
  { icon: Twitter, href: 'https://twitter.com/vikkichatbot', label: 'Twitter' },
  { icon: Linkedin, href: 'https://linkedin.com/company/vikkichatbot', label: 'LinkedIn' }
];

export const AppFooter: React.FC<AppFooterProps> = ({
  showExtended = false,
  companyName = 'Vikki ChatBot',
  version = '1.0.0'
}) => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white/80 backdrop-blur-sm border-t border-default-200/50">
      <div className="flex">
        {/* Left side - Fixed width like sidebar */}
        <div className="w-64 px-4 py-4 flex items-center">
          <span className="text-xs text-default-500">© {currentYear} All rights reserved.</span>
        </div>

        {/* Right side - Flexible content */}
        <div className="flex-1 px-6 py-4">
          <div className="flex items-center justify-end">
            {/* Right side - Social & Made with love */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                {socialLinks.map((social) => (
                  <Link
                    key={social.label}
                    href={social.href}
                    isExternal
                    className="text-default-500 hover:text-primary transition-colors duration-200"
                  >
                    <social.icon className="h-4 w-4" />
                  </Link>
                ))}
              </div>
              <div className="flex items-center gap-1 text-xs text-default-500">
                <span>Made with</span>
                <Heart className="h-3 w-3 text-red-500" />
                <span>by Vikki Team</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );

};

export default AppFooter;

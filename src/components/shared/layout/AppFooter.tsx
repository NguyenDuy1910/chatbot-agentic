import React from 'react';
import { Heart, ExternalLink, Mail, Phone, MapPin, Sparkles } from 'lucide-react';
import {
  Card,
  CardBody,
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

const footerLinks: { [key: string]: FooterLink[] } = {
  product: [
    { label: 'Features', href: '/features' },
    { label: 'Pricing', href: '/pricing' },
    { label: 'API Docs', href: '/docs', external: true },
    { label: 'Changelog', href: '/changelog' }
  ],
  company: [
    { label: 'About Us', href: '/about' },
    { label: 'Careers', href: '/careers' },
    { label: 'Blog', href: '/blog' },
    { label: 'Contact', href: '/contact' }
  ],
  support: [
    { label: 'Help Center', href: '/help' },
    { label: 'Community', href: '/community', external: true },
    { label: 'Status', href: '/status', external: true },
    { label: 'Report Bug', href: '/bug-report' }
  ],
  legal: [
    { label: 'Privacy Policy', href: '/privacy' },
    { label: 'Terms of Service', href: '/terms' },
    { label: 'Cookie Policy', href: '/cookies' },
    { label: 'GDPR', href: '/gdpr' }
  ]
};

export const AppFooter: React.FC<AppFooterProps> = ({
  showExtended = false,
  companyName = 'Vikki ChatBot',
  version = '1.0.0'
}) => {
  const currentYear = new Date().getFullYear();

  if (!showExtended) {
    return (
      <footer className="bg-background border-t border-divider">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <p className="text-sm text-default-600">
                © {currentYear} {companyName}. All rights reserved.
              </p>
              <Chip size="sm" variant="flat" color="default">
                v{version}
              </Chip>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/privacy"
                size="sm"
                color="foreground"
                className="hover:text-primary"
              >
                Privacy
              </Link>
              <Link
                href="/terms"
                size="sm"
                color="foreground"
                className="hover:text-primary"
              >
                Terms
              </Link>
              <Link
                href="/contact"
                size="sm"
                color="foreground"
                className="hover:text-primary"
              >
                Contact
              </Link>
            </div>
          </div>
        </div>
      </footer>
    );
  }

  return (
    <footer className="bg-background border-t border-divider">
      <div className="max-w-7xl mx-auto px-6">
        {/* Extended Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 py-12">
          {/* Company Info */}
          <div className="lg:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <span className="font-bold text-foreground">{companyName}</span>
            </div>
            <p className="text-sm text-default-600 mb-6">
              AI-powered chatbot platform for modern businesses.
              Streamline your customer interactions with intelligent automation.
            </p>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-default-600">
                <Mail className="h-4 w-4 text-primary" />
                <span>support@vikkichatbot.com</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-default-600">
                <Phone className="h-4 w-4 text-primary" />
                <span>+1 (555) 123-4567</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-default-600">
                <MapPin className="h-4 w-4 text-primary" />
                <span>San Francisco, CA</span>
              </div>
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h3 className="font-semibold text-foreground mb-4">Product</h3>
            <ul className="space-y-3">
              {footerLinks.product.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    size="sm"
                    color="foreground"
                    className="hover:text-primary flex items-center gap-1"
                    isExternal={link.external}
                  >
                    <span>{link.label}</span>
                    {link.external && <ExternalLink className="h-3 w-3" />}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="font-semibold text-foreground mb-4">Company</h3>
            <ul className="space-y-3">
              {footerLinks.company.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    size="sm"
                    color="foreground"
                    className="hover:text-primary"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Support Links */}
          <div>
            <h3 className="font-semibold text-foreground mb-4">Support</h3>
            <ul className="space-y-3">
              {footerLinks.support.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    size="sm"
                    color="foreground"
                    className="hover:text-primary flex items-center gap-1"
                    isExternal={link.external}
                  >
                    <span>{link.label}</span>
                    {link.external && <ExternalLink className="h-3 w-3" />}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h3 className="font-semibold text-foreground mb-4">Legal</h3>
            <ul className="space-y-3">
              {footerLinks.legal.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    size="sm"
                    color="foreground"
                    className="hover:text-primary"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <Divider />

        {/* Bottom Bar */}
        <div className="py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-default-600">
              © {currentYear} {companyName}. All rights reserved.
            </p>
            <div className="flex items-center gap-4">
              <Chip size="sm" variant="flat" color="default">
                Version {version}
              </Chip>
              <div className="flex items-center gap-1 text-xs text-default-500">
                <span>Made with</span>
                <Heart className="h-3 w-3 text-danger" />
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

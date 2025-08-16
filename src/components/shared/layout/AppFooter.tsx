import React from 'react';
import { Heart, ExternalLink, Mail, Phone, MapPin } from 'lucide-react';
import '@/styles/components/julius-ai-styles.css';

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
      <footer className="julius-footer">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <p className="text-sm">
              © {currentYear} {companyName}. All rights reserved.
            </p>
            <span className="text-xs text-gray-400">v{version}</span>
          </div>
          <div className="flex items-center space-x-4">
            <a
              href="/privacy"
              className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
              Privacy
            </a>
            <a
              href="/terms"
              className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
              Terms
            </a>
            <a
              href="/contact"
              className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
            >
              Contact
            </a>
          </div>
        </div>
      </footer>
    );
  }

  return (
    <footer className="julius-footer julius-footer-extended">
      <div className="max-w-7xl mx-auto">
        {/* Extended Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 py-8">
          {/* Company Info */}
          <div className="lg:col-span-1">
            <div className="flex items-center space-x-2 mb-4">
              <div className="julius-logo">
                <Heart className="h-4 w-4" />
              </div>
              <span className="font-bold text-gray-900">{companyName}</span>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              AI-powered chatbot platform for modern businesses. 
              Streamline your customer interactions with intelligent automation.
            </p>
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Mail className="h-4 w-4" />
                <span>support@vikkichatbot.com</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Phone className="h-4 w-4" />
                <span>+1 (555) 123-4567</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <MapPin className="h-4 w-4" />
                <span>San Francisco, CA</span>
              </div>
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Product</h3>
            <ul className="space-y-2">
              {footerLinks.product.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-sm text-gray-600 hover:text-gray-900 transition-colors flex items-center space-x-1"
                    target={link.external ? '_blank' : undefined}
                    rel={link.external ? 'noopener noreferrer' : undefined}
                  >
                    <span>{link.label}</span>
                    {link.external && <ExternalLink className="h-3 w-3" />}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Company</h3>
            <ul className="space-y-2">
              {footerLinks.company.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Support Links */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Support</h3>
            <ul className="space-y-2">
              {footerLinks.support.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-sm text-gray-600 hover:text-gray-900 transition-colors flex items-center space-x-1"
                    target={link.external ? '_blank' : undefined}
                    rel={link.external ? 'noopener noreferrer' : undefined}
                  >
                    <span>{link.label}</span>
                    {link.external && <ExternalLink className="h-3 w-3" />}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Legal</h3>
            <ul className="space-y-2">
              {footerLinks.legal.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    className="text-sm text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-200 pt-6 pb-4">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <p className="text-sm text-gray-600">
              © {currentYear} {companyName}. All rights reserved.
            </p>
            <div className="flex items-center space-x-4 mt-4 md:mt-0">
              <span className="text-xs text-gray-400">Version {version}</span>
              <div className="flex items-center space-x-1 text-xs text-gray-500">
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

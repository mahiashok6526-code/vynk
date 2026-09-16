import React from 'react';
import { Link } from 'react-router-dom';

import vynkLogoColor from '../../assets/vynk_logo_color.png';
import vynkLogoWhite from '../../assets/vynk_logo_white.png';
import vynkSymbol from '../../assets/vynk_symbol.png';
import vynkAppIcon from '../../assets/vynk_app_icon.png';

/**
 * Official Vynk Brand Logo Component.
 *
 * Sourced directly from the official Vynk branding asset.
 * Preserves original geometry, proportions, and aspect ratios without distortion.
 *
 * @param {'full' | 'symbol' | 'app-icon'} variant - Logo layout variant.
 * @param {'sm' | 'md' | 'lg' | 'xl' | number} size - Predefined or explicit pixel height.
 * @param {boolean} monochrome - Use white monochrome lockup if true.
 * @param {boolean} withLink - Wrap logo in Link to home ('/').
 * @param {string} className - Optional CSS classes.
 * @param {object} style - Optional inline styles.
 */
export function VynkLogo({
  variant = 'full',
  size = 'md',
  monochrome = false,
  withLink = false,
  className = '',
  style = {},
  alt = 'Vynk — Ideas Meet Opportunities',
  ...props
}) {
  // Preset height map
  const heightMap = {
    sm: 28,
    md: 38,
    lg: 52,
    xl: 68,
  };

  const height = typeof size === 'number' ? size : heightMap[size] || 38;

  let src = vynkLogoColor;
  let aspectRatio = 366 / 93; // Original lockup aspect ratio

  if (variant === 'symbol') {
    src = vynkSymbol;
    aspectRatio = 173 / 167; // Original symbol aspect ratio (~1.036)
  } else if (variant === 'app-icon') {
    src = vynkAppIcon;
    aspectRatio = 1;
  } else if (monochrome) {
    src = vynkLogoWhite;
    aspectRatio = 366 / 93;
  }

  const width = Math.round(height * aspectRatio);

  const imageElement = (
    <img
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={`vynk-logo ${className}`}
      style={{
        display: 'inline-block',
        height: `${height}px`,
        width: 'auto',
        maxWidth: '100%',
        aspectRatio: `${aspectRatio}`,
        objectFit: 'contain',
        verticalAlign: 'middle',
        userSelect: 'none',
        ...style,
      }}
      loading="eager"
      decoding="async"
      {...props}
    />
  );

  if (withLink) {
    return (
      <Link
        to="/"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          textDecoration: 'none',
          lineHeight: 1,
        }}
        aria-label="Vynk Home"
      >
        {imageElement}
      </Link>
    );
  }

  return imageElement;
}

export default VynkLogo;

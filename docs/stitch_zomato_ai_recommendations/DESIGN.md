---
name: Luminous Intelligence
colors:
  surface: '#0f131d'
  surface-dim: '#0f131d'
  surface-bright: '#353944'
  surface-container-lowest: '#0a0e18'
  surface-container-low: '#171b26'
  surface-container: '#1c1f2a'
  surface-container-high: '#262a35'
  surface-container-highest: '#313540'
  on-surface: '#dfe2f1'
  on-surface-variant: '#c7c4d7'
  inverse-surface: '#dfe2f1'
  inverse-on-surface: '#2c303b'
  outline: '#908fa0'
  outline-variant: '#464554'
  surface-tint: '#c0c1ff'
  primary: '#c0c1ff'
  on-primary: '#1000a9'
  primary-container: '#8083ff'
  on-primary-container: '#0d0096'
  inverse-primary: '#494bd6'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#ca8100'
  on-tertiary-container: '#3e2400'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e1e0ff'
  primary-fixed-dim: '#c0c1ff'
  on-primary-fixed: '#07006c'
  on-primary-fixed-variant: '#2f2ebe'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#0f131d'
  on-background: '#dfe2f1'
  surface-variant: '#313540'
typography:
  display-xl:
    fontFamily: Outfit
    fontSize: 64px
    fontWeight: '700'
    lineHeight: 72px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: 0.05em
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: 0.02em
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
    letterSpacing: '0'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: '0'
  label-bold-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.1em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: '0'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-padding: 24px
  gutter: 20px
  grid-columns: '12'
  max-width: 1440px
---

## Brand & Style
The design system is engineered for a high-fidelity, premium AI recommendation engine. It targets food enthusiasts and power users who value precision, speed, and a futuristic aesthetic. The brand personality is "The Sophisticated Concierge"—intelligent, discreet, and visually captivating.

The design style leverages **Glassmorphism** and **Cyber-Minimalism**. It creates a sense of infinite depth through the use of translucent layers, vibrant background blurs, and localized neon glows. The interface should feel like a high-end command center, prioritizing clarity through high-contrast typography and subtle motion feedback.

## Colors
The palette is rooted in **Obsidian Slate**, providing a deep, ink-like canvas that allows accent colors to pop with neon intensity.

- **Primary (Neon Indigo):** Used for primary actions, focus states, and the "AI energy" signature glow.
- **Secondary (Emerald Mint):** Reserved for success states, fresh recommendations, and price indicators.
- **Tertiary (Warm Amber):** Used for "Must Try" highlights and urgent status updates.
- **Containers:** Surfaces utilize a semi-transparent charcoal with a heavy 12px backdrop blur to create a glass-like occlusion effect.

## Typography
This design system pairs **Outfit** for headlines to provide a modern, geometric flair with **Inter** for body text to ensure maximum legibility within complex data sets. 

Key headers utilize wide tracking (letter spacing) to enhance the "premium" feel. Functional labels and badges use a strict uppercase bold treatment to distinguish metadata from content. On smaller screens, headline sizes should scale down by 20% while maintaining the uppercase tracking ratios.

## Layout & Spacing
The layout follows a **Fixed-Fluid Hybrid** model. The main content is contained within a 1440px max-width 12-column grid, centered on the desktop viewport. 

- **Desktop:** 24px margins, 20px gutters.
- **Rhythm:** All margins and paddings must be multiples of 8px to maintain a strict mathematical harmony.
- **Glass Padding:** Component containers should use generous internal padding (min 24px) to ensure the backdrop blur effects have sufficient "breathing room" behind the content.

## Elevation & Depth
Depth is not communicated via traditional drop shadows, but through **Luminous Layers** and **Backdrop Blurs**.

- **Z-Index 1 (Base):** Obsidian Slate background with subtle, large-scale indigo radial gradients in the corners.
- **Z-Index 2 (Cards):** 70% opacity charcoal with 12px blur and a 1px inner border of semi-transparent slate.
- **Z-Index 3 (Modals/Popovers):** Higher opacity (85%) and an additional "Ambient Glow"—a soft indigo drop-shadow (30px blur, 10% opacity) that suggests the element is physically emitting light.
- **Interactive State:** Elements scale by 1.02x on hover to break the flat plane of the screen.

## Shapes
The shape language is consistently **Rounded**. A standard radius of 0.5rem (8px) is used for small components like inputs and buttons, while large glass cards use 1rem (16px). This creates a friendly yet structured appearance. Callout cards are unique; they feature a 4px solid left-border (Indigo or Emerald) that respects the container's corner radius.

## Components
- **Glass Cards:** Must include the 1px semi-transparent border. For "AI-suggested" items, use a 4px solid Indigo left-border.
- **Buttons:** Primary buttons feature a subtle linear gradient (Indigo to Violet) with a focus state that adds an outer indigo glow.
- **Segmented Controls:** These should appear as a single glass track. The active segment is indicated by a glowing border and a slightly lighter background tint.
- **Numeric Sliders:** The track is a gradient from Emerald to Indigo. The handle is a solid white circle with a 10px Indigo glow.
- **Input Fields:** On focus, the 1px border transitions from Slate to Indigo, accompanied by a soft inner glow.
- **Badges:** Small, uppercase bold text inside a low-opacity Indigo pill container with a high-contrast Indigo border.
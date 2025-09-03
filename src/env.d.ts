/// <reference path="../.astro/types.d.ts" />

declare namespace App {
  interface Locals {
    auth?: import('@/types').AuthContext;
  }
}

declare global {
  interface Window {
    toggleTheme: () => void;
  }

  interface WindowEventMap {
    'theme-change': CustomEvent<{ theme: string }>;
  }
}
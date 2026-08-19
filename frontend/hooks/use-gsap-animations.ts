"use client";

import { useEffect, useRef, RefObject } from "react";
import gsap from "gsap";

/**
 * Hook to animate staggered entrance of child elements using GSAP with smooth spring easing.
 */
export function useGsapStagger<T extends HTMLElement = HTMLDivElement>(
  selector: string = ".gsap-card",
  deps: any[] = []
): RefObject<T | null> {
  const ref = useRef<T>(null);

  useEffect(() => {
    if (!ref.current) return;

    const elements = ref.current.querySelectorAll(selector);
    if (elements.length === 0) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        elements,
        {
          opacity: 0,
          y: 24,
          scale: 0.96,
          filter: "blur(4px)",
        },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          filter: "blur(0px)",
          duration: 0.6,
          stagger: 0.06,
          ease: "cubic-bezier(0.16, 1, 0.3, 1)",
        }
      );
    }, ref);

    return () => ctx.revert();
  }, deps);

  return ref;
}

/**
 * Hook to animate single zoom-in and fade with a fluid spring curve.
 */
export function useGsapZoomIn<T extends HTMLElement = HTMLDivElement>(
  delay: number = 0,
  deps: any[] = []
): RefObject<T | null> {
  const ref = useRef<T>(null);

  useEffect(() => {
    if (!ref.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ref.current,
        {
          opacity: 0,
          scale: 0.92,
          y: 16,
          filter: "blur(6px)",
        },
        {
          opacity: 1,
          scale: 1,
          y: 0,
          filter: "blur(0px)",
          duration: 0.7,
          delay,
          ease: "cubic-bezier(0.16, 1, 0.3, 1)",
        }
      );
    }, ref);

    return () => ctx.revert();
  }, deps);

  return ref;
}

/**
 * Hook for intersection-based smooth scroll reveal animation with scale and fade.
 */
export function useGsapScrollReveal<T extends HTMLElement = HTMLDivElement>(
  threshold: number = 0.15
): RefObject<T | null> {
  const ref = useRef<T>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    // Initial state
    gsap.set(el, { opacity: 0, y: 30, scale: 0.95, filter: "blur(4px)" });

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            gsap.to(el, {
              opacity: 1,
              y: 0,
              scale: 1,
              filter: "blur(0px)",
              duration: 0.75,
              ease: "cubic-bezier(0.16, 1, 0.3, 1)",
            });
            observer.unobserve(el);
          }
        });
      },
      { threshold }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return ref;
}

/**
 * Hook to animate single fade & slide in element.
 */
export function useGsapFadeIn<T extends HTMLElement = HTMLDivElement>(
  delay: number = 0,
  deps: any[] = []
): RefObject<T | null> {
  const ref = useRef<T>(null);

  useEffect(() => {
    if (!ref.current) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ref.current,
        {
          opacity: 0,
          y: 15,
        },
        {
          opacity: 1,
          y: 0,
          duration: 0.6,
          delay,
          ease: "cubic-bezier(0.16, 1, 0.3, 1)",
        }
      );
    }, ref);

    return () => ctx.revert();
  }, deps);

  return ref;
}

/**
 * Hook to trigger a subtle pulse or glow highlight on state change.
 */
export function useGsapPulse<T extends HTMLElement = HTMLDivElement>(
  trigger: any
): RefObject<T | null> {
  const ref = useRef<T>(null);

  useEffect(() => {
    if (!ref.current || !trigger) return;

    const ctx = gsap.context(() => {
      gsap.fromTo(
        ref.current,
        { scale: 1 },
        {
          scale: 1.03,
          duration: 0.2,
          yoyo: true,
          repeat: 1,
          ease: "power2.inOut",
        }
      );
    }, ref);

    return () => ctx.revert();
  }, [trigger]);

  return ref;
}

/**
 * Hook to add subtle 3D tilt interaction on mouse move.
 */
export function useCardTilt<T extends HTMLElement = HTMLDivElement>(): RefObject<T | null> {
  const ref = useRef<T>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      const rotateX = (-y / rect.height) * 8;
      const rotateY = (x / rect.width) * 8;

      gsap.to(el, {
        rotateX,
        rotateY,
        transformPerspective: 1000,
        ease: "power1.out",
        duration: 0.3,
      });
    };

    const handleMouseLeave = () => {
      gsap.to(el, {
        rotateX: 0,
        rotateY: 0,
        ease: "power2.out",
        duration: 0.5,
      });
    };

    el.addEventListener("mousemove", handleMouseMove);
    el.addEventListener("mouseleave", handleMouseLeave);

    return () => {
      el.removeEventListener("mousemove", handleMouseMove);
      el.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, []);

  return ref;
}

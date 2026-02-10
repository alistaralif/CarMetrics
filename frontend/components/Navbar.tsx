"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export default function Navbar() {
  const pathname = usePathname();
  const isHome = pathname === "/";
  const [showBrand, setShowBrand] = useState(false);

  useEffect(() => {
    const checkWidth = () => {
      setShowBrand(window.innerWidth >= 570);
    };
    
    checkWidth();
    window.addEventListener("resize", checkWidth);
    return () => window.removeEventListener("resize", checkWidth);
  }, []);

  return (
    <nav className="navbar">
      {/* Animated Brand Text */}
      {showBrand && (
        <motion.div
          className="brand-text"
          initial={false}
          animate={{
            x: isHome ? "calc(40vw - 20px)" : 0,
            opacity: isHome ? 0 : 1,
          }}
          transition={{
            x: {
              type: "spring",
              stiffness: isHome? 100: 90,
              damping: 20,
              mass: 1,
            },
            opacity: { 
              duration: 0.4,
              ease: "easeInOut",
              delay: isHome ? 0.15 : 0,
            },
          }}
        >
          CarMetrics
        </motion.div>
      )}

      <div className="navbar-links">
        <Link href="/">Home</Link>
        <Link href="/quick-start">Quick Start</Link>
        <Link href="/analysis">Analysis</Link>
      </div>
    </nav>
  );
}

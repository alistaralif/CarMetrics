"use client";

import { AnimatePresence, motion } from "framer-motion";
import { usePathname } from "next/navigation";
import { useRef } from "react";
import { getRouteIndex } from "@/lib/routeOrder";

const OFFSET = 500;
const DURATION = 0.3;

export default function RouteTransition({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const prevPathRef = useRef<string>(pathname);
  const directionRef = useRef<number>(1);

  if (prevPathRef.current !== pathname) {
    const prevIndex = getRouteIndex(prevPathRef.current);
    const currentIndex = getRouteIndex(pathname);
    directionRef.current = currentIndex > prevIndex ? 1 : -1;
    prevPathRef.current = pathname;
  }

  return (
    <AnimatePresence mode="popLayout" initial={false}>
      <motion.div
        key={pathname}
        initial={{ opacity: 0, x: OFFSET * directionRef.current }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: DURATION, ease: "easeInOut" }}
        style={{ minHeight: "100vh" }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
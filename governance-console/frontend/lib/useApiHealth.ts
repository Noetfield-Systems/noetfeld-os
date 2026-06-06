"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ApiHealth, fetchApiHealth } from "@/lib/health";

const POLL_MS_VISIBLE = 60_000;
const POLL_MS_HIDDEN = 300_000;

function pollIntervalMs(): number {
  if (typeof document === "undefined") return POLL_MS_VISIBLE;
  return document.visibilityState === "hidden" ? POLL_MS_HIDDEN : POLL_MS_VISIBLE;
}

export function useApiHealth(): ApiHealth | null {
  const [health, setHealth] = useState<ApiHealth | null>(null);
  const inFlight = useRef(false);

  const refresh = useCallback(async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    try {
      setHealth(await fetchApiHealth());
    } finally {
      inFlight.current = false;
    }
  }, []);

  useEffect(() => {
    void refresh();
    let id = setInterval(() => void refresh(), pollIntervalMs());

    const onVisibility = () => {
      if (document.visibilityState === "visible") {
        void refresh();
      }
      clearInterval(id);
      id = setInterval(() => void refresh(), pollIntervalMs());
    };
    document.addEventListener("visibilitychange", onVisibility);

    return () => {
      clearInterval(id);
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [refresh]);

  return health;
}

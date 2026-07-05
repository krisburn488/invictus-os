import { useEffect, useState } from "react";

import { fetchAgents } from "../services/agents";
import type { AgentSummary, LoadState } from "../types/system";

export function useAgents() {
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [state, setState] = useState<LoadState>("loading");

  useEffect(() => {
    let active = true;

    fetchAgents()
      .then((result) => {
        if (active) {
          setAgents(result);
          setState("ready");
        }
      })
      .catch(() => {
        if (active) {
          setState("error");
        }
      });

    return () => {
      active = false;
    };
  }, []);

  return { agents, state };
}

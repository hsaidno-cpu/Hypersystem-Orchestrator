"use client";

import { useState } from "react";

export default function PromptCopy({text}:{text:string}) {
  const [state,setState]=useState("Copy prompt");
  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
      setState("Copied");
    } catch {
      setState("Clipboard unavailable");
    }
  }
  return <button className="button copy-button" onClick={copy}>{state}</button>;
}

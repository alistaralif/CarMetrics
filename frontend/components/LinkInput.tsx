"use client";

import { useState } from "react";

export default function LinkInput({
  links,
  setLinks,
}: {
  links: string[];
  setLinks: (v: string[]) => void;
}) {
  const [value, setValue] = useState("");

  function addLinks(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey && value.trim()) {
      e.preventDefault();
      
      // Split on newlines, whitespace, or before "https"
      const newLinks = value
        .split(/[\n\s]+|(?=https:\/\/)/)
        .map((link) => link.trim())
        .filter((link) => link && link.startsWith("http"));
      
      if (newLinks.length > 0) {
        // Filter out duplicates
        const uniqueNewLinks = newLinks.filter((link) => !links.includes(link));
        setLinks([...links, ...uniqueNewLinks]);
      }
      setValue("");
    }
  }

  function removeLink(idx: number) {
    setLinks(links.filter((_, i) => i !== idx));
  }

  return (
    <div className="link-input-wrapper">
      <h2>Listings</h2>
      <textarea
        className="link-input"
        placeholder="Paste links and press Enter (supports multiple links)"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={addLinks}
        rows={3}
      />

      <div className="link-chips">
        {links.map((link, idx) => (
          <div key={idx} className="chip">
            <span>{link}</span>
            <button onClick={() => removeLink(idx)}>×</button>
          </div>
        ))}
      </div>
      <p className="link-disclaimer">To avoid source blocking, CarMetrics processes listings gradually. 
        Large batches may take several minutes.</p>
    </div>
  );
}
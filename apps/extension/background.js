chrome.contextMenus.create({
  title: "Check Truth with TrustLens",
  contexts: ["link"],
  onclick: async (info) => {
    const url = info.linkUrl;
    const res = await fetch("https://api.trustlens.ai/v1/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });
    const data = await res.json();
    alert(`TrustLens Score: ${data.score}/100\n${data.evidence.map(e => `${e.title}: ${e.summary}`).join('\n')}`);
  }
});
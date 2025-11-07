chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'score') {
    fetch('http://127.0.0.1:8001/v1/score/url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: msg.url, html: msg.html || '' })
    })
    .then(r => r.json())
    .then(data => sendResponse({ data }))
    .catch(err => sendResponse({ error: 'API down: ' + err.message }))
    return true;
  }
});
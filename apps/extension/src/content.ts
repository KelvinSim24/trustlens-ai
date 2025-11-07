setTimeout(() => {
  const waitForImages = setInterval(() => {
    const imgs = document.querySelectorAll('img[src*="bbcimg"], img[data-src*="bbcimg"]');
    if (imgs.length >= 2) {
      clearInterval(waitForImages);
      sendScore();
    }
  }, 500);

  setTimeout(() => clearInterval(waitForImages), 8000); // Max 8s

  function sendScore() {
    chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
      if (!tab.id || !tab.url?.startsWith('http')) return;
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => document.documentElement.outerHTML
      }, ([{ result }]) => {
        chrome.runtime.sendMessage({
          action: 'score',
          url: tab.url!,
          html: result
        });
      });
    });
  }
}, 1500);
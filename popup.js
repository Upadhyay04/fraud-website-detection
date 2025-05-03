document.getElementById("checkButton").addEventListener("click", () => {
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    const currentUrl = tabs[0].url;

    fetch("http://localhost:5000/check", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ url: currentUrl })
    })
      .then((response) => response.json())
      .then((data) => {
        const resultEl = document.getElementById("result");
        if (data.fraudulent) {
          resultEl.textContent = "Warning: Fraudulent Website!";
          resultEl.style.color = "red";
        } else {
          resultEl.textContent = "This site is safe.";
          resultEl.style.color = "green";
        }
      })
      .catch((error) => {
        document.getElementById("result").textContent = "Error: Backend not reachable";
      });
  });
});

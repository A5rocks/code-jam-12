// boot.js
// call window.startBootSequence() to begin, window.finishBoot() when pyodide is ready

const bootMessages = [
  {
    text: "BIOS Version 2.1.87 - Copyright (C) 1987 Iridescent Ivies",
    delay: 500,
  },
  { text: "Memory Test: 640K OK", delay: 800 },
  { text: "Extended Memory Test: 15360K OK", delay: 600 },
  { text: "", delay: 200 },
  { text: "Detecting Hardware...", delay: 400 },
  { text: "  - Primary Hard Disk.......... OK", delay: 300 },
  { text: "  - Network Interface.......... OK", delay: 300 },
  { text: "  - Math Coprocessor........... OK", delay: 400 },
  { text: "", delay: 200 },
  { text: "Loading SQL Social Network v1.0...", delay: 600 },
  { text: "Initializing Python Runtime Environment...", delay: 800 },
  { text: "Loading Pyodide Kernel", delay: 1000, showProgress: true },
  { text: "Installing pandas...", delay: 2000 },
  { text: "Installing sqlalchemy...", delay: 1500 },
  { text: "Configuring data structures...", delay: 800 },
  { text: "Establishing database connections...", delay: 600 },
  { text: "Loading sample datasets...", delay: 400 },
  { text: "", delay: 200 },
  { text: "System Ready!", delay: 300, blink: true },
  { text: "Press any key to continue...", delay: 500, blink: true },
];

let bootScreen = null;
let isBootComplete = false;

window.startBootSequence = async function () {
  // create boot screen overlay
  bootScreen = document.createElement("div");
  bootScreen.className = "boot-screen";
  bootScreen.innerHTML = '<div class="boot-content" id="boot-content"></div>';

  // add to body
  document.body.appendChild(bootScreen);

  // hide main interface
  document.querySelector(".interface").style.opacity = "0";

  // start boot sequence
  await showBootMessages();

  // wait for user interaction or auto-continue
  await waitForContinue();

  isBootComplete = true;
};

// hide boot screen and show main interface
window.finishBoot = function () {
  if (bootScreen) {
    bootScreen.style.opacity = "0";
    bootScreen.style.transition = "opacity 0.5s ease";

    setTimeout(() => {
      if (bootScreen && bootScreen.parentNode) {
        document.body.removeChild(bootScreen);
      }
      bootScreen = null;
    }, 500);
  }

  // show main interface
  const mainInterface = document.querySelector(".interface");
  mainInterface.style.transition = "opacity 0.5s ease";
  mainInterface.style.opacity = "1";

  console.log("🚀 boot sequence complete - system ready");
};

window.isBootComplete = function () {
  return isBootComplete;
};

// show boot messages
async function showBootMessages() {
  const bootContent = document.getElementById("boot-content");

  for (let i = 0; i < bootMessages.length; i++) {
    const message = bootMessages[i];
    const line = document.createElement("div");
    line.className = "boot-line";

    if (message.showProgress) {
      line.innerHTML =
        message.text +
        '<div class="boot-progress"><div class="boot-progress-bar" id="progress-bar-' +
        i +
        '"></div></div>';
    } else {
      line.textContent = message.text;
    }

    if (message.blink) {
      line.classList.add("boot-blink");
    }

    bootContent.appendChild(line);

    // show the line with fade effect
    setTimeout(() => {
      line.classList.add("boot-show");
    }, 50);

    // handle progress bar animation
    if (message.showProgress) {
      await animateProgressBar("progress-bar-" + i);
    }

    await new Promise((resolve) => setTimeout(resolve, message.delay));
  }
}

function animateProgressBar(barId) {
  return new Promise((resolve) => {
    const progressBar = document.getElementById(barId);
    if (!progressBar) {
      resolve();
      return;
    }

    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 15;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        resolve();
      }
      progressBar.style.width = progress + "%";
    }, 100);
  });
}

function waitForContinue() {
  return new Promise((resolve) => {
    const handleInteraction = () => {
      document.removeEventListener("keydown", handleInteraction);
      document.removeEventListener("click", handleInteraction);
      resolve();
    };

    document.addEventListener("keydown", handleInteraction);
    document.addEventListener("click", handleInteraction);

    // auto-continue after 3 seconds
    setTimeout(() => {
      document.removeEventListener("keydown", handleInteraction);
      document.removeEventListener("click", handleInteraction);
      resolve();
    }, 3000);
  });
}

// styles for boot screen (inject into document head)
const bootStyles = `
.boot-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #000;
  color: #00ff00;
  font-family: "JetBrains Mono", "Courier New", monospace;
  z-index: 10000;
  padding: 20px;
  font-size: 14px;
  line-height: 1.4;
  overflow-y: auto;
}

.boot-content {
  max-width: 800px;
  margin: 0 auto;
}

.boot-line {
  opacity: 0;
  margin-bottom: 2px;
  transition: opacity 0.3s ease;
}

.boot-line.boot-show {
  opacity: 1;
}

.boot-line.boot-blink {
  animation: bootBlink 0.5s infinite;
}

.boot-progress {
  display: inline-block;
  width: 200px;
  height: 8px;
  border: 1px solid #00ff00;
  margin-left: 10px;
  position: relative;
  vertical-align: middle;
}

.boot-progress-bar {
  height: 100%;
  background: #00ff00;
  width: 0%;
  transition: width 0.5s ease;
}

@keyframes bootBlink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
`;

const styleSheet = document.createElement("style");
styleSheet.textContent = bootStyles;
document.head.appendChild(styleSheet);

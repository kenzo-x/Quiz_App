(function () {
  const camera = document.getElementById("camera");
  const cameraStatus = document.getElementById("camera-status");
  const gamepadToggle = document.getElementById("gamepad-toggle");
  const gamepadStatus = document.getElementById("gamepad-status");
  let stream;
  let gamepadEnabled = false;

  async function startCamera() {
    if (!navigator.mediaDevices?.getUserMedia) {
      cameraStatus.textContent = "カメラがサポートされていません";
      return;
    }
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      camera.srcObject = stream;
      cameraStatus.textContent = "カメラ準備完了";
    } catch (err) {
      console.error(err);
      cameraStatus.textContent = "カメラの初期化に失敗しました（権限を確認してください）";
    }
  }

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach((t) => t.stop());
    }
  }

  function updateGamepadStatus() {
    gamepadStatus.textContent = `Gamepad: ${gamepadEnabled ? "ON" : "OFF"}`;
  }

  function enableGamepad() {
    if (!window.GamepadManager) {
      gamepadStatus.textContent = "Gamepad API が利用できません";
      return;
    }
    if (gamepadEnabled) return;
    gamepadEnabled = true;
    updateGamepadStatus();
    window.GamepadManager.start(({ playerId, choiceIndex }) => {
      if (gamepadEnabled) {
        window.quizApp?.submitAnswer(choiceIndex);
      }
    });
  }

  function disableGamepad() {
    if (!gamepadEnabled) return;
    gamepadEnabled = false;
    updateGamepadStatus();
    window.GamepadManager?.stop();
  }

  function bind() {
    gamepadToggle?.addEventListener("change", () => {
      if (gamepadToggle.checked) {
        enableGamepad();
      } else {
        disableGamepad();
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    startCamera();
    bind();
    updateGamepadStatus();
  });

  window.addEventListener("beforeunload", stopCamera);
})();

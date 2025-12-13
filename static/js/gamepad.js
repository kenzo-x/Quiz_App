(function () {
  const BUTTON_TO_CHOICE = {
    1: 1, // ○
    0: 2, // ×（標準マッピングで cross は 0）
    2: 3, // △
    3: 4, // □
  };

  let rafId = null;
  let enabled = false;
  const previous = new Map();

  function poll(onPress) {
    const gamepads = navigator.getGamepads ? navigator.getGamepads() : [];
    for (let i = 0; i < gamepads.length; i++) {
      const gp = gamepads[i];
      if (!gp) continue;
      const playerId = `p${gp.index}`;
      const prevButtons = previous.get(gp.index) || [];
      gp.buttons.forEach((btn, idx) => {
        const wasPressed = prevButtons[idx]?.pressed;
        if (btn.pressed && !wasPressed && BUTTON_TO_CHOICE[idx]) {
          onPress({ playerId, choiceIndex: BUTTON_TO_CHOICE[idx] });
        }
      });
      previous.set(gp.index, gp.buttons.map((b) => ({ pressed: b.pressed })));
    }
    if (enabled) {
      rafId = requestAnimationFrame(() => poll(onPress));
    }
  }

  function start(onPress) {
    if (enabled) return;
    if (!navigator.getGamepads) {
      console.warn("Gamepad API is not supported");
      return;
    }
    enabled = true;
    poll(onPress);
  }

  function stop() {
    enabled = false;
    if (rafId) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
    previous.clear();
  }

  window.GamepadManager = { start, stop };
})();

document.addEventListener(
  "play",
  (event) => {
    const currentPlayer = event.target;

    if (
      !(currentPlayer instanceof HTMLAudioElement) ||
      !currentPlayer.closest(".audio-notes-grid")
    ) {
      return;
    }

    document.querySelectorAll(".audio-notes-grid audio").forEach((player) => {
      if (player !== currentPlayer) {
        player.pause();
      }
    });
  },
  true,
);

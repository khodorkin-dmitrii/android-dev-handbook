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
const audioNotesPlayers = [
  ...document.querySelectorAll(".audio-notes-grid audio"),
];

audioNotesPlayers.forEach((player, index) => {
  player.addEventListener("ended", () => {
    const nextPlayer = audioNotesPlayers[index + 1];

    if (!nextPlayer) {
      return;
    }

    nextPlayer.currentTime = 0;
    nextPlayer.play().catch(() => {
      // A browser may block automatic continuation because of its media policy.
    });
  });
});
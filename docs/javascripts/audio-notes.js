const audioNotesSelector = ".audio-notes-grid audio";

const isAudioNotesPlayer = (target) =>
  target instanceof HTMLAudioElement && target.matches(audioNotesSelector);

const setActivePlayer = (currentPlayer) => {
  document.querySelectorAll(audioNotesSelector).forEach((player) => {
    player.classList.toggle("is-playing", player === currentPlayer);
  });
};

document.addEventListener(
  "play",
  (event) => {
    const currentPlayer = event.target;

    if (!isAudioNotesPlayer(currentPlayer)) {
      return;
    }

    document.querySelectorAll(audioNotesSelector).forEach((player) => {
      if (player !== currentPlayer) {
        player.pause();
      }
    });

    setActivePlayer(currentPlayer);
  },
  true,
);

["pause", "ended"].forEach((eventName) => {
  document.addEventListener(
    eventName,
    (event) => {
      if (isAudioNotesPlayer(event.target)) {
        event.target.classList.remove("is-playing");
      }
    },
    true,
  );
});

const audioNotesPlayers = [...document.querySelectorAll(audioNotesSelector)];

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

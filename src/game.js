import {
  GRID_SIZE,
  createInitialState,
  keyForPos,
  setDirection,
  step,
  togglePause,
} from "./snake.js";

const TICK_MS = 140;

const boardEl = document.querySelector("#board");
const scoreEl = document.querySelector("#score");
const statusEl = document.querySelector("#status");
const restartEl = document.querySelector("#restart");
const pauseEl = document.querySelector("#pause");
const mobileControlButtons = Array.from(
  document.querySelectorAll(".mobile-controls [data-dir]")
);

let state = createInitialState();

boardEl.style.setProperty("--size", String(GRID_SIZE));
for (let i = 0; i < GRID_SIZE * GRID_SIZE; i += 1) {
  const cell = document.createElement("div");
  cell.className = "cell";
  boardEl.appendChild(cell);
}
const cellElements = Array.from(boardEl.children);

function render() {
  for (const cell of cellElements) {
    cell.className = "cell";
  }

  for (const segment of state.snake) {
    const idx = segment.y * GRID_SIZE + segment.x;
    if (cellElements[idx]) {
      cellElements[idx].classList.add("snake");
    }
  }

  if (state.food.x >= 0 && state.food.y >= 0) {
    const foodIdx = state.food.y * GRID_SIZE + state.food.x;
    if (cellElements[foodIdx]) {
      cellElements[foodIdx].classList.add("food");
    }
  }

  scoreEl.textContent = String(state.score);
  if (state.gameOver) {
    statusEl.textContent = "Game over";
  } else if (state.paused) {
    statusEl.textContent = "Paused";
  } else {
    statusEl.textContent = "Running";
  }
  pauseEl.textContent = state.paused ? "Resume" : "Pause";
}

function restartGame() {
  state = createInitialState();
  render();
}

const keyToDirection = {
  ArrowUp: "up",
  ArrowDown: "down",
  ArrowLeft: "left",
  ArrowRight: "right",
  w: "up",
  W: "up",
  s: "down",
  S: "down",
  a: "left",
  A: "left",
  d: "right",
  D: "right",
};

document.addEventListener("keydown", (event) => {
  if (event.key === " ") {
    event.preventDefault();
    state = togglePause(state);
    render();
    return;
  }
  const dir = keyToDirection[event.key];
  if (!dir) {
    return;
  }
  event.preventDefault();
  state = setDirection(state, dir);
});

restartEl.addEventListener("click", restartGame);
pauseEl.addEventListener("click", () => {
  state = togglePause(state);
  render();
});

mobileControlButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const dir = button.dataset.dir;
    state = setDirection(state, dir);
  });
});

function loop() {
  state = step(state);
  render();
}

setInterval(loop, TICK_MS);
render();

window.__SNAKE_DEBUG__ = {
  getState: () => ({
    ...state,
    snake: state.snake.map((segment) => ({ ...segment })),
    food: { ...state.food },
    snakeKeys: state.snake.map(keyForPos),
  }),
  restart: restartGame,
};

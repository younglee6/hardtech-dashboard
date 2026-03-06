export const GRID_SIZE = 20;
export const INITIAL_DIRECTION = "right";

const DIRECTION_VECTORS = {
  up: { x: 0, y: -1 },
  down: { x: 0, y: 1 },
  left: { x: -1, y: 0 },
  right: { x: 1, y: 0 },
};

const OPPOSITE_DIRECTIONS = {
  up: "down",
  down: "up",
  left: "right",
  right: "left",
};

export function keyForPos(pos) {
  return `${pos.x},${pos.y}`;
}

export function createInitialState(randInt = defaultRandInt) {
  const middle = Math.floor(GRID_SIZE / 2);
  const snake = [
    { x: middle, y: middle },
    { x: middle - 1, y: middle },
    { x: middle - 2, y: middle },
  ];
  return {
    snake,
    direction: INITIAL_DIRECTION,
    nextDirection: INITIAL_DIRECTION,
    food: placeFood(snake, GRID_SIZE, randInt),
    score: 0,
    gameOver: false,
    paused: false,
  };
}

export function setDirection(state, direction) {
  if (!DIRECTION_VECTORS[direction]) {
    return state;
  }
  if (direction === OPPOSITE_DIRECTIONS[state.direction]) {
    return state;
  }
  return {
    ...state,
    nextDirection: direction,
  };
}

export function togglePause(state) {
  if (state.gameOver) {
    return state;
  }
  return {
    ...state,
    paused: !state.paused,
  };
}

export function step(state, randInt = defaultRandInt) {
  if (state.gameOver || state.paused) {
    return state;
  }

  const direction = state.nextDirection;
  const movement = DIRECTION_VECTORS[direction];
  const nextHead = {
    x: state.snake[0].x + movement.x,
    y: state.snake[0].y + movement.y,
  };

  if (isWallCollision(nextHead, GRID_SIZE)) {
    return { ...state, direction, gameOver: true };
  }

  const hitsFood = nextHead.x === state.food.x && nextHead.y === state.food.y;
  const currentBody = hitsFood ? state.snake : state.snake.slice(0, -1);
  if (isSelfCollision(nextHead, currentBody)) {
    return { ...state, direction, gameOver: true };
  }

  let snake = [nextHead, ...state.snake];
  let score = state.score;
  let food = state.food;

  if (hitsFood) {
    score += 1;
    food = placeFood(snake, GRID_SIZE, randInt);
  } else {
    snake = snake.slice(0, -1);
  }

  return {
    ...state,
    snake,
    direction,
    food,
    score,
  };
}

export function placeFood(snake, gridSize, randInt = defaultRandInt) {
  const occupied = new Set(snake.map(keyForPos));
  const freeCells = [];
  for (let y = 0; y < gridSize; y += 1) {
    for (let x = 0; x < gridSize; x += 1) {
      const cell = { x, y };
      if (!occupied.has(keyForPos(cell))) {
        freeCells.push(cell);
      }
    }
  }
  if (freeCells.length === 0) {
    return { x: -1, y: -1 };
  }
  return freeCells[randInt(freeCells.length)];
}

export function isWallCollision(pos, gridSize) {
  return pos.x < 0 || pos.y < 0 || pos.x >= gridSize || pos.y >= gridSize;
}

export function isSelfCollision(head, body) {
  return body.some((segment) => segment.x === head.x && segment.y === head.y);
}

function defaultRandInt(max) {
  return Math.floor(Math.random() * max);
}

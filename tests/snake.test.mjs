import test from "node:test";
import assert from "node:assert/strict";
import {
  GRID_SIZE,
  createInitialState,
  placeFood,
  setDirection,
  step,
} from "../src/snake.js";

test("moves one cell in current direction", () => {
  const state = createInitialState(() => 0);
  const next = step(state, () => 0);
  assert.equal(next.snake[0].x, state.snake[0].x + 1);
  assert.equal(next.snake[0].y, state.snake[0].y);
  assert.equal(next.snake.length, state.snake.length);
});

test("eating food grows snake and increments score", () => {
  const start = {
    snake: [
      { x: 5, y: 5 },
      { x: 4, y: 5 },
      { x: 3, y: 5 },
    ],
    direction: "right",
    nextDirection: "right",
    food: { x: 6, y: 5 },
    score: 0,
    gameOver: false,
    paused: false,
  };
  const next = step(start, () => 0);
  assert.equal(next.score, 1);
  assert.equal(next.snake.length, 4);
  assert.deepEqual(next.snake[0], { x: 6, y: 5 });
});

test("wall collision ends game", () => {
  const start = {
    snake: [{ x: GRID_SIZE - 1, y: 0 }],
    direction: "right",
    nextDirection: "right",
    food: { x: 0, y: 0 },
    score: 0,
    gameOver: false,
    paused: false,
  };
  const next = step(start, () => 0);
  assert.equal(next.gameOver, true);
});

test("self collision ends game", () => {
  const start = {
    snake: [
      { x: 3, y: 2 },
      { x: 2, y: 2 },
      { x: 2, y: 3 },
      { x: 3, y: 3 },
    ],
    direction: "up",
    nextDirection: "left",
    food: { x: 0, y: 0 },
    score: 0,
    gameOver: false,
    paused: false,
  };
  const next = step(start, () => 0);
  assert.equal(next.gameOver, true);
});

test("cannot reverse direction instantly", () => {
  const state = {
    ...createInitialState(() => 0),
    direction: "right",
    nextDirection: "right",
  };
  const next = setDirection(state, "left");
  assert.equal(next.nextDirection, "right");
});

test("food placement avoids snake cells", () => {
  const snake = [
    { x: 0, y: 0 },
    { x: 1, y: 0 },
    { x: 2, y: 0 },
  ];
  const food = placeFood(snake, 4, () => 0);
  assert.notDeepEqual(food, { x: 0, y: 0 });
  assert.notDeepEqual(food, { x: 1, y: 0 });
  assert.notDeepEqual(food, { x: 2, y: 0 });
  assert.deepEqual(food, { x: 3, y: 0 });
});

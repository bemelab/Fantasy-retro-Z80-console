# How Snake works

Snake is a loop that repeats many times per second. Each pass:

1. **Read input.** Store the new direction, ignoring a 180 degree turn.
2. **Move.** The snake is a list of grid cells with the head first. Add a new head one step ahead and remove the tail cell, so the length stays the same.
3. **Food.** If the new head lands on the food, keep the tail (the snake grows), add to the score and place new food on a random empty cell.
4. **Collisions.** The game ends if the head hits a wall or any body cell.
5. **Draw and wait.** Redraw, then pause briefly. A shorter pause means a faster snake.

```
loop:
    read key -> update direction
    new_head = head + direction
    if new_head outside grid or in snake: game over
    insert new_head at front of snake
    if new_head == food:
        score += 1
        place new food
    else:
        remove last cell of snake
    draw everything
    wait
```

# How Boulder Dash works

The game is a grid where every cell holds one thing: dirt, wall, boulder, diamond, empty space, the player or an enemy. The whole grid is updated in small steps (ticks), scanning from the top-left to the bottom-right.

- **Gravity.** A boulder or diamond with an empty cell below falls. If it rests on a rounded surface (another boulder, a diamond or a brick wall) and the cell beside it and the one diagonally below are empty, it rolls off (left first, then right).
- **Falling state.** An object must be marked as falling to be dangerous. A falling boulder that lands on the player or an enemy kills it or makes it explode.
- **Player.** Moving into dirt digs it, moving into a diamond collects it, moving sideways into a boulder pushes it if the cell beyond is empty.
- **Enemies.** Fireflies and butterflies follow a wall: the firefly keeps a wall on its left, the butterfly on its right. They turn when blocked, so no pathfinding is needed.
- **Explosions.** A firefly or butterfly hit by a boulder explodes into a 3x3 area (butterflies leave diamonds).
- **Amoeba.** A slow-growing tile that spreads at random into empty or dirt cells and can be trapped.
- **Win and lose.** Collect the required diamonds, then the exit opens. The player dies if crushed, caught in an explosion, touched by an enemy or out of time.

Because cells are processed in scan order, an object could be moved twice in one tick, so implementations remember which cells were already updated.

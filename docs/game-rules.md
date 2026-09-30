# Orbital Courier rules

You pilot a ship between Earth, Luna, Mars, Europa, and Titan. Complete delivery contracts to earn points.

1. Inspect an open contract. It tells you the cargo, quantity, source, destination, and reward.
2. Travel to its source station.
3. Load the required cargo.
4. Travel to its destination.
5. Deliver the contract. The game consumes the cargo and awards ten points.

Your ship holds **six units total**. Supplies are unlimited. Any station is directly reachable from any other station. Travel costs nothing. Each player has independent state, so nobody can take your cargo or contracts.

| Station | Supplies |
|---|---|
| Earth | food, water |
| Luna | tools |
| Mars | medicine |
| Europa | fuel |
| Titan | parts |

There are twelve contracts per round. Each can score once, giving a maximum personal score of 120. Unloading discards cargo without awarding points and works at every station. Invalid actions do not change game state.

In practice you may reset your own position, cargo, completed contracts, and points. Your identity stays registered. After practice, reset and registration close. A fresh round uses new contract IDs and quantities. Always inspect the current contract instead of memorizing an example.

During timed play, the instructor can pause or end the round. Read-only commands continue to work while gameplay actions are disabled. Reaching the time limit freezes scores. No autonomous game-playing loops or direct API calls during timed play; use your CLI for each gameplay action.


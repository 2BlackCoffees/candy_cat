# Wall Breaker

To run this game please make sure you have python3 and pip3 installed.

Then:

* `python3 -m pip install -U pygame --user`
* Clone this repository.
* Switch to the branch students for students exercises.
* The program can be started as follows: `python3 wall_breaker`
* Exercises to fill are described in the respository students.
* Once all exercises are finished, bonus exercises are the following:

    1. We need to define a timer. A timer is related to one game, once the timer elapsed the player lost (as if he had lost all his balls).
    2. Create a new type of brick: when this brick is bumped by a ball, then the user gets an additional ball (the number of balls is incresed by 1)
    3. Create again a new type of brick, this time when a ball bumps against it, a new ball should be given to the user that is able to move independantly of the first ball. Each time the new brick is bumped a new ball is created. The new ball should be placed on the player's racket.
    4. There are (at least) 2 bugs that were left on purpose: 

        * Bug 1: The ball does not start at the right position when a game is won and the next one starts.
        * Bug 2: The ball sometimes bumps against an horizontal or vertical wall but goes in its opposite direction (as if it was a corner instead of horizontal or vertical wall). This is a more complex one.
    5. Improvements:
        * Destroyable bricks have all a specific count of bumps before they get destroyed. The remaining number of bumbs should be displayed on the top right of each detroyable brick.
        * Each tme a brick is destroyed an anmiation should be played (each brick should have its specific animation).
        * The racket should be able to shoot rockets and destroy the skull bricks. Rockets should destroy unbreakable walls but when a dollar brick is touched then many points should be reduced.


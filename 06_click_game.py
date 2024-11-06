import pyxel

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 256
GROWTH_SPEED = 0.5
FRAGMENTS = 128
BUBBLE_INTERVAL = 20
MAX_BUBBLES = 20
GAME_DURATION = 30 * 30  # 60秒（30フレーム/秒）

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class GameObject:
    def __init__(self, x, y):
        self.pos = Vec2(x, y)
        self.life = 45

    def update(self):
        self.life -= 1

class Fragment(GameObject):
    def __init__(self, x, y, color):
        super().__init__(x, y)
        self.vel = Vec2(pyxel.rndf(-1.5, 1.5), pyxel.rndf(-1.5, 1.5))
        self.color = color

    def update(self):
        super().update()
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

class Score(GameObject):
    def __init__(self, x, y, value):
        super().__init__(x, y)
        self.value = value

class Bubble:
    def __init__(self):
        self.target_r = pyxel.rndf(15, 25)
        self.r = 1
        self.start_pos = Vec2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
        self.target_pos = Vec2(
            pyxel.rndf(self.target_r, SCREEN_WIDTH - self.target_r),
            pyxel.rndf(self.target_r, SCREEN_HEIGHT - self.target_r)
        )
        self.pos = Vec2(self.start_pos.x, self.start_pos.y)
        self.color = pyxel.rndi(1, 15)
        self.is_popped = False
        self.is_grown = False

    def update(self):
        if not self.is_popped and not self.is_grown:
            self.pos.x += (self.target_pos.x - self.start_pos.x) * 0.01
            self.pos.y += (self.target_pos.y - self.start_pos.y) * 0.01
            if self.r < self.target_r:
                self.r += GROWTH_SPEED
            if self.r >= self.target_r:
                self.r = self.target_r
                self.is_grown = True

class FlashingBubble(Bubble):
    def __init__(self):
        super().__init__()
        self.flash_timer = 0

    def update(self):
        super().update()
        self.flash_timer += 1
        self.color = 8 if self.flash_timer % 15 < 7 else 7

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Bubble Pop Game")
        pyxel.mouse(True)
        self.high_score = 0
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.bubbles = [Bubble()]
        self.fragments = []
        self.scores = []
        self.score = 0
        self.bubble_timer = 0
        self.flashing_bubble_timer = 0
        self.game_over = False
        self.timer = GAME_DURATION
        self.final_score = 0

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.game_over:
            self.high_score = max(self.high_score, self.score)
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.reset_game()
            return

        self.timer -= 1
        if self.timer <= 0:
            self.game_over = True
            self.final_score = self.score
            return

        self.update_bubbles()
        self.handle_click()
        self.update_fragments()
        self.update_scores()

        if len(self.bubbles) > MAX_BUBBLES:
            self.game_over = True
            self.final_score = self.score

    def update_bubbles(self):
        self.bubble_timer += 1
        if self.bubble_timer >= BUBBLE_INTERVAL:
            self.bubbles.append(Bubble())
            self.bubble_timer = 0

        self.flashing_bubble_timer += 1
        if self.flashing_bubble_timer >= 600:
            self.bubbles.append(FlashingBubble())
            self.flashing_bubble_timer = 0

        for bubble in self.bubbles:
            if not bubble.is_popped:
                bubble.update()

    def handle_click(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for bubble in self.bubbles:
                if not bubble.is_popped:
                    dx = bubble.pos.x - pyxel.mouse_x
                    dy = bubble.pos.y - pyxel.mouse_y
                    if dx * dx + dy * dy < bubble.r * bubble.r:
                        self.pop_bubble(bubble)
                        break

    def pop_bubble(self, bubble):
        if isinstance(bubble, FlashingBubble):
            self.pop_all_bubbles()
        else:
            score_value = self.calculate_score()
            self.score += score_value
            self.scores.append(Score(bubble.pos.x, bubble.pos.y, score_value))
            bubble.is_popped = True
            self.create_fragments(bubble)

        self.bubbles = [b for b in self.bubbles if not b.is_popped]

    def pop_all_bubbles(self):
        total_score = 0
        for bubble in self.bubbles:
            bubble.is_popped = True
            score_value = self.calculate_score()
            total_score += score_value
            self.create_fragments(bubble)
        self.score += total_score
        self.scores.append(Score(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, total_score))

    def calculate_score(self):
        return max(10, min(100, int((1 - len(self.bubbles) / MAX_BUBBLES) * 100)))

    def create_fragments(self, bubble):
        for _ in range(FRAGMENTS):
            self.fragments.append(Fragment(bubble.pos.x, bubble.pos.y, bubble.color))

    def update_fragments(self):
        self.fragments = [f for f in self.fragments if f.life > 0]
        for fragment in self.fragments:
            fragment.update()

    def update_scores(self):
        self.scores = [s for s in self.scores if s.life > 0]
        for score in self.scores:
            score.update()

    def draw(self):
        pyxel.cls(0)

        if self.game_over:
            self.draw_game_over()
        else:
            self.draw_bubbles()
            self.draw_fragments()
            self.draw_scores()
            self.draw_ui()

    def draw_game_over(self):
        pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 - 30, "GAME OVER", pyxel.COLOR_RED)
        pyxel.text(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 10, f"Final Score: {self.final_score}", pyxel.COLOR_YELLOW)
        pyxel.text(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 10, f"High Score: {self.high_score}", pyxel.COLOR_GREEN)
        pyxel.text(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 30, "Click to Restart", pyxel.COLOR_WHITE)

    def draw_bubbles(self):
        for bubble in self.bubbles:
            if not bubble.is_popped:
                pyxel.circ(bubble.pos.x, bubble.pos.y, bubble.r, bubble.color)

    def draw_fragments(self):
        for fragment in self.fragments:
            pyxel.circ(fragment.pos.x, fragment.pos.y, 1, fragment.color)

    def draw_scores(self):
        for score in self.scores:
            pyxel.text(score.pos.x, score.pos.y, str(score.value), pyxel.COLOR_YELLOW)

    def draw_ui(self):
        pyxel.text(5, 5, f"Score: {self.score}", 7)
        pyxel.text(5, 15, f"High Score: {self.high_score}", 10)
        pyxel.text(SCREEN_WIDTH // 2 - 20, 5, f"Time: {self.timer // 30}", 7)
        self.draw_bar_graph_background()
        self.draw_bar_graph()

    def draw_bar_graph_background(self):
        pyxel.rect(10, SCREEN_HEIGHT - MAX_BUBBLES * 10, 20, SCREEN_HEIGHT, 5)

    def draw_bar_graph(self):
        pyxel.rect(10, SCREEN_HEIGHT - len(self.bubbles) * 10, 20, SCREEN_HEIGHT, 8)

App()
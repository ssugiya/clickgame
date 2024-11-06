import pyxel

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 256
GROWTH_SPEED = 0.5  # バブルの成長速度
FRAGMENTS = 128  # 破裂時に飛び散る破片の数
BUBBLE_INTERVAL = 10  # 新しいバブルを生成する間隔（フレーム数）
MAX_BUBBLES = 20  # ゲームオーバーになるバブルの最大数

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Fragment:
    def __init__(self, x, y, color):
        self.pos = Vec2(x, y)
        self.vel = Vec2(pyxel.rndf(-1.5, 1.5), pyxel.rndf(-1.5, 1.5))
        self.color = color
        self.life = 55  # 破片の寿命フレーム数

    def update(self):
        # 破片の位置更新
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y
        self.life -= 1

class Bubble:
    def __init__(self):
        self.target_r = pyxel.rndf(15, 25)  # 最終的なバブルのサイズ
        self.r = 1  # 初期サイズは小さく
        # 開始位置は固定
        self.start_pos = Vec2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
        # 画面内のランダムな目標位置（端も含む）を設定
        self.target_pos = Vec2(
            pyxel.rndf(self.target_r, SCREEN_WIDTH - self.target_r),
            pyxel.rndf(self.target_r, SCREEN_HEIGHT - self.target_r)
        )
        self.pos = Vec2(self.start_pos.x, self.start_pos.y)
        self.color = pyxel.rndi(1, 15)
        self.is_popped = False  # 破裂状態を管理
        self.is_grown = False   # 成長が完了したかを示すフラグ

    def update(self):
        if not self.is_popped and not self.is_grown:
            # 目標位置に移動しつつ、サイズを拡大
            self.pos.x += (self.target_pos.x - self.start_pos.x) * 0.01
            self.pos.y += (self.target_pos.y - self.start_pos.y) * 0.01
            # 拡大処理
            if self.r < self.target_r:
                self.r += GROWTH_SPEED
                if self.r >= self.target_r:
                    self.r = self.target_r
                    self.is_grown = True  # 最大サイズに達したら移動を停止

class FlashingBubble(Bubble):
    def __init__(self):
        super().__init__()
        self.flash_timer = 0

    def update(self):
        super().update()
        self.flash_timer += 1
        if self.flash_timer % 15 < 7:
            self.color = 8  # 赤色
        else:
            self.color = 7  # 白色

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Bubble Pop Game")
        pyxel.mouse(True)
        self.bubbles = [Bubble()]  # 表示中のバブルリスト
        self.fragments = []  # 破裂時の破片リスト
        self.score = 0
        self.bubble_timer = 0  # 新しいバブルを生成するためのタイマー
        self.flashing_bubble_timer = 0  # 点滅バブルを生成するためのタイマー
        self.game_over = False  # ゲームオーバーフラグ
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.bubbles = [Bubble()]
        self.fragments = []
        self.score = 0
        self.bubble_timer = 0
        self.flashing_bubble_timer = 0
        self.game_over = False

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.game_over:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.reset_game()
            return

        # 新しいバブルを生成するタイミングを管理
        self.bubble_timer += 1
        if self.bubble_timer >= BUBBLE_INTERVAL:
            self.bubbles.append(Bubble())
            self.bubble_timer = 0

        # 点滅バブルを生成するタイミングを管理
        self.flashing_bubble_timer += 1
        if self.flashing_bubble_timer >= 600:  # 300フレームごとに点滅バブルを生成
            self.bubbles.append(FlashingBubble())
            self.flashing_bubble_timer = 0

        # バブルの更新
        for bubble in self.bubbles:
            if not bubble.is_popped:
                bubble.update()

        # クリックでバブルを破裂させる
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for bubble in self.bubbles:
                if not bubble.is_popped:
                    dx = bubble.pos.x - pyxel.mouse_x
                    dy = bubble.pos.y - pyxel.mouse_y
                    if dx * dx + dy * dy < bubble.r * bubble.r:
                        if isinstance(bubble, FlashingBubble):
                            # 点滅バブルに触れた場合、すべてのバブルを破裂させる
                            for b in self.bubbles:
                                b.is_popped = True
                                # 破裂時の破片を生成
                                for _ in range(FRAGMENTS):
                                    fragment = Fragment(b.pos.x, b.pos.y, b.color)
                                    self.fragments.append(fragment)
                        else:
                            self.score += int(bubble.target_r * 10)
                            bubble.is_popped = True
                            # 破裂時の破片を生成
                            for _ in range(FRAGMENTS):
                                fragment = Fragment(bubble.pos.x, bubble.pos.y, bubble.color)
                                self.fragments.append(fragment)

            # 破裂したバブルをリストから削除
            self.bubbles = [bubble for bubble in self.bubbles if not bubble.is_popped]

            # 棒グラフの再描画
            self.draw_bar_graph()

        # 破片の更新（寿命が尽きた破片を削除）
        self.fragments = [f for f in self.fragments if f.life > 0]
        for fragment in self.fragments:
            fragment.update()

        # ゲームオーバーのチェック
        if len(self.bubbles) > MAX_BUBBLES:
            self.game_over = True

    def draw(self):
        pyxel.cls(0)

        if self.game_over:
            pyxel.text(SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2, "GAME OVER", pyxel.COLOR_RED)
            pyxel.text(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 10, "Click to Restart", pyxel.COLOR_WHITE)
            return

        # バブルを描画
        for bubble in self.bubbles:
            if not bubble.is_popped:
                pyxel.circ(bubble.pos.x, bubble.pos.y, bubble.r, bubble.color)

        # 破片を小さな円として描画
        for fragment in self.fragments:
            pyxel.circ(fragment.pos.x, fragment.pos.y, 1, fragment.color)  # 小さな円として描画
        
        # スコア表示
        pyxel.text(5, 5, f"Score: {self.score}", 7)

        # 背景部分を描画
        self.draw_bar_graph_background()

        # バブルの数を棒グラフで表示
        self.draw_bar_graph()

    def draw_bar_graph_background(self):
        pyxel.rect(10, SCREEN_HEIGHT - MAX_BUBBLES * 10, 20, SCREEN_HEIGHT, 5)  # 背景部分を塗る

    def draw_bar_graph(self):
        pyxel.rect(10, SCREEN_HEIGHT - len(self.bubbles) * 10, 20, SCREEN_HEIGHT, 8)

App()
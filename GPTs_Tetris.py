import tkinter as tk
import random
import csv
import os

# ゲームの基本設定
BOARD_WIDTH = 10  # 横幅（ブロック数）
BOARD_HEIGHT = 20  # 縦幅（ブロック数）
BLOCK_SIZE = 30  # 1ブロックのサイズ
SPEED = 500  # ミノの通常の落下速度（ミリ秒）
FAST_SPEED = 50  # 加速時の落下速度

# 色の設定
BACKGROUND_COLOR = "black"
ACTIVE_BLOCK_COLOR = "yellow"
INACTIVE_BLOCK_COLOR = "gray"

# ミノの形状
TETROMINOS = {
    'I': [(0, 1), (1, 1), (2, 1), (3, 1)],
    'O': [(1, 0), (2, 0), (1, 1), (2, 1)],
    'T': [(1, 0), (0, 1), (1, 1), (2, 1)],
    'S': [(1, 0), (2, 0), (0, 1), (1, 1)],
    'Z': [(0, 0), (1, 0), (1, 1), (2, 1)],
    'J': [(0, 0), (0, 1), (1, 1), (2, 1)],
    'L': [(2, 0), (0, 1), (1, 1), (2, 1)],
}

class Tetris:
    def __init__(self, root):
        self.root = root
        self.root.title("Tetris")

        # メインフレームを作成し、左にゲーム画面、右にサイドパネルを配置
        self.main_frame = tk.Frame(root)
        self.main_frame.pack()

        # キャンバスの設定（ゲーム画面）
        self.canvas = tk.Canvas(self.main_frame, width=BOARD_WIDTH * BLOCK_SIZE, height=BOARD_HEIGHT * BLOCK_SIZE, bg=BACKGROUND_COLOR)
        self.canvas.grid(row=0, column=0)

        # サイドパネル（Next, スコア, ランキング）を縦に並べるフレーム
        self.side_panel = tk.Frame(self.main_frame)
        self.side_panel.grid(row=0, column=1, sticky="n")

        # ゲーム状態の初期化
        self.init_game()

        # 操作キーのバインド
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<Down>", self.move_down)
        self.root.bind("<Up>", self.rotate_tetromino)
        self.root.bind("<space>", self.hard_drop)
        self.root.bind("<Return>", self.start_game)  # エンターキーでスタート

        # スコアウィンドウの作成
        self.create_score_window()

        # 次のミノ表示ウィンドウの作成
        self.create_next_window()

        # スコアランキングのウィンドウの作成
        self.create_high_score_window()

    def init_game(self):
        """ゲームの初期化処理"""
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.current_tetromino = None
        self.next_tetromino = random.choice(list(TETROMINOS.values()))  # 次のミノ
        self.current_position = None
        self.current_rotation = 0
        self.is_game_over = False
        self.is_hard_drop_active = False  # ハードドロップのフラグ
        self.speed = SPEED

        # スコア関連
        self.score = 0
        self.high_scores = []  # スコア履歴を保存
        self.load_high_scores()  # CSVからハイスコアを読み込み

    def create_score_window(self):
        """スコア表示用のウィジェットを作成してサイドパネルに追加"""
        score_frame = tk.Frame(self.side_panel)
        score_frame.pack(pady=10)

        tk.Label(score_frame, text="Score", font=("Helvetica", 20)).pack()
        self.score_label = tk.Label(score_frame, text=f"{self.score}", font=("Helvetica", 16))
        self.score_label.pack()

    def create_next_window(self):
        """次のミノを表示するウィジェットを作成してサイドパネルに追加"""
        next_frame = tk.Frame(self.side_panel)
        next_frame.pack(pady=10)

        tk.Label(next_frame, text="Next Tetromino", font=("Helvetica", 20)).pack()
        self.next_canvas = tk.Canvas(next_frame, width=4 * BLOCK_SIZE, height=4 * BLOCK_SIZE, bg=BACKGROUND_COLOR)
        self.next_canvas.pack()
        self.draw_next_tetromino()

    def draw_next_tetromino(self):
        """次に出現するミノを描画"""
        self.next_canvas.delete("all")
        for x, y in self.next_tetromino:
            self.next_canvas.create_rectangle(
                (x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                (x + 2) * BLOCK_SIZE, (y + 2) * BLOCK_SIZE,
                fill=ACTIVE_BLOCK_COLOR
            )

    def create_high_score_window(self):
        """ハイスコア表示用のウィジェットを作成してサイドパネルに追加"""
        high_score_frame = tk.Frame(self.side_panel)
        high_score_frame.pack(pady=10)

        tk.Label(high_score_frame, text="High Scores", font=("Helvetica", 20)).pack()

        self.high_score_labels = []
        for idx in range(3):
            label = tk.Label(high_score_frame, text=f"{idx + 1}. ---", font=("Helvetica", 16))
            label.pack()
            self.high_score_labels.append(label)

        self.update_high_scores()

    def update_high_scores(self):
        """ハイスコアウィンドウの更新"""
        for idx, score in enumerate(self.high_scores):
            self.high_score_labels[idx].config(text=f"{idx + 1}. {score}")

    def update_score(self, points):
        """スコアを更新し、スコアウィンドウに反映"""
        self.score += points
        self.score_label.config(text=f"{self.score}")

    def new_tetromino(self):
        """新しいミノを生成する"""
        self.current_tetromino = self.next_tetromino  # 次のミノを現在のミノに
        self.next_tetromino = random.choice(list(TETROMINOS.values()))  # 次のミノを新たに選択
        self.current_position = [0, BOARD_WIDTH // 2 - 2]
        self.current_rotation = 0
        self.update_score(100)  # ミノ生成時に100ポイント追加
        self.draw_next_tetromino()  # 次のミノを描画

        # ゲームオーバー判定
        if not self.is_valid_position(self.current_tetromino, self.current_position):
            self.game_over()

    def is_valid_position(self, tetromino, position):
        """ミノの配置が有効かどうかを確認"""
        for x, y in tetromino:
            board_x = position[1] + x
            board_y = position[0] + y
            if board_x < 0 or board_x >= BOARD_WIDTH or board_y >= BOARD_HEIGHT:
                return False
            if board_y >= 0 and self.board[board_y][board_x] is not None:
                return False
        return True

    def place_tetromino(self):
        """ミノをフィールドに配置"""
        for x, y in self.current_tetromino:
            board_x = self.current_position[1] + x
            board_y = self.current_position[0] + y
            if board_y >= 0:
                self.board[board_y][board_x] = self.canvas.create_rectangle(
                    board_x * BLOCK_SIZE, board_y * BLOCK_SIZE,
                    (board_x + 1) * BLOCK_SIZE, (board_y + 1) * BLOCK_SIZE,
                    fill=INACTIVE_BLOCK_COLOR
                )

        # ハードドロップ終了後、速度を元に戻す
        self.is_hard_drop_active = False
        self.speed = SPEED

    def move_left(self, event):
        """左に移動"""
        new_position = [self.current_position[0], self.current_position[1] - 1]
        if self.is_valid_position(self.current_tetromino, new_position):
            self.current_position = new_position
        self.draw_tetromino()
        self.draw_prediction()

    def move_right(self, event):
        """右に移動"""
        new_position = [self.current_position[0], self.current_position[1] + 1]
        if self.is_valid_position(self.current_tetromino, new_position):
            self.current_position = new_position
        self.draw_tetromino()
        self.draw_prediction()

    def move_down(self, event=None):
        """下に移動"""
        new_position = [self.current_position[0] + 1, self.current_position[1]]
        if self.is_valid_position(self.current_tetromino, new_position):
            self.current_position = new_position
        else:
            self.place_tetromino()
            self.clear_lines()
            self.new_tetromino()
        self.draw_tetromino()
        self.draw_prediction()

    def rotate_tetromino(self, event):
        """ミノを回転"""
        new_tetromino = [(y, -x) for x, y in self.current_tetromino]
        if self.is_valid_position(new_tetromino, self.current_position):
            self.current_tetromino = new_tetromino
        self.draw_tetromino()
        self.draw_prediction()

    def hard_drop(self, event):
        """スペースキーで加速"""
        self.is_hard_drop_active = True  # フラグを立てる
        self.speed = FAST_SPEED  # 加速
        self.draw_prediction()

    def draw_tetromino(self):
        """ミノを描画"""
        self.canvas.delete("tetromino")
        for x, y in self.current_tetromino:
            board_x = self.current_position[1] + x
            board_y = self.current_position[0] + y
            if board_y >= 0:
                self.canvas.create_rectangle(
                    board_x * BLOCK_SIZE, board_y * BLOCK_SIZE,
                    (board_x + 1) * BLOCK_SIZE, (board_y + 1) * BLOCK_SIZE,
                    fill=ACTIVE_BLOCK_COLOR, tags="tetromino"
                )

    def clear_lines(self):
        """ラインが揃った場合に消去"""
        new_board = [row for row in self.board if any(block is None for block in row)]
        lines_cleared = BOARD_HEIGHT - len(new_board)
        if lines_cleared > 0:
            self.update_score(500 * lines_cleared)  # ライン消去でスコア追加
        new_board = [[None for _ in range(BOARD_WIDTH)] for _ in range(lines_cleared)] + new_board
        self.board = new_board

        self.canvas.delete("all")
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x] is not None:
                    self.canvas.create_rectangle(
                        x * BLOCK_SIZE, y * BLOCK_SIZE,
                        (x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                        fill=INACTIVE_BLOCK_COLOR
                    )
    def draw_prediction(self):
        """落下予想位置を描画"""
        # 現在の位置を基にしてミノがどこに落下するかを計算
        prediction_position = list(self.current_position)
        
        while self.is_valid_position(self.current_tetromino, [prediction_position[0] + 1, prediction_position[1]]):
            prediction_position[0] += 1

        # 予測位置を描画するために現状のキャンバスから "prediction" タグを削除
        self.canvas.delete("prediction")

        # 落下予想位置のミノを描画（予測位置用の色を指定）
        for x, y in self.current_tetromino:
            board_x = prediction_position[1] + x
            board_y = prediction_position[0] + y
            if board_y >= 0:
                self.canvas.create_rectangle(
                    board_x * BLOCK_SIZE, board_y * BLOCK_SIZE,
                    (board_x + 1) * BLOCK_SIZE, (board_y + 1) * BLOCK_SIZE,
                    outline="white",  # 枠線のみで表示
                    tags="prediction"
                )


    def update_game(self):
        """ゲームの進行"""
        if not self.is_game_over:
            self.move_down()
            self.root.after(self.speed, self.update_game)

    def game_over(self):
        """ゲームオーバー処理"""
        self.is_game_over = True
        self.save_score()  # スコアを保存
        self.update_high_scores()  # ハイスコアウィンドウを更新
        self.canvas.create_text(BOARD_WIDTH * BLOCK_SIZE // 2, BOARD_HEIGHT * BLOCK_SIZE // 2,
                                text="Game Over", fill="red", font=("Helvetica", 30))

    def save_score(self):
        """スコアをCSVに保存"""
        file_name = "high_scores.csv"
        if os.path.exists(file_name):
            with open(file_name, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([self.score])
        else:
            with open(file_name, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Score"])
                writer.writerow([self.score])

        self.high_scores.append(self.score)
        self.high_scores = sorted(self.high_scores, reverse=True)[:3]  # 上位3つだけ保持

    def load_high_scores(self):
        """CSVからハイスコアを読み込み"""
        file_name = "high_scores.csv"
        if os.path.exists(file_name):
            with open(file_name, mode='r') as f:
                reader = csv.reader(f)
                next(reader)  # ヘッダーをスキップ
                for row in reader:
                    self.high_scores.append(int(row[0]))

    def start_game(self, event=None):
        """ゲームをスタート"""
        self.canvas.delete("all")
        self.init_game()
        self.new_tetromino()
        self.update_game()

# メイン処理
if __name__ == "__main__":
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()

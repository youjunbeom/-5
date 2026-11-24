import tkinter as tk
from PIL import Image, ImageTk
import random
from pathlib import Path
from PIL import ImageDraw

WIDTH = 1000
HEIGHT = 700

root = tk.Tk()
root.title("냥집사")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.resizable(False, False)

fur_var = tk.StringVar(value="흰색")
eye_var = tk.StringVar(value="파란색")

# ------------------------
# 상태
# ------------------------

happy = 0
sleeping = False
dragging = False

cat_x = 500
cat_y = 380

walk_frame = 0
walk_dir = 1

# ------------------------
# 캔버스
# ------------------------

canvas = tk.Canvas(
    root,
    width=WIDTH,
    height=HEIGHT,
    bg="#FDEAD7",
    highlightthickness=0,
)
canvas.pack()

# ------------------------
# 이미지
# ------------------------

ASSET_DIR = Path(__file__).resolve().parent / "assets"

def make_fallback_cat(state):
    image = Image.new("RGBA", (280, 280), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    body_color = "#CFA56B"
    if state == "happy":
        body_color = "#E6A57A"
    elif state == "sleep":
        body_color = "#B9A4C9"

    draw.ellipse((55, 90, 225, 245), fill=body_color, outline="#765C45", width=4)
    draw.polygon([(75, 105), (95, 35), (125, 100)], fill=body_color, outline="#765C45")
    draw.polygon([(155, 100), (185, 35), (205, 105)], fill=body_color, outline="#765C45")
    draw.ellipse((70, 70, 210, 175), fill=body_color, outline="#765C45", width=4)

    if state == "sleep":
        draw.arc((105, 115, 125, 135), 0, 180, fill="#765C45", width=4)
        draw.arc((155, 115, 175, 135), 0, 180, fill="#765C45", width=4)
    else:
        draw.ellipse((105, 112, 122, 129), fill="#765C45")
        draw.ellipse((158, 112, 175, 129), fill="#765C45")

    if state == "happy":
        draw.arc((120, 135, 160, 155), 0, 180, fill="#765C45", width=4)
    else:
        draw.line((140, 137, 140, 145), fill="#765C45", width=3)
        draw.arc((128, 140, 152, 158), 200, 340, fill="#765C45", width=3)

    if state == "walk1":
        draw.ellipse((82, 215, 112, 250), fill="#765C45")
    elif state == "walk2":
        draw.ellipse((168, 215, 198, 250), fill="#765C45")

    return image

def load_source_img(path, fallback_state):
    try:
        return Image.open(path).convert("RGBA")
    except (FileNotFoundError, OSError):
        return make_fallback_cat(fallback_state).resize((424, 617))

sprite_sources = {
    "idle": load_source_img(ASSET_DIR / "cat_idle.png", "idle"),
    "happy": load_source_img(ASSET_DIR / "cat_happy.png", "happy"),
    "sleep": load_source_img(ASSET_DIR / "cat_sleep.png", "sleep"),
    "walk1": load_source_img(ASSET_DIR / "cat_walk1.png", "walk1"),
    "walk2": load_source_img(ASSET_DIR / "cat_walk2.png", "walk2"),
}
custom_sprites = {}

FUR_COLORS = {
    "흰색": "#F4F1ED",
    "치즈색": "#E8A33D",
    "회색": "#A7A7B2",
    "갈색": "#9A6847",
    "검정색": "#202020",
}
EYE_COLORS = {
    "파란색": "#3B8FE8",
    "초록색": "#39A96B",
    "호박색": "#E7A52B",
    "보라색": "#9B69D3",
}
OUTLINE_COLOR = "#19182A"


def customize_sprite(source, state):
    image = source.copy()
    fur_color = FUR_COLORS[fur_var.get()]
    fur_rgb = tuple(int(fur_color[index:index + 2], 16) for index in (1, 3, 5))
    pixels = image.load()

    for y in range(image.height):
        for x in range(image.width):
            red, green, blue, alpha = pixels[x, y]
            if alpha and max(red, green, blue) - min(red, green, blue) < 20 and min(red, green, blue) > 175:
                brightness = (red + green + blue) / 765
                pixels[x, y] = (
                    int(fur_rgb[0] * brightness),
                    int(fur_rgb[1] * brightness),
                    int(fur_rgb[2] * brightness),
                    alpha,
                )

    draw = ImageDraw.Draw(image)

    if state != "sleep":
        eye_color = EYE_COLORS[eye_var.get()]
        draw.ellipse((145, 125, 159, 141), fill=eye_color, outline=OUTLINE_COLOR, width=2)
        draw.ellipse((184, 125, 198, 141), fill=eye_color, outline=OUTLINE_COLOR, width=2)
        draw.ellipse((150, 128, 154, 137), fill="#FFFFFF")
        draw.ellipse((189, 128, 193, 137), fill="#FFFFFF")

    return ImageTk.PhotoImage(image.resize((280, 280), Image.Resampling.LANCZOS))


def refresh_customization(*_):
    custom_sprites.clear()
    for state, source in sprite_sources.items():
        custom_sprites[state] = customize_sprite(source, state)
    update_cat_state()

# ------------------------
# 배경
# ------------------------

canvas.create_rectangle(
    0, 500,
    WIDTH, HEIGHT,
    fill="#e7c9a9",
    outline=""
)

# ------------------------
# UI
# ------------------------

canvas.create_text(
    500,
    35,
    text="😺 모찌",
    font=("맑은 고딕", 24, "bold")
)

mood_text = canvas.create_text(
    500,
    70,
    text="기분 : 😐",
    font=("맑은 고딕", 16)
)

canvas.create_rectangle(
    300,
    95,
    700,
    120,
    fill="#dddddd",
    outline=""
)

gauge = canvas.create_rectangle(
    300,
    95,
    300,
    120,
    fill="#ff77aa",
    outline=""
)

# ------------------------
# 그림자
# ------------------------

shadow = canvas.create_oval(
    cat_x - 80,
    cat_y + 100,
    cat_x + 80,
    cat_y + 130,
    fill="#bbbbbb",
    outline=""
)

# ------------------------
# 고양이
# ------------------------

cat = canvas.create_image(
    cat_x,
    cat_y,
    image=""
)

# ------------------------
# 고양이 꾸미기
# ------------------------

custom_frame = tk.Frame(root, bg="#FFF8EF", padx=10, pady=4)
custom_options = (
    ("털 색", fur_var, tuple(FUR_COLORS)),
    ("눈 색", eye_var, tuple(EYE_COLORS)),
)

for column, (label, variable, choices) in enumerate(custom_options):
    option_frame = tk.Frame(custom_frame, bg="#FFF8EF")
    option_frame.grid(row=0, column=column, padx=7)
    tk.Label(option_frame, text=label, bg="#FFF8EF", font=("맑은 고딕", 9, "bold")).pack()
    tk.OptionMenu(option_frame, variable, *choices, command=refresh_customization).pack()

canvas.create_window(500, 165, window=custom_frame)

# ------------------------
# UI 업데이트
# ------------------------

def update_ui():
    value = min(happy, 100)

    canvas.coords(
        gauge,
        300,
        95,
        300 + 4 * value,
        120
    )

    if happy < 30:
        mood = "😐"
    elif happy < 70:
        mood = "😺"
    else:
        mood = "😻"

    canvas.itemconfig(
        mood_text,
        text=f"기분 : {mood} 행복도 {happy}"
    )

# ------------------------
# 이미지 상태
# ------------------------

def set_cat_image(img):
    canvas.itemconfig(
        cat,
        image=img
    )

def update_cat_state():

    if sleeping:
        set_cat_image(custom_sprites["sleep"])
        return

    if happy >= 70:
        set_cat_image(custom_sprites["happy"])
    else:
        set_cat_image(custom_sprites["idle"])

# ------------------------
# 하트
# ------------------------

def create_heart(x, y):

    heart = canvas.create_text(
        x,
        y,
        text="❤️",
        font=("Arial", 18)
    )

    def anim():

        canvas.move(
            heart,
            0,
            -3
        )

        pos = canvas.coords(heart)

        if pos[1] > y - 80:
            root.after(
                25,
                anim
            )
        else:
            canvas.delete(heart)

    anim()

# ------------------------
# 쓰다듬기
# ------------------------

def start_pet(event):
    global dragging
    dragging = True
    pet(event)

def stop_pet(event):
    global dragging
    dragging = False

def pet(event):
    global happy

    if not dragging:
        return

    happy += 1
    update_ui()

    if random.random() < 0.25:
        create_heart(
            event.x,
            event.y
        )

    update_cat_state()

# ------------------------
# 랜덤 눈깜빡임
# ------------------------

def blink():

    if sleeping:
        root.after(3000, blink)
        return

    set_cat_image(custom_sprites["idle"])

    root.after(
        150,
        lambda: update_cat_state()
    )

    root.after(
        random.randint(2500, 6000),
        blink
    )

# ------------------------
# 걷기
# ------------------------

def walk():

    global cat_x
    global walk_dir
    global walk_frame

    if sleeping:
        root.after(100, walk)
        return

    move = 2 * walk_dir

    canvas.move(cat, move, 0)
    canvas.move(shadow, move, 0)

    cat_x += move

    if cat_x > 680:
        walk_dir = -1

    if cat_x < 320:
        walk_dir = 1

    if walk_frame == 0:
        canvas.itemconfig(cat, image=custom_sprites["walk1"])
        walk_frame = 1
    else:
        canvas.itemconfig(cat, image=custom_sprites["walk2"])
        walk_frame = 0

    root.after(
        130,
        lambda: (
            update_cat_state(),
            walk()
        )
    )

# ------------------------
# 장난감
# ------------------------

def play_ball():

    global happy

    ball = canvas.create_text(
        150,
        520,
        text="⚽",
        font=("Arial", 40)
    )

    def move_ball(x=150):

        canvas.coords(
            ball,
            x,
            520
        )

        if x < 850:
            root.after(
                15,
                lambda: move_ball(x + 10)
            )
        else:
            canvas.delete(ball)

    move_ball()

    happy += 10
    update_ui()

# ------------------------
# 간식
# ------------------------

def feed_cat():

    global happy

    happy += 15

    msg = canvas.create_text(
        500,
        180,
        text="츄르 냠냠 😋",
        fill="orange",
        font=("맑은 고딕", 18, "bold")
    )

    root.after(
        1500,
        lambda: canvas.delete(msg)
    )

    update_ui()
    update_cat_state()

# ------------------------
# 잠자기
# ------------------------

def sleep_cat():

    global sleeping

    sleeping = True

    canvas.itemconfig(
        cat,
        image=custom_sprites["sleep"]
    )

# ------------------------
# 깨우기
# ------------------------

def wake_cat():

    global sleeping

    sleeping = False

    update_cat_state()

# ------------------------
# 랜덤 행동 AI
# ------------------------

def random_ai():

    if sleeping:
        root.after(5000, random_ai)
        return

    action = random.choice([
        "sit",
        "look",
        "happy"
    ])

    if action == "look":

        msg = canvas.create_text(
            cat_x,
            cat_y - 170,
            text="👀",
            font=("Arial", 20)
        )

        root.after(
            1000,
            lambda: canvas.delete(msg)
        )

    elif action == "happy":

        msg = canvas.create_text(
            cat_x,
            cat_y - 170,
            text="냥~",
            font=("맑은 고딕", 16, "bold")
        )

        root.after(
            1200,
            lambda: canvas.delete(msg)
        )

    root.after(
        random.randint(4000, 8000),
        random_ai
    )

# ------------------------
# 버튼
# ------------------------

tk.Button(
    root,
    text="⚽ 장난감",
    command=play_ball,
    width=12
).place(x=220, y=640)

tk.Button(
    root,
    text="🍖 츄르",
    command=feed_cat,
    width=12
).place(x=400, y=640)

tk.Button(
    root,
    text="💤 잠자기",
    command=sleep_cat,
    width=12
).place(x=580, y=640)

tk.Button(
    root,
    text="☀️ 깨우기",
    command=wake_cat,
    width=12
).place(x=760, y=640)

# ------------------------
# 이벤트
# ------------------------

canvas.tag_bind(
    cat,
    "<ButtonPress-1>",
    start_pet
)

canvas.tag_bind(
    cat,
    "<ButtonRelease-1>",
    stop_pet
)

canvas.tag_bind(
    cat,
    "<B1-Motion>",
    pet
)

# ------------------------
# 시작
# ------------------------

refresh_customization()
update_ui()
update_cat_state()

blink()
walk()
random_ai()

root.mainloop()
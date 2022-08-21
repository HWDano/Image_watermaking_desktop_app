import tkinter as tk
from tkinter import filedialog, PhotoImage, Canvas, Scrollbar
from PIL import Image
import cv2
import cvzone

RESIZED_WATERMARK = "resized.png"
PREVIEW_IMAGE = "preview.png"

took_image, image_name, took_watermark, took_result, watermark_name, image_container, watermark_container, \
    result_container, wa_scroll_x, wa_scroll_y, im_scroll_x, im_scroll_y, re_scroll_x, re_scroll_y = "", "", "", "", \
                                                                                                     "", "", "", "", \
                                                                                                     "", "", "", "", \
                                                                                                     "", ""
image_plot, watermark_plot, result_plot, result = None, None, None, None
size_percentage, limit_percentage, x_spot, y_spot, transparency = 100, 100, 0, 0, 0


def add_image():
    select_picture(image_action)


def add_watermark():
    select_picture(watermark_action)


def select_picture(picture_action):
    global took_image, took_watermark, image_name, watermark_name, image_plot, watermark_plot, \
        image_container, watermark_container, im_scroll_x, im_scroll_y, wa_scroll_x, wa_scroll_y
    file = filedialog.askopenfilenames()[0]
    img_height, img_width = cv2.imread(file).shape[:2]
    if picture_action == image_action:
        took_image = PhotoImage(file=file)
        image_plot, im_scroll_x, im_scroll_y, image_container = apply_scroll_im(image_frame, image_plot, 290, 290,
                                                                                img_width, img_height, im_scroll_x,
                                                                                im_scroll_y, image_container,
                                                                                took_image)
        # if watermark_frame.winfo_height() < image_frame.winfo_height():
        #     watermark_frame.config(height=img_height)
    elif picture_action == watermark_action:
        took_watermark = PhotoImage(file=file)
        watermark_plot, wa_scroll_x, wa_scroll_y, watermark_container = apply_scroll_im(watermark_frame,
                                                                                        watermark_plot, 290, 290,
                                                                                        img_width, img_height,
                                                                                        wa_scroll_x, wa_scroll_y,
                                                                                        watermark_container,
                                                                                        took_watermark)
        # if image_frame.winfo_height() < watermark_frame.winfo_height():
        #     image_frame.config(height=img_height)
    if image_plot and watermark_plot:
        image_name = took_image["file"]
        watermark_name = took_watermark["file"]
        create_result(image_name, watermark_name)
    # picture_action.config(width=(img_width - 90))


def create_result(image, watermark):
    global result_plot, result_container, took_result, re_scroll_x, re_scroll_y, size_percentage, limit_percentage, \
        result
    front = cv2.imread(image)
    back = cv2.imread(watermark, cv2.IMREAD_UNCHANGED)  # , cv2.IMREAD_UNCHANGED
    im_he, im_wi = front.shape[:2]
    wa_he, wa_wi = back.shape[:2]
    if wa_he > im_he or wa_wi > im_wi:
        wa_k = wa_wi / wa_he
        if (wa_he - im_he) > (wa_wi - im_wi):
            resized = cv2.resize(back, (round(im_he * wa_k), im_he))
            size_percentage = im_he * 100 / wa_he
            limit_percentage = size_percentage
        else:
            resized = cv2.resize(back, (im_wi, round(im_wi / wa_k)))
            size_percentage = im_wi * 100 / wa_wi
            limit_percentage = size_percentage
        tool_button_p.config(state=tk.DISABLED)
        tool_button_l.config(state=tk.DISABLED)
        tool_button_u.config(state=tk.DISABLED)
        cv2.imwrite(RESIZED_WATERMARK, resized)
        # back = cv2.imread(RESIZED_WATERMARK, cv2.IMREAD_UNCHANGED)  # , cv2.IMREAD_UNCHANGED
        img = Image.open(RESIZED_WATERMARK)
        # print(f"{item[0]}, {item[1]}, {item[2]}, {item[3]}")

        # wa_he, wa_wi = back.shape[:2]
        # overlay_image = cv2.resize(overlay_image, (wa_wi, wa_he))
    else:
        img = Image.open(watermark)
    rgba = img.convert("RGBA")
    img_rgba = rgba.copy()
    datas = img_rgba.getdata()
    new_data = []
    for item in datas:
        if item[3] != 0:
            new_data.append((item[0], item[1], item[2], round(item[3] * (1 - (transparency * 0.01)))))
        else:
            new_data.append(item)

    img_rgba.putdata(new_data)
    img_rgba.save("transparent.png", "PNG")
    back = cv2.imread("transparent.png", cv2.IMREAD_UNCHANGED)
    tool_label2.config(text=f"{round(size_percentage, 2)}%")
    tool_label5.config(text=f"{transparency}%")

    result = cvzone.overlayPNG(front, back, [x_spot, y_spot])
    cv2.imwrite(PREVIEW_IMAGE, result)
    took_result = PhotoImage(file=PREVIEW_IMAGE)
    result_plot, re_scroll_x, re_scroll_y, result_container = apply_scroll_im(result_frame, result_plot, 800, 600,
                                                                              im_wi, im_he, re_scroll_x, re_scroll_y,
                                                                              result_container, took_result)


def apply_scroll_im(se_frame, se_plot, lim_x, lim_y, width, height, se_scroll_x, se_scroll_y, se_container, took_se):
    if not se_plot:
        se_plot = Canvas(se_frame, width=lim_x, height=lim_y)
        se_container = se_plot.create_image(0, 0, anchor=tk.NW, image=took_se)
    else:
        # se_frame.delete(tk.ALL)
        se_plot.config(width=lim_x, height=lim_y, scrollregion=(0, 0, width, height))
        se_plot.itemconfig(se_container, image=took_se)
    if width > lim_x:
        se_plot.pack_forget()
        if se_scroll_x == "":
            se_scroll_x = Scrollbar(se_frame, orient='horizontal', command=se_plot.xview)
            se_scroll_x.pack(side=tk.BOTTOM, fill=tk.BOTH)
            se_plot.config(xscrollcommand=se_scroll_x.set, scrollregion=(0, 0, width, height))
        else:
            se_scroll_x.pack(side=tk.BOTTOM, fill=tk.BOTH)
    else:
        se_plot.config(width=width)
    if height > lim_y:
        se_plot.pack_forget()
        if se_scroll_y == "":
            se_scroll_y = Scrollbar(se_frame, orient='vertical', command=se_plot.yview)
            se_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
            se_plot.config(yscrollcommand=se_scroll_y.set, scrollregion=(0, 0, width, height))
        else:
            se_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    else:
        if se_scroll_x != "":
            se_scroll_x.pack_forget()
        if se_scroll_y != "":
            se_scroll_y.pack_forget()
        se_plot.config(height=height)
    se_plot.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
    return se_plot, se_scroll_x, se_scroll_y, se_container


def reduce_size():
    # global size_percentage
    if size_percentage - 10 < 0:
        tool_button_m.config(state=tk.DISABLED)
    if tool_button_p['state'] == "disabled":
        tool_button_p.config(state=tk.NORMAL)
    resize_result(size_percentage - 5)


def increase_size():
    # global size_percentage
    if size_percentage + 10 > 100 or size_percentage + 10 > limit_percentage:
        tool_button_p.config(state=tk.DISABLED)
    if tool_button_m['state'] == "disabled":
        tool_button_m.config(state=tk.NORMAL)
    resize_result(size_percentage + 5)


def resize_result(new_percentage):
    global took_image, took_watermark, size_percentage
    na_image = took_image["file"]
    na_watermark = took_watermark["file"]
    back = cv2.imread(na_watermark, cv2.IMREAD_UNCHANGED)
    re_back = cv2.imread(RESIZED_WATERMARK, cv2.IMREAD_UNCHANGED)
    wa_he, wa_wi = back.shape[:2]
    re_wa_he, re_wa_wi = re_back.shape[:2]
    if size_percentage == 100:
        resized = cv2.resize(
            back,
            (round(new_percentage * wa_wi / size_percentage), round(new_percentage * wa_he / size_percentage))
        )
    else:
        resized = cv2.resize(
            back,
            (round(new_percentage * re_wa_wi / size_percentage), round(new_percentage * re_wa_he / size_percentage))
        )
    cv2.imwrite(RESIZED_WATERMARK, resized)
    size_percentage = new_percentage
    create_result(na_image, RESIZED_WATERMARK)


def move_left():
    global x_spot
    im_na = took_image["file"]
    wa_na = took_watermark["file"]
    if x_spot - 20 < 0:
        tool_button_l.config(state=tk.DISABLED)
    if tool_button_r['state'] == "disabled":
        tool_button_r.config(state=tk.NORMAL)
    x_spot -= 10
    if size_percentage == 100:
        create_result(im_na, wa_na)
    else:
        create_result(im_na, RESIZED_WATERMARK)


def move_right():
    global x_spot
    im_na = took_image["file"]
    wa_na = took_watermark["file"]
    im_wi = cv2.imread(im_na).shape[1:2][0]
    if size_percentage == 100:
        wa_wi = cv2.imread(wa_na, cv2.IMREAD_UNCHANGED).shape[1:2][0]
    else:
        wa_wi = cv2.imread(RESIZED_WATERMARK, cv2.IMREAD_UNCHANGED).shape[1:2][0]
    if (x_spot + wa_wi + 20) > im_wi:
        tool_button_r.config(state=tk.DISABLED)
    if tool_button_l['state'] == "disabled":
        tool_button_l.config(state=tk.NORMAL)
    x_spot += 10
    if size_percentage == 100:
        create_result(im_na, wa_na)
    else:
        create_result(im_na, RESIZED_WATERMARK)


def move_up():
    global y_spot
    im_na = took_image["file"]
    wa_na = took_watermark["file"]
    if y_spot - 20 < 0:
        tool_button_u.config(state=tk.DISABLED)
    if tool_button_d['state'] == "disabled":
        tool_button_d.config(state=tk.NORMAL)
    y_spot -= 10
    if size_percentage == 100:
        create_result(im_na, wa_na)
    else:
        create_result(im_na, RESIZED_WATERMARK)


def move_down():
    global y_spot
    im_na = took_image["file"]
    wa_na = took_watermark["file"]
    im_he = cv2.imread(im_na).shape[0:1][0]
    if size_percentage == 100:
        wa_he = cv2.imread(wa_na, cv2.IMREAD_UNCHANGED).shape[0:1][0]
    else:
        wa_he = cv2.imread(RESIZED_WATERMARK, cv2.IMREAD_UNCHANGED).shape[0:1][0]
    if (y_spot + wa_he + 20) > im_he:
        tool_button_d.config(state=tk.DISABLED)
    if tool_button_u['state'] == "disabled":
        tool_button_u.config(state=tk.NORMAL)
    y_spot += 10
    if size_percentage == 100:
        create_result(im_na, wa_na)
    else:
        create_result(im_na, RESIZED_WATERMARK)


def tra_down():
    global transparency
    im_na = took_image["file"]
    wa_na = took_watermark["file"]
    if transparency - 5 == 0:
        tool_button_lt.config(state=tk.DISABLED)
    if tool_button_pt['state'] == "disabled":
        tool_button_pt.config(state=tk.NORMAL)
    transparency -= 5
    if size_percentage == 100:
        create_result(im_na, wa_na)
    else:
        create_result(im_na, RESIZED_WATERMARK)


def tra_up():
    global transparency
    im_na = took_image["file"]
    wa_na = took_watermark["file"]
    if transparency + 5 == 100:
        tool_button_pt.config(state=tk.DISABLED)
    if tool_button_lt['state'] == "disabled":
        tool_button_lt.config(state=tk.NORMAL)
    transparency += 5
    if size_percentage == 100:
        create_result(im_na, wa_na)
    else:
        create_result(im_na, RESIZED_WATERMARK)


def default():
    global size_percentage, x_spot, y_spot, transparency
    im_na = took_image["file"]
    wa_na = took_watermark["file"]
    size_percentage = limit_percentage
    x_spot = 0
    y_spot = 0
    transparency = 0
    if size_percentage == 100:
        create_result(im_na, wa_na)
    else:
        create_result(im_na, RESIZED_WATERMARK)


def save_result():
    file = filedialog.asksaveasfilename(filetypes=[("png image", ".png")], defaultextension=".png")
    cv2.imwrite(file, result)


# TODO 1: Create a window for the app.
window = tk.Tk()
window.title("WaterMaker")
window.minsize(width=600, height=300)
window.config(bg="gray")
pixel = PhotoImage(width=1, height=1)

# TODO 2: Create a way to upload images to the app.
# Image section
image_frame = tk.Frame(width=300, height=300, bg="white")
image_frame.grid(column=0, row=0, columnspan=2)

image_label = tk.Label(
    text="Basic image",
    image=pixel,
    compound="center",
    width=90,
    height=60,
    bg="yellow"
)
image_label.grid(column=0, row=1)

image_action = tk.Button(
    text="Add Image",
    image=pixel,
    compound="center",
    width=210,
    height=60,
    borderwidth=1,
    command=add_image
)
image_action.grid(column=1, row=1)

# TODO 3: Create a system to include a watermark on the app.
# Watermark section
watermark_frame = tk.Frame(width=300, height=300, bg="white")
watermark_frame.grid(column=2, row=0, columnspan=2)

watermark_label = tk.Label(
    text="Watermark",
    image=pixel,
    compound="center",
    width=90,
    height=60,
    bg="yellow"
)
watermark_label.grid(column=2, row=1)

watermark_action = tk.Button(
    text="Add watermark",
    image=pixel,
    compound="center",
    width=210,
    height=60,
    borderwidth=1,
    command=add_watermark
)
watermark_action.grid(column=3, row=1)

# TODO 4: Include tools to modify the image that we add to the app, pasting the watermark.
tools_frame = tk.Frame(width=200, height=300, bg="white")
tools_frame.grid(column=4, row=0, rowspan=1)
tool_label1 = tk.Label(
    master=tools_frame,
    text="SETTINGS\n\nSize percentage:",
    image=pixel,
    compound="center",
    width=200,
    height=70
)
tool_label1.grid(column=0, row=0, columnspan=4)
tool_button_m = tk.Button(
    master=tools_frame,
    text="-",
    image=pixel,
    compound="center",
    width=50,
    height=30,
    borderwidth=0,
    command=reduce_size
)
tool_button_m.grid(column=0, row=1)
tool_label2 = tk.Label(
    master=tools_frame,
    text="- %",
    image=pixel,
    compound="center",
    width=90,
    height=30
)
tool_label2.grid(column=1, row=1, columnspan=2)
tool_button_p = tk.Button(
    master=tools_frame,
    text="+",
    image=pixel,
    compound="center",
    width=50,
    height=30,
    borderwidth=0,
    command=increase_size
)
tool_button_p.grid(column=3, row=1)

tool_label3 = tk.Label(
    master=tools_frame,
    text="Watermark location:",
    image=pixel,
    compound="center",
    width=200,
    height=40
)
tool_label3.grid(row=2, column=0, columnspan=4)
tool_button_l = tk.Button(
    master=tools_frame,
    text="Left",
    image=pixel,
    compound="center",
    width=50,
    height=30,
    borderwidth=0,
    command=move_left
)
tool_button_l.grid(column=0, row=3)
tool_button_u = tk.Button(
    master=tools_frame,
    text="Up",
    image=pixel,
    compound="center",
    width=45,
    height=30,
    borderwidth=0,
    command=move_up
)
tool_button_u.grid(column=1, row=3)
tool_button_d = tk.Button(
    master=tools_frame,
    text="Down",
    image=pixel,
    compound="center",
    width=45,
    height=30,
    borderwidth=0,
    command=move_down
)
tool_button_d.grid(column=2, row=3)
tool_button_r = tk.Button(
    master=tools_frame,
    text="Right",
    image=pixel,
    compound="center",
    width=50,
    height=30,
    borderwidth=0,
    command=move_right
)
tool_button_r.grid(column=3, row=3)

tool_label4 = tk.Label(
    master=tools_frame,
    text="Transparency percentage:",
    image=pixel,
    compound="center",
    width=200,
    height=40
)
tool_label4.grid(row=4, column=0, columnspan=4)
tool_button_lt = tk.Button(
    master=tools_frame,
    text="-",
    image=pixel,
    compound="center",
    width=50,
    height=30,
    borderwidth=0,
    command=tra_down
)
tool_button_lt.grid(column=0, row=5)
tool_label5 = tk.Label(
    master=tools_frame,
    text="- %",
    image=pixel,
    compound="center",
    width=90,
    height=30
)
tool_label5.grid(column=1, row=5, columnspan=2)
tool_button_pt = tk.Button(
    master=tools_frame,
    text="+",
    image=pixel,
    compound="center",
    width=50,
    height=30,
    borderwidth=0,
    command=tra_up
)
tool_button_pt.grid(column=3, row=5)
default_button = tk.Button(
    master=tools_frame,
    text="Default settings",
    image=pixel,
    compound="center",
    width=200,
    height=30,
    borderwidth=0,
    command=default
)
default_button.grid(column=0, row=6, columnspan=4)

create_button = tk.Button(
    master=window,
    text="Create Image",
    image=pixel,
    compound="center",
    width=200,
    height=60,
    borderwidth=0,
    command=save_result
)
create_button.grid(column=4, row=1)

# TODO 5: Create a form to watch and download the final image.
result_frame = tk.Frame(
    master=window,
    bg="white",
    width=800,
    height=600
)
result_frame.grid(column=0, row=8, columnspan=8)

result_label = tk.Label(
    text="Result",
    image=pixel,
    compound="center",
    width=800,
    height=60,
    bg="yellow"
)
result_label.grid(column=0, row=9, columnspan=8)

window.mainloop()

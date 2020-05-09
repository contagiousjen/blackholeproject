import sys
import matplotlib.pyplot as plt
import config as cfg
import numpy as np
import configparser
from PIL import Image

def generate_file():
    print()

def name_output(name):
    global f_out
    f_out = name + '.jpg'

##------------ Вывод сообщений об ошибках и завершение программы ------------##

def show_no_file_message():
    print(cfg.NO_FILE_ERROR_MSG)
    sys.exit(cfg.NO_FILE_ERROR)

def show_incorrect_input_message():
    print(cfg.INVALID_INPUT_MSG)
    sys.exit(cfg.INVALID_INPUT)

def show_camera_pos_message():
    print(cfg.CAMERA_POS_ERROR_MSG)
    sys.exit(cfg.INVALID_INPUT)

##----------------------- Чтение типов из файла .scene ----------------------##

def read_int_array(file, section, key):
    try:
        arr = [int(x) for x in file.get(section, key).split(',')]
    except:
        show_incorrect_input_message()
    return arr

def read_int(file, section, key):
    try:
        int_num = int(file.get(section, key))
    except:
        show_incorrect_input_message()
    return int_num

def read_float_array(file, section, key):
    try:
        arr = [float(x) for x in file.get(section, key).split(',')]
    except:
        show_incorrect_input_message()
    return arr

def read_float(file, section, key):
    try:
        float_num = float(file.get(section, key))
    except:
        show_incorrect_input_message()
    return float_num

def read_string(file, section, key):
    try:
        string = file.get(section, key)
    except:
        show_incorrect_input_message()
    return string

##------------------------------ Проверки ввода -----------------------------##

def check_arr_size(arr, n):
    if (len(arr) != n):
        show_incorrect_input_message()

def check_arr_norm(arr):
    if np.linalg.norm(arr) <= 1.0:
        show_camera_pos_message()

def check_radii(r1, r2):
    if (r1 >= r2):
        show_incorrect_input_message

##-------------------------- Работа с изображением --------------------------##

def open_texture(name):
    name = 'textures/' + name + '.jpg'
    im = Image.open(name)
    im  = np.array(im)
    im  = im.astype(float)
    im /= 255.0
    mask = im > 0.04045
    im[mask] += 0.055
    im[mask] /= 1.055
    im[mask] **= 2.4
    im[~mask] /= 12.92
    return im

##----------------------------- Чтение из файлов ----------------------------##

def open_file(path):
    global resolution
    global iter_number
    global step_size
    global camera_pos
    global look_at
    global up_vector
    global disk_inner_r
    global disk_outer_r
    global field_of_view
    global texarr_disk
    global texarr_sky
    global sky_disk_rat

    cfg_file = configparser.ConfigParser()
    read_f   = cfg_file.read(path)

    if not read_f:
        show_no_file_message()

    resolution = read_int_array(cfg_file, 'Imaging options', 'Resolution')
    check_arr_size(resolution, 2)

    iter_number = read_int(cfg_file, 'Imaging options', 'Iterations')
    step_size   = read_float(cfg_file, 'Imaging options', 'Step_size')

    camera_pos = read_float_array(cfg_file, 'Geometry', 'Camera_position')
    check_arr_size(camera_pos, 3)
    check_arr_norm(camera_pos)

    look_at = read_float_array(cfg_file, 'Geometry', 'Look_at')
    check_arr_size(look_at, 3)

    up_vector = read_float_array(cfg_file, 'Geometry', 'Up_vector')
    check_arr_size(up_vector, 3)

    disk_inner_r  = read_float(cfg_file, 'Geometry', 'Disk_inner_radius')
    disk_outer_r  = read_float(cfg_file, 'Geometry', 'Disk_outer_radius')
    check_radii(disk_inner_r, disk_outer_r)

    field_of_view = read_float(cfg_file, 'Geometry', 'Field_of_view')

    disk_texture = read_string(cfg_file, 'Materials', 'Disk_texture')
    sky_texture = read_string(cfg_file, 'Materials', 'Sky_texture')

    sky_disk_rat = read_float(cfg_file, 'Materials', 'Sky_disk_ratio')

    texarr_disk = open_texture(disk_texture)
    texarr_sky = open_texture(sky_texture)

    camera_pos = np.array(camera_pos)
    look_at    = np.array(look_at)
    up_vector  = np.array(up_vector)

##-------------------------- Сохранение изображения--------------------------##

def save_to_image(arr, name):
    img_output = np.array(arr)
    img_output = np.clip(img_output, 0.0, 1.0)

    # Откорректировать изображение
    mask = img_output > 0.0031308
    img_output[mask] **= 1/2.4
    img_output[mask] *= 1.055
    img_output[mask] -= 0.055
    img_output[~mask] *= 12.92

    img_output = np.reshape(img_output, (resolution[1],\
                                         resolution[0], 3))

    plt.imsave(name, img_output)

import numpy as np
from PIL import Image
import calculations as clc

##--------------------------- Объявление констант ---------------------------##

## Коды ошибок
OK             = 0
INVALID_CALL   = 1
NO_FILE_ERROR  = 2
INVALID_INPUT  = 3

## Сообщения для вывода в консоль
HELP_MSG = \
'Эта программа предназначена для получения изображения черной дыры c    \n' +\
'нулевыми зарядом и моментом вращения.                                  \n' +\
'                                                                       \n' +\
'Доступные опции:                                                       \n' +\
'                                                                       \n' +\
'-help             Вывести это сообщение и завершить программу          \n' +\
'-generate <name>  Сгенерировать шаблон с именем <name>.scene для ввода \n' +\
'                  параметров изображения и завершить программу         \n' 

INPUT_FILE_MSG  = \
'Введите имя файла ввода без расширения (по умолчанию input):           \n'
OUTPUT_FILE_MSG = \
'Введите имя файла вывода без расширения (по умолчанию output):         \n'

CALL_ERROR_MSG = \
'ОШИБКА: Некорректный вызов. Попробуйте вызвать blackhole.py -help для  \n' +\
'        получения информации о доступных опциях вызова.                  '

NO_FILE_ERROR_MSG = \
'ОШИБКА: Файла с указанным именем не существует в директории scenes/.     '

INVALID_INPUT_MSG = \
'ОШИБКА: Некорректные данные в файле .scene.                                      '

CAMERA_POS_ERROR_MSG = \
'ОШИБКА: Наблюдатель не может находиться внутри горизонта событий.      \n' +\
'        Попробуйте изменить значение camera_position в файле .scene      '

## Флаги опций
INPUT_FLAG  = 0
OUTPUT_FLAG = 1

## Имя файлов ввода и вывода по умолчанию
DEFAULT_INPUT_NAME  = 'input'
DEFAULT_OUTPUT_NAME = 'output'

## Параметры обработки
CHUNK_SIZE  = 9000
NUM_THREADS = 4

####--------------------- Предварительная обработка данных --------------------##
##
#### Убедимся, что используем именно массивы numpy
## = np.array(camera_pos)
##look_at    = np.array(look_at)
##up_vec     = np.array(up_vec)
##
#### Загружаем текстуры
##texarr_sky  = Image.open(sky_texture)
##texarr_sky  = np.array(texarr_sky)
##texarr_sky  = texarr_sky.astype(float)
##texarr_sky /= 255.0
##
##texarr_disk  = Image.open(disk_texture)
##texarr_disk  = np.array(texarr_disk)
##texarr_disk  = texarr_disk.astype(float)
##texarr_disk /= 255.0
##
##mask = texarr_disk > 0.04045
##texarr_disk[mask] += 0.055
##texarr_disk[mask] /= 1.055
##texarr_disk[mask] **= 2.4
##texarr_disk[~mask] /= 12.92
##
####------------------ Предварительные математические расчеты -----------------##
##
##disk_inner_sqr = disk_inner_r * disk_inner_r
##disk_outer_sqr = disk_outer_r * disk_outer_r
##
#### Вектор, определяющий направление взгляда наблюдателя
##view_vec = look_at - camera_pos
##view_vec = view_vec / np.linalg.norm(view_vec)
##
#### Вектор, направленный влево от наблюдателя
##left_vec = np.cross(up_vec, view_vec)
##left_vec = left_vec / np.linalg.norm(left_vec)
##
#### Матрица осей
##view_mtx = np.zeros((3, 3))
##
##view_mtx[:, 0] = left_vec
##view_mtx[:, 1] = up_vec
##view_mtx[:, 2] = view_vec
##
##num_pixels = resolution[0] * resolution[1]
##num_chunks = num_pixels // chunk_size + 1

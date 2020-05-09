## Импорт файлов проекта
import config as cfg
import calculations as clc
import tracer
import terminal
import file as f

## Работа с файлами и конфигурациями
import os

## Вычисления
import numpy as np
import random
import multiprocessing as multi
import ctypes

## Работа с изображениями
from PIL import Image

## Вывод в терминал
import logging
logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger(__name__)
import sys
import time


##----------------------- Обработка вызова в терминале ----------------------##

terminal.parse_args()

input_file_name  = terminal.get_file_name(cfg.INPUT_FLAG)
output_file_name = terminal.get_file_name(cfg.OUTPUT_FLAG)

input_file_name  = 'scenes/' + input_file_name + '.scene'
output_file_name = 'renders/' + output_file_name + '.jpg'

##---------------------------- Подготовка данных ----------------------------##

f.open_file(input_file_name)

clc.precalcs()

## Подготовка буфера изображения
colour_buffer = np.zeros((clc.num_pixels, 3))

## Подготовка изображения к параллельной обработке
pixels = np.arange(0, clc.num_pixels, 1)
chunks = np.array_split(pixels, clc.num_chunks)

random.shuffle(chunks)

chunks_per_thread = clc.num_chunks // cfg.NUM_THREADS
leftover_chunks   = clc.num_chunks %  cfg.NUM_THREADS

indices = []
for i in range(cfg.NUM_THREADS + 1):
    indices.append(chunks_per_thread * i + min(i, leftover_chunks))

schedules = []
for i in range(cfg.NUM_THREADS):
    schedules.append(chunks[ indices[i]:indices[i+1] ])

shared_buffer = multi.Array(ctypes.c_float, clc.num_pixels * 3)
colour_buffer = clc.tonumpyarray(shared_buffer)

##--------------------------- Запуск трассировщика --------------------------##


start_time = time.time()

killers = [False for i in range(cfg.NUM_THREADS)]

process_list = []
for i in range(cfg.NUM_THREADS):
    p = multi.Process(target = tracer.raytrace,
                      args = (shared_buffer, schedules[i]))
    process_list.append(p)

for proc in process_list:
    proc.start()

try:
    refreshcounter = 0
    while True:
        refreshcounter+=1
        time.sleep(0.1)

        alldone = True
        for i in range(cfg.NUM_THREADS):
            if process_list[i].is_alive():
                alldone = False
        if alldone:
            break
except KeyboardInterrupt:
    for i in range(cfg.NUM_THREADS):
        killers[i] = True
    sys.exit()

colour_buffer = np.clip(colour_buffer, 0.0, 1.0)

f.save_to_image(colour_buffer, output_file_name)

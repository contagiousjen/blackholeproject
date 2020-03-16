import numpy as np
import matplotlib as plt
from PIL import Image
import matplotlib.pyplot as plt
import file as f
import config as cfg

def precalcs():
    global num_pixels
    global num_chunks
    global disk_inner_sqr
    global disk_outer_sqr
    global view_vec
    global left_vec
    global view_mtx

    ## Количество пикселей в изображении
    num_pixels = f.resolution[0] * f.resolution[1]

    ## Количество частей, на которые будет разбито изображение
    num_chunks = num_pixels // cfg.CHUNK_SIZE + 1

    ## Заранее возведем в квадрат радиусы диска
    disk_inner_sqr = f.disk_inner_r * f.disk_inner_r
    disk_outer_sqr = f.disk_outer_r * f.disk_outer_r

    ## Вектор, определяющий направление взгляда наблюдателя
    view_vector = f.look_at - f.camera_pos
    view_vector = view_vector / np.linalg.norm(view_vector)

    ## Вектор, направленный влево от наблюдателя
    left_vector = np.cross(f.up_vector, view_vector)
    left_vector = left_vector / np.linalg.norm(left_vector)

    ## Матрица осей
    view_mtx = np.zeros((3, 3))

    view_mtx[:, 0] = left_vector
    view_mtx[:, 1] = f.up_vector
    view_mtx[:, 2] = view_vector
    

def vec3a(vec): #returns a constant 3-vector array (don't use for varying vectors)
    return np.outer(ones,vec)

def vec3(x,y,z):
    return vec3a(np.array([x,y,z]))

def norm(vec):
    return np.sqrt(np.einsum('...i,...i',vec,vec))

def normalize(vec):
    return vec / (norm(vec)[:,np.newaxis])

def sqrnorm(vec):
    return np.einsum('...i,...i',vec,vec)

def sixth(v):
    tmp = sqrnorm(v)
    return tmp*tmp*tmp


def RK4f(y,h2):
    f = np.zeros(y.shape)
    f[:,0:3] = y[:,3:6]
    f[:,3:6] = - 1.5 * h2 * y[:,0:3] / np.power(sqrnorm(y[:,0:3]),2.5)[:,np.newaxis]
    return f


# this blends colours ca and cb by placing ca in front of cb
def blendcolors(cb,balpha,ca,aalpha):
    return  ca + cb * (balpha*(1.-aalpha))[:,np.newaxis]


# this is for the final alpha channel after blending
def blendalpha(balpha,aalpha):
    return aalpha + balpha*(1.-aalpha)


# this is not just for bool, also for floats (as grayscale)
def saveToImgBool(arr,fname):
    saveToImg(np.outer(arr,np.array([1.,1.,1.])),fname)


#for shared arrays

def tonumpyarray(mp_arr):
    a = np.frombuffer(mp_arr.get_obj(), dtype=np.float32)
    a.shape = ((num_pixels,3))
    return a

def lookup(texarr,uvarrin): #uvarrin is an array of uv coordinates
    uvarr = np.clip(uvarrin,0.0,0.999)

    uvarr[:,0] *= float(texarr.shape[1])
    uvarr[:,1] *= float(texarr.shape[0])

    uvarr = uvarr.astype(int)

    return texarr[  uvarr[:,1], uvarr[:,0] ]


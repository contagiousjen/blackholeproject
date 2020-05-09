import numpy as np
import config as cfg
import calculations as clc
import file as f
import gc

def raytrace(shared, schedule):
    if len(schedule) == 0:
        return

    colour_buffer = clc.tonumpyarray(shared)

    for chunk in schedule:
        pixels_per_chunk = chunk.shape[0]

        ## Получим массивы координат каждого пикселя в сегменте
        x = chunk % f.resolution[0]
        y = chunk / f.resolution[0]

        ## Инициализируем буферы цвета
        object_colour = np.zeros((pixels_per_chunk, 3))
        object_alpha  = np.zeros((pixels_per_chunk))

        ## Полезные константные массивы
        ones  = np.ones((pixels_per_chunk))
        ones3 = np.ones((pixels_per_chunk, 3))

        upfield = np.outer(ones, np.array([0.,1.,0.]))
        black   = np.outer(ones, np.array([0.,0.,0.]))

        ## Вектор наблюдателя в 3Д пространстве
        view = np.zeros((pixels_per_chunk, 3))

        view[:,0] =  x.astype(float) / f.resolution[0] - .5
        view[:,1] = -y.astype(float) / f.resolution[1] + .5
        view[:,2] = 1.0

        view[:,1] *=  f.resolution[1] / f.resolution[0]

        view[:,0] *= f.field_of_view
        view[:,1] *= f.field_of_view

        view = np.einsum('jk,ik->ij', clc.view_mtx, view)

        ## Первоначальное положение наблюдателя
        point    = np.outer(ones, f.camera_pos)
        normview = clc.normalize(view)
        velocity = np.copy(normview)
        h2       = clc.sqrnorm(np.cross(point, velocity))[:,np.newaxis]
        pointsqr = np.copy(ones3)

        for i in range(f.iter_number):
            old_point = np.copy(point)

            y = np.zeros((pixels_per_chunk, 6))

            y[:,0:3] = point
            y[:,3:6] = velocity

            k1 = clc.RK4f(y, h2)
            k2 = clc.RK4f(y + 0.5 * f.step_size * k1, h2)
            k3 = clc.RK4f(y + 0.5 * f.step_size * k2, h2)
            k4 = clc.RK4f(y +       f.step_size * k3, h2)

            increment = f.step_size / 6. * (k1 + 2 * k2 + 2 * k3 + k4)
            velocity += increment[:,3:6]
            point    += increment[:,0:3]

            pointsqr = clc.sqrnorm(point)

            ## Проверяем на пересечение с объектами сцены
            ## Аккреционный диск
            mask_crossing = np.logical_xor(old_point[:,1] > 0.0, \
                                               point[:,1] > 0.0)
            mask_distance = np.logical_and((pointsqr < clc.disk_outer_sqr), \
                                           (pointsqr > clc.disk_inner_sqr))

            disk_mask = np.logical_and(mask_crossing, mask_distance)

            if (disk_mask.any()):
                lambdaa     = -point[:, 1] / velocity[:, 1]
                colpoint    = point + lambdaa[:, np.newaxis] * velocity
                colpointsqr = clc.sqrnorm(colpoint)

                phi = np.arctan2(colpoint[:, 0],point[:, 2])

                uv = np.zeros((pixels_per_chunk, 2))

                uv[:, 0] = ((phi + 2 * np.pi) % (2 * np.pi)) / (2 * np.pi)
                uv[:, 1] = (np.sqrt(colpointsqr) - f.disk_inner_r) / \
                           (f.disk_outer_r - f.disk_inner_r)
                
                diskcolor = clc.lookup(f.texarr_disk, np.clip(uv, 0.0, 1.0))
                diskalpha = disk_mask * np.clip(clc.sqrnorm(diskcolor) / \
                                               3.0, 0.0, 1.0)

                object_colour = clc.blendcolors(diskcolor, diskalpha, \
                                            object_colour, object_alpha)
                object_alpha  = clc.blendalpha(diskalpha, object_alpha)

            ## Горизонт событий
            oldpointsqr = clc.sqrnorm(old_point)
            mask_horizon = np.logical_and((pointsqr < 1), \
                                          (clc.sqrnorm(old_point) > 1))

            if mask_horizon.any() :

                lambdaa = 1.0 - ((1.0 - oldpointsqr) / \
                                 ((pointsqr - oldpointsqr)))[:,np.newaxis]
                colpoint = lambdaa * point + (1 - lambdaa) * old_point

                horizoncolour = black

                horizonalpha = mask_horizon

                object_colour = clc.blendcolors(horizoncolour, horizonalpha, \
                                                object_colour, object_alpha)
                object_alpha = clc.blendalpha(horizonalpha, object_alpha)


        vphi   = np.arctan2(velocity[:, 0], velocity[:, 2])
        vtheta = np.arctan2(velocity[:, 1], clc.norm(velocity[:, [0, 2]]))

        vuv = np.zeros((pixels_per_chunk, 2))

        vuv[:, 0] = np.mod(vphi + 4.5, 2 * np.pi) / (2 * np.pi)
        vuv[:, 1] = (vtheta + np.pi / 2) / (np.pi)

        col_bg = clc.lookup(f.texarr_sky,vuv)[:,0:3]
        col_bg_and_obj = clc.blendcolors(f.sky_disk_rat * col_bg, ones, \
                                         object_colour, object_alpha)

        colour_buffer[chunk] = col_bg_and_obj

        gc.collect()
    print('g')

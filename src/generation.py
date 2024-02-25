import pygame
import math
import random
import numpy

from opensimplex import OpenSimplex

SAMPLE_PER_UNIT = 512
SAMPLE_PER_UNIT_TREES = 32

NOISE1 = OpenSimplex(5)
NOISE2 = OpenSimplex(15)
THRESHOLD_LAYER_ONE = {0:3, 0.1:1, 0.18:2,1:None}
LAYER_TWO_REPARTITION = {0.6:0, 0.2:148, 0.15:164, 0.05:165} # {0:0, 0.4:148, 0.5:164, 0.6:165, 1:None}
LAYER_THREE_REPARTITION = {5:0, 10:1, 40:-1}

LAYER_ONE_CHUNK_DATAS = {}
LAYER_TWO_CHUNK_DATAS = {}

def generate_noise1(tilemap, layer, chunk_pos):
    thresholds = list(THRESHOLD_LAYER_ONE.items())
    m_datas = []
    map_samples = NOISE1.noise2array(
        numpy.array(
            [3.5 * (i + chunk_pos[0] * 16) / SAMPLE_PER_UNIT for i in range(16 + 2)]
        ),
        numpy.array(
            [3.5 * (i + chunk_pos[1] * 16) / SAMPLE_PER_UNIT for i in range(16 + 2)]
        ),
    )
    map_samples = numpy.absolute(map_samples)

    map_samples_2 = NOISE2.noise2array(
        numpy.array(
            [3.5 * (i + chunk_pos[0] * 16) / SAMPLE_PER_UNIT_TREES for i in range(16 + 2)]
        ),
        numpy.array(
            [3.5 * (i + chunk_pos[1] * 16) / SAMPLE_PER_UNIT_TREES for i in range(16 + 2)]
        ),
    )

    LAYER_ONE_CHUNK_DATAS[chunk_pos] = map_samples

    # From height float values to integer values representing the type of tile
    for j in range(tilemap.chunk_size + 2):
        l = []
        for i in range(tilemap.chunk_size + 2):
            index = 0
            for k in range(len(thresholds) - 1):
                if thresholds[k][0] <= map_samples[j, i] <= thresholds[k + 1][0]:
                    index = thresholds[k][1]
                    if index == 2 and map_samples_2[j, i] < -0.3:
                        index = 1
                        map_samples[j, i] = 0.15
                    break
                
            l.append(index)
        m_datas.append(l)
    return m_datas

def generate_flowers(tilemap, layer, chunk_pos):
    map_samples_layer_one = LAYER_ONE_CHUNK_DATAS[chunk_pos]
    weights, values = list(LAYER_TWO_REPARTITION.keys()), list(LAYER_TWO_REPARTITION.values())
    m_datas = []
    
    # From height float values to integer values representing the type of tile
    for j in range(tilemap.chunk_size + 2):
        l = []
        for i in range(tilemap.chunk_size + 2):
            index = 0
            if map_samples_layer_one[j, i] > 0.2:
                index = random.choices(values, weights=weights)[0]

            l.append(index)
        m_datas.append(l)
    return m_datas

def generate_trees(tilemap, layer, chunk_pos):
    map_samples_layer_one = LAYER_ONE_CHUNK_DATAS[chunk_pos]

    map_samples = NOISE2.noise2array(
        numpy.array(
            [3.5 * (i + chunk_pos[0] * 16) / SAMPLE_PER_UNIT_TREES for i in range(16 + 2)]
        ),
        numpy.array(
            [3.5 * (i + chunk_pos[1] * 16) / SAMPLE_PER_UNIT_TREES for i in range(16 + 2)]
        ),
    )

    weights, values = list(LAYER_THREE_REPARTITION.keys()), list(LAYER_THREE_REPARTITION.values())
    m_datas = numpy.full((tilemap.chunk_size + 2, tilemap.chunk_size + 2), -1)
    
    # From height float values to integer values representing the type of tile
    for j in range(tilemap.chunk_size + 2):
        for i in range(0, tilemap.chunk_size + 2, 2):
            index = -1
            if map_samples_layer_one[j, i] > 0.21 and map_samples[j, i] > 0.1:
                index = random.choices(values, weights=weights)[0]
            m_datas[j][i] = index
    return m_datas

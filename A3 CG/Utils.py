#UTILS
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import os

# Função para carregar um modelo OBJ com materiais
def load_obj(file_path, mtl_path):
    vertices = []
    textures = []
    normals = []
    faces = []
    materials = {}

    # Carregar materiais do arquivo .mtl
    if os.path.exists(mtl_path):
        with open(mtl_path, 'r') as mtl_file:
            current_material = None
            for line in mtl_file:
                values = line.split()
                if not values:
                    continue
                if values[0] == "newmtl":
                    current_material = values[1]
                    materials[current_material] = None
                elif values[0] == "map_Kd" and current_material:
                    materials[current_material] = values[1]  # Caminho da textura

    # Carregar geometria do arquivo .obj
    with open(file_path, 'r') as obj_file:
        current_material = None
        for line in obj_file:
            values = line.split()
            if not values:
                continue
            if values[0] == "v":
                vertices.append([float(v) for v in values[1:4]])
            elif values[0] == "vt":
                textures.append([float(v) for v in values[1:3]])
            elif values[0] == "vn":
                normals.append([float(v) for v in values[1:4]])
            elif values[0] == "usemtl":
                current_material = values[1]
            elif values[0] == "f":
                face = []
                for vertex in values[1:]:
                    v, t, _ = (int(x) if x else 0 for x in vertex.split('/'))
                    face.append((v - 1, t - 1))
                faces.append((face, current_material))

    return vertices, textures, faces, materials

def load_texture(image_path):
    print(f"Carregando textura: {image_path}")
    texture_id = glGenTextures(1)
    texture_surface = pygame.image.load(image_path)

    # Redimensionar textura para potências de 2 (se necessário)
    width, height = texture_surface.get_size()
    if (width & (width - 1)) != 0 or (height & (height - 1)) != 0:
        print(f"Redimensionando textura para potência de 2: {image_path}")
        new_width = 2 ** (width - 1).bit_length()
        new_height = 2 ** (height - 1).bit_length()
        texture_surface = pygame.transform.scale(texture_surface, (new_width, new_height))
        width, height = texture_surface.get_size()

    texture_data = pygame.image.tostring(texture_surface, "RGB", True)

    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture_id

def draw_obj(vertices, textures, faces, texture_map, position=(0, 0, 0), scale=(1, 1, 1), rotation=(0, 0, 0)):
    glEnable(GL_TEXTURE_2D)
    glPushMatrix()
    glTranslatef(*position)
    glScalef(*scale)
    glRotatef(rotation[0], 1, 0, 0)  # Rotação em torno do eixo X
    glRotatef(rotation[1], 0, 1, 0)  # Rotação em torno do eixo Y
    glRotatef(rotation[2], 0, 0, 1)  # Rotação em torno do eixo Z

    for face, material in faces:
        if material in texture_map:
            glBindTexture(GL_TEXTURE_2D, texture_map[material])
        else:
            glDisable(GL_TEXTURE_2D)

        glBegin(GL_TRIANGLES)
        for vertex, tex_coord in face:
            if tex_coord >= 0:
                glTexCoord2fv(textures[tex_coord])
            glVertex3fv(vertices[vertex])
        glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def check_collision(obj_position, obj_size, moto_position):
    ox, oy, oz = obj_position
    osx, osy, osz = obj_size
    mx, my, mz = moto_position
    return ox - osx/2 <= mx <= ox + osx/2 and oz - osz/2 <= mz <= oz + osz/2

def is_on_grass(position):
    # Definição das áreas da pista com base nos vértices fornecidos
    pista_x_min = -5.392707
    pista_x_max = 5.392707
    pista_z_min = -6.040908
    pista_z_max = 6.040908

    # Definição da extensão da grama em torno da pista (por exemplo, 2 unidades)
    grass_extension = 2.0

    grass_x_min = pista_x_min - grass_extension
    grass_x_max = pista_x_max + grass_extension
    grass_z_min = pista_z_min - grass_extension
    grass_z_max = pista_z_max + grass_extension

    # Verificar se a posição está na área de grama fora da pista
    on_grass_x = (grass_x_min < position[0] < pista_x_min or pista_x_max < position[0] < grass_x_max)
    on_grass_z = (grass_z_min < position[2] < pista_z_min or pista_z_max < position[2] < grass_z_max)

    return on_grass_x or on_grass_z


def is_out_of_bounds(position):
    # Definição dos limites do mapa (ajustar conforme necessário)
    map_x_min = -10.0
    map_x_max = 10.0
    map_z_min = -10.0
    map_z_max = 10.0

    return not (map_x_min < position[0] < map_x_max and map_z_min < position[2] < map_z_max)


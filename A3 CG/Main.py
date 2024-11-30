import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from Utils import *
import os


def get_pista_limits(vertices):
    """
    Calcula os limites mínimos e máximos da pista baseado nos vértices.
    """
    x_coords = [v[0] for v in vertices]
    z_coords = [v[2] for v in vertices]

    return {
        "x_min": min(x_coords),
        "x_max": max(x_coords),
        "z_min": min(z_coords),
        "z_max": max(z_coords),
    }


def is_within_limits(position, limits):
    """
    Verifica se uma posição está dentro dos limites especificados.
    """
    x, _, z = position
    return limits["x_min"] <= x <= limits["x_max"] and limits["z_min"] <= z <= limits["z_max"]


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, -2.0, -20.0)

    # Carregar os objetos
    grama_vertices, grama_textures, grama_faces, grama_materials = load_obj("Engine/grama.obj", "Engine/grama.mtl")
    estrada_vertices, estrada_textures, estrada_faces, estrada_materials = load_obj("Engine/estrada.obj", "Engine/estrada.mtl")
    caixa_vertices, caixa_textures, caixa_faces, caixa_materials = load_obj("Engine/caixa.obj", "Engine/caixa.mtl")
    barril_vertices, barril_textures, barril_faces, barril_materials = load_obj("Engine/barril.obj", "Engine/barril.mtl")
    moto_vertices, moto_textures, moto_faces, moto_materials = load_obj("Engine/moto.obj", "Engine/moto.mtl")

    # Carregar texturas
    grama_texture_map = {material: load_texture(os.path.join("Engine", texture_path))
                         for material, texture_path in grama_materials.items()
                         if texture_path and os.path.exists(os.path.join("Engine", texture_path))}
    estrada_texture_map = {material: load_texture(os.path.join("Engine", texture_path))
                           for material, texture_path in estrada_materials.items()
                           if texture_path and os.path.exists(os.path.join("Engine", texture_path))}
    caixa_texture_map = {material: load_texture(os.path.join("Engine", texture_path))
                         for material, texture_path in caixa_materials.items()
                         if texture_path and os.path.exists(os.path.join("Engine", texture_path))}
    barril_texture_map = {material: load_texture(os.path.join("Engine", texture_path))
                          for material, texture_path in barril_materials.items()
                          if texture_path and os.path.exists(os.path.join("Engine", texture_path))}
    moto_texture_map = {material: load_texture(os.path.join("Engine", texture_path))
                        for material, texture_path in moto_materials.items()
                        if texture_path and os.path.exists(os.path.join("Engine", texture_path))}

    # Calcular limites da grama e da estrada
    grama_limits = get_pista_limits(grama_vertices)
    estrada_limits = get_pista_limits(estrada_vertices)

    # Margem de segurança (tamanho da moto ajustado)
    moto_margin_x = 0.5  # Largura da moto
    moto_margin_z = 0.5  # Comprimento da moto

    # Variáveis de controle
    camera_angle_y = 0
    camera_angle_x = 0
    zoom = -20.0

    moto_position = [0.0, 0.0, 0.0]
    base_speed = 0.1
    moto_speed = base_speed
    moto_rotation_x = 0  # Empinar para frente/trás
    moto_rotation_z = 0  # Inclinar para os lados

    # Posições e tamanhos dos obstáculos
    caixa_position = [2.0, 0.1, -0.5]
    barril_position = [-2.0, 0.1, 0.5]
    obstacle_size = [0.8, 0.8, 0.8]  # Tamanho reduzido dos objetos

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    camera_angle_x += 2
                elif event.button == 5:  # Scroll down
                    camera_angle_x -= 2

        keys = pygame.key.get_pressed()

        # Movimentos da câmera
        if keys[pygame.K_LEFT]:
            camera_angle_y += 2
        if keys[pygame.K_RIGHT]:
            camera_angle_y -= 2
        if keys[pygame.K_UP]:
            zoom += 0.5
        if keys[pygame.K_DOWN]:
            zoom -= 0.5

        # Determinar nova posição da moto
        new_position = moto_position[:]
        if keys[pygame.K_a]:
            new_position[2] -= moto_speed
            moto_rotation_x = -15  # Empinar para trás
        elif keys[pygame.K_d]:
            new_position[2] += moto_speed
            moto_rotation_x = 15  # Empinar para frente
        else:
            moto_rotation_x = 0  # Voltar à posição normal

        if keys[pygame.K_w]:
            new_position[0] += moto_speed
            moto_rotation_z = 15  # Inclinar para a esquerda
        elif keys[pygame.K_s]:
            new_position[0] -= moto_speed
        else:
            moto_rotation_z = 0  # Voltar à posição normal

        # Ajustar velocidade com base no terreno
        if is_within_limits(new_position, estrada_limits):
            moto_speed = base_speed  # Velocidade normal na estrada
        elif is_within_limits(new_position, grama_limits):
            moto_speed = base_speed * 0.3  # Reduzir 70% na grama

        # Restringir posição da moto dentro dos limites da grama
        new_position[0] = clamp(new_position[0], grama_limits["x_min"] + moto_margin_x, grama_limits["x_max"] - moto_margin_x)
        new_position[2] = clamp(new_position[2], grama_limits["z_min"] + moto_margin_z, grama_limits["z_max"] - moto_margin_z)

        # Verificar colisões
        if not check_collision(caixa_position, obstacle_size, new_position) and not check_collision(barril_position, obstacle_size, new_position):
            moto_position = new_position

        glLoadIdentity()
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
        glTranslatef(0.0, -2.0, zoom)
        glRotatef(camera_angle_x, 1, 0, 0)
        glRotatef(camera_angle_y, 0, 1, 0)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Renderizar objetos
        draw_obj(grama_vertices, grama_textures, grama_faces, grama_texture_map)
        draw_obj(estrada_vertices, estrada_textures, estrada_faces, estrada_texture_map)
        draw_obj(caixa_vertices, caixa_textures, caixa_faces, caixa_texture_map, position=caixa_position,
                 scale=(0.3, 0.3, 0.3))  # Reduzir tamanho da caixa
        draw_obj(barril_vertices, barril_textures, barril_faces, barril_texture_map, position=barril_position,
                 scale=(0.3, 0.3, 0.3))  # Reduzir tamanho do barril
        draw_obj(moto_vertices, moto_textures, moto_faces, moto_texture_map, position=moto_position,
                 scale=(1.0, 1.0, 1.0), rotation=(moto_rotation_x, 0, moto_rotation_z))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()

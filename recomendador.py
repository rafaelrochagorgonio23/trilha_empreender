from trilhas import TRILHAS

def recomendar_trilha(perfil, objetivo, area):
    for trilha in TRILHAS:
        if trilha['area'] == area:
            return trilha
    return TRILHAS[0]

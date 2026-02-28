import statistics

def veredicto_ia(app_nombre, consumo_actual, historial):
    # Si la app es nueva y no hay historial, usamos un "sentido común" básico
    if len(historial) < 5:
        # Regla simple: si es chat y pasa de 20%, ya es sospechoso de entrada
        if "whatsapp" in app_nombre.lower() and consumo_actual > 20:
            return False, 5, 15 # (esta_mal, min_normal, max_normal)
        return True, 0, 100 # Por ahora aceptamos todo hasta aprender

    # Si hay historial, usamos Z-Score (Estadística)
    media = statistics.mean(historial)
    desviacion = statistics.stdev(historial) if len(historial) > 1 else 1
    
    # Definimos el rango normal como: Media +/- 2 veces la desviación
    r_min = max(0, media - (2 * desviacion))
    r_max = media + (2 * desviacion)
    
    # El veredicto
    esta_dentro = r_min <= consumo_actual <= r_max
    
    return esta_dentro, round(r_min, 1), round(r_max, 1)

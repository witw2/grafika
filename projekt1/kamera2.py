DEBUG = False

import pygame
import math
import sys
import random


SZEROKOSC_EKRANU, WYSOKOSC_EKRANU = 1920, 1080
BIALY = (255, 255, 255)
CZARNY = (0, 0, 0)
KOLOR = (200, 0, 0)

mnoznik = 4

PREDKOSC_RUCHU = 5.0 / mnoznik
PREDKOSC_OBROTU = 0.012 / mnoznik
PREDKOSC_ZOOM = 0.01 / mnoznik
BLISKIE_CIECIE = 1
MARTWA_STREFA_JOYSTICKA = 0.1

POCZATKOWY_KAM_X, POCZATKOWY_KAM_Y, POCZATKOWY_KAM_Z = 0.0, 50.0, -100.0
POCZATKOWE_ODCHYLENIE, POCZATKOWE_POCHYLENIE, POCZATKOWE_PRZECHYLENIE = 0.0, 0.0, 0.0
POCZATKOWE_POLE_WIDZENIA = 60 * math.pi / 180

kam_x, kam_y, kam_z = POCZATKOWY_KAM_X, POCZATKOWY_KAM_Y, POCZATKOWY_KAM_Z
pole_widzenia = POCZATKOWE_POLE_WIDZENIA
MIN_POLE_WIDZENIA = 20 * math.pi / 180
MAX_POLE_WIDZENIA = 120 * math.pi / 180

def dodaj_wektory(v1, v2):
    return {'x': v1['x'] + v2['x'], 'y': v1['y'] + v2['y'], 'z': v1['z'] + v2['z']}

def odejmij_wektory(v1, v2):
    return {'x': v1['x'] - v2['x'], 'y': v1['y'] - v2['y'], 'z': v1['z'] - v2['z']}

def mnoz_wektor_przez_skalar(v, s):
    return {'x': v['x'] * s, 'y': v['y'] * s, 'z': v['z'] * s}

def iloczyn_skalarny(v1, v2):
    return v1['x'] * v2['x'] + v1['y'] * v2['y'] + v1['z'] * v2['z']

def iloczyn_wektorowy(v1, v2):
    return {
        'x': v1['y'] * v2['z'] - v1['z'] * v2['y'],
        'y': v1['z'] * v2['x'] - v1['x'] * v2['z'],
        'z': v1['x'] * v2['y'] - v1['y'] * v2['x']
    }

def wektor_dlugosc_kwadrat(v):
    return v['x']**2 + v['y']**2 + v['z']**2

def wektor_dlugosc(v):
    dl_kw = wektor_dlugosc_kwadrat(v)
    return math.sqrt(dl_kw) if dl_kw > 1e-12 else 0.0

def normalizuj(v):
    dl = wektor_dlugosc(v)
    if dl < 1e-9:
        return {'x': v['x'], 'y': v['y'], 'z': v['z']}
    inv_dl = 1.0 / dl
    return mnoz_wektor_przez_skalar(v, inv_dl)

def obroc_wektor(wektor, os, kat):
    if abs(kat) < 1e-9: return wektor
    os = normalizuj(os)
    cos_kat = math.cos(kat)
    sin_kat = math.sin(kat)

    term1 = mnoz_wektor_przez_skalar(wektor, cos_kat)
    cross_prod = iloczyn_wektorowy(os, wektor)
    term2 = mnoz_wektor_przez_skalar(cross_prod, sin_kat)
    dot_prod = iloczyn_skalarny(os, wektor)
    term3_scalar = dot_prod * (1 - cos_kat)
    term3 = mnoz_wektor_przez_skalar(os, term3_scalar)

    return dodaj_wektory(dodaj_wektory(term1, term2), term3)

def ortonormalizuj(do_przodu, gora, prawo):
    do_przodu = normalizuj(do_przodu)
    prawo = normalizuj(iloczyn_wektorowy(do_przodu, gora))
    gora = normalizuj(iloczyn_wektorowy(prawo, do_przodu))
    return do_przodu, gora, prawo

def oblicz_baze_z_eulerow(odchylenie, pochylenie, przechylenie):
    cos_y, sin_y = math.cos(odchylenie), math.sin(odchylenie)
    cos_p, sin_p = math.cos(pochylenie), math.sin(pochylenie)
    cos_r, sin_r = math.cos(przechylenie), math.sin(przechylenie)
    do_przodu = { 'x': sin_y * cos_p, 'y': -sin_p, 'z': cos_y * cos_p }
    prawo0 = { 'x': cos_y, 'y': 0, 'z': -sin_y }
    gora0 = iloczyn_wektorowy(prawo0, do_przodu)

    prawo = obroc_wektor(prawo0, do_przodu, przechylenie)
    gora = obroc_wektor(gora0, do_przodu, przechylenie)

    do_przodu, gora, prawo = ortonormalizuj(do_przodu, gora, prawo)
    return do_przodu, prawo, gora

kam_do_przodu, kam_prawo, kam_gora = oblicz_baze_z_eulerow(
    POCZATKOWE_ODCHYLENIE, POCZATKOWE_POCHYLENIE, POCZATKOWE_PRZECHYLENIE
)

def stworz_wierzcholki_prostopadloscianu(sx, sy, sz, szerokosc, wysokosc, glebokosc):
    pol_szer, pol_wys, pol_gleb = szerokosc / 2, wysokosc / 2, glebokosc / 2
    return [
        {'x': sx - pol_szer, 'y': sy - pol_wys, 'z': sz - pol_gleb},
        {'x': sx + pol_szer, 'y': sy - pol_wys, 'z': sz - pol_gleb},
        {'x': sx + pol_szer, 'y': sy + pol_wys, 'z': sz - pol_gleb},
        {'x': sx - pol_szer, 'y': sy + pol_wys, 'z': sz - pol_gleb},
        {'x': sx - pol_szer, 'y': sy - pol_wys, 'z': sz + pol_gleb},
        {'x': sx + pol_szer, 'y': sy - pol_wys, 'z': sz + pol_gleb},
        {'x': sx + pol_szer, 'y': sy + pol_wys, 'z': sz + pol_gleb},
        {'x': sx - pol_szer, 'y': sy + pol_wys, 'z': sz + pol_gleb}
    ]
krawedzie_prostopadloscianu = [
    (0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6),
    (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)
]
sciany_prostopadloscianu = [
    (0, 3, 2, 1), (5, 6, 7, 4), (4, 7, 3, 0),
    (1, 2, 6, 5), (3, 7, 6, 2), (4, 0, 1, 5)
]
def generuj_losowe_kolory_scian(liczba_scian):
    return [(random.randint(50, 240), random.randint(50, 240), random.randint(50, 240)) for _ in range(liczba_scian)]

dane_sceny = [
    {'wierzcholki': stworz_wierzcholki_prostopadloscianu(sx=0, sy=0, sz=600, szerokosc=150, wysokosc=150, glebokosc=150), 'krawedzie': krawedzie_prostopadloscianu, 'sciany': sciany_prostopadloscianu, 'kolor': KOLOR, 'kolory_scian': generuj_losowe_kolory_scian(len(sciany_prostopadloscianu))},
    {'wierzcholki': stworz_wierzcholki_prostopadloscianu(sx=-250, sy=100, sz=800, szerokosc=50, wysokosc=300, glebokosc=50), 'krawedzie': krawedzie_prostopadloscianu, 'sciany': sciany_prostopadloscianu, 'kolor': KOLOR, 'kolory_scian': generuj_losowe_kolory_scian(len(sciany_prostopadloscianu))},
    {'wierzcholki': stworz_wierzcholki_prostopadloscianu(sx=250, sy=-50, sz=1000, szerokosc=300, wysokosc=50, glebokosc=200), 'krawedzie': krawedzie_prostopadloscianu, 'sciany': sciany_prostopadloscianu, 'kolor': KOLOR, 'kolory_scian': generuj_losowe_kolory_scian(len(sciany_prostopadloscianu))},
    {'wierzcholki': stworz_wierzcholki_prostopadloscianu(sx=0, sy=0, sz=1300, szerokosc=400, wysokosc=50, glebokosc=50), 'krawedzie': krawedzie_prostopadloscianu, 'sciany': sciany_prostopadloscianu, 'kolor': KOLOR, 'kolory_scian': generuj_losowe_kolory_scian(len(sciany_prostopadloscianu))},
    {'wierzcholki': stworz_wierzcholki_prostopadloscianu(sx=150, sy=150, sz=700, szerokosc=80, wysokosc=80, glebokosc=250), 'krawedzie': krawedzie_prostopadloscianu, 'sciany': sciany_prostopadloscianu, 'kolor': KOLOR, 'kolory_scian': generuj_losowe_kolory_scian(len(sciany_prostopadloscianu))}
]

if DEBUG:
    dane_sceny = [
        {'wierzcholki': stworz_wierzcholki_prostopadloscianu(sx=0, sy=0, sz=800.0, szerokosc=500.0, wysokosc=50.0,glebokosc=25.0),
         'krawedzie': krawedzie_prostopadloscianu,
         'sciany': sciany_prostopadloscianu,
         'kolor': (220, 20, 60),
         'kolory_scian': generuj_losowe_kolory_scian(len(sciany_prostopadloscianu))},
        {'wierzcholki': stworz_wierzcholki_prostopadloscianu(sx=0, sy=0, sz=800.0, szerokosc=50.0, wysokosc=500.0,glebokosc=25.0),
         'krawedzie': krawedzie_prostopadloscianu,
         'sciany': sciany_prostopadloscianu,
         'kolor': (30, 144, 255),
         'kolory_scian': generuj_losowe_kolory_scian(len(sciany_prostopadloscianu))}
    ]

def zmien_kolory_scian(dane_sceny):
    for ksztalt in dane_sceny:
        ksztalt['kolory_scian'] = generuj_losowe_kolory_scian(len(ksztalt['sciany']))

def swiat_do_kamery(wierzcholek, pos_kamery, baza_p, baza_pr, baza_g):
    v = odejmij_wektory(wierzcholek, pos_kamery)
    return {
        'x': iloczyn_skalarny(v, baza_pr),
        'y': iloczyn_skalarny(v, baza_g),
        'z': iloczyn_skalarny(v, baza_p)
    }

def rzutuj_wierzcholek(w):
    if pole_widzenia <= 0 or pole_widzenia >= math.pi: return None
    if w['z'] < BLISKIE_CIECIE: return None
    tan_fov_half = math.tan(pole_widzenia / 2)
    if abs(tan_fov_half) < 1e-6: return None

    d = (WYSOKOSC_EKRANU / 2) / tan_fov_half
    ekran_x = (w['x'] * d) / w['z'] + SZEROKOSC_EKRANU / 2
    ekran_y = -(w['y'] * d) / w['z'] + WYSOKOSC_EKRANU / 2

    return ekran_x, ekran_y

def pole_ze_znakiem(punkty):
    if punkty is None or len(punkty) < 3: return 0
    pole = 0.0
    j = len(punkty) - 1
    for i in range(len(punkty)):
        if punkty[j] is None or punkty[i] is None: return 0
        pole += (punkty[j][0] + punkty[i][0]) * (punkty[j][1] - punkty[i][1])
        j = i
    return pole / 2.0

def odczytaj_os(indeks_osi):
    if indeks_osi >= 0 and indeks_osi < liczba_osi:
        wartosc = joystick.get_axis(indeks_osi)
        return wartosc if abs(wartosc) > MARTWA_STREFA_JOYSTICKA else 0.0
    return 0.0

pygame.init()
pygame.joystick.init()
joystick = None
liczba_joystickow = pygame.joystick.get_count()
liczba_osi = 0; liczba_hatow = 0

aktualny_tryb_sortowania = 0 # 0: Średnia Z, 1: Min Z, 2: Max Z
nazwy_trybow_sortowania = ["Średnia Z", "Min Z (Najbliższy)", "Max Z (Najdalszy)"]

if liczba_joystickow > 0:
    try:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        liczba_osi = joystick.get_numaxes(); liczba_hatow = joystick.get_numhats()
        print(f"Znaleziono kontroler: {joystick.get_name()} ({liczba_osi} osi, {liczba_hatow} hat)")
    except pygame.error as e: joystick = None; print(f"Błąd joysticka: {e}")
else: print("Nie znaleziono kontrolera.")

ekran = pygame.display.set_mode((SZEROKOSC_EKRANU, WYSOKOSC_EKRANU))
pygame.display.set_caption("Kamera wirtualna (Nowy system rotacji)")
zegar = pygame.time.Clock()
tryb_wypelnienia = False
wcisniety_M = False
wcisniety_R3 = False
wcisniety_6 = False
wcisniety_P = False

dziala = True
while dziala:
    for zdarzenie in pygame.event.get():
        if zdarzenie.type == pygame.QUIT: dziala = False
        if zdarzenie.type == pygame.KEYDOWN:
            if zdarzenie.key == pygame.K_ESCAPE: dziala = False
            if zdarzenie.key == pygame.K_r:
                kam_x, kam_y, kam_z = POCZATKOWY_KAM_X, POCZATKOWY_KAM_Y, POCZATKOWY_KAM_Z
                kam_do_przodu, kam_prawo, kam_gora = oblicz_baze_z_eulerow(
                    POCZATKOWE_ODCHYLENIE, POCZATKOWE_POCHYLENIE, POCZATKOWE_PRZECHYLENIE
                )
                pole_widzenia = POCZATKOWE_POLE_WIDZENIA
            if zdarzenie.key == pygame.K_m:
                if not wcisniety_M:
                    tryb_wypelnienia = not tryb_wypelnienia
                    wcisniety_M = True
            if zdarzenie.key == pygame.K_j:
                zmien_kolory_scian(dane_sceny)
            if zdarzenie.key == pygame.K_p:
                if not wcisniety_P:
                    aktualny_tryb_sortowania = (aktualny_tryb_sortowania + 1) % len(nazwy_trybow_sortowania)
                    nowy_tytul = f"Kamera wirtualna (Sortowanie: {nazwy_trybow_sortowania[aktualny_tryb_sortowania]})"
                    pygame.display.set_caption(nowy_tytul)
                    print(f"Zmieniono tryb sortowania na: {nazwy_trybow_sortowania[aktualny_tryb_sortowania]}")
                    wcisniety_P = True

        if zdarzenie.type == pygame.KEYUP:
            if zdarzenie.key == pygame.K_m:
                wcisniety_M = False
            if zdarzenie.key == pygame.K_p:
                wcisniety_P = False

        if zdarzenie.type == pygame.JOYBUTTONDOWN:
            if joystick is not None and zdarzenie.instance_id == joystick.get_instance_id():
                if zdarzenie.button == 7:
                    kam_x, kam_y, kam_z = POCZATKOWY_KAM_X, POCZATKOWY_KAM_Y, POCZATKOWY_KAM_Z
                    kam_do_przodu, kam_prawo, kam_gora = oblicz_baze_z_eulerow(
                        POCZATKOWE_ODCHYLENIE, POCZATKOWE_POCHYLENIE, POCZATKOWE_PRZECHYLENIE
                    )
                    pole_widzenia = POCZATKOWE_POLE_WIDZENIA
                if zdarzenie.button == 9:
                    if not wcisniety_R3:
                        tryb_wypelnienia = not tryb_wypelnienia
                        wcisniety_R3 = True
                if zdarzenie.button == 6:
                    if not wcisniety_6:
                        zmien_kolory_scian(dane_sceny)
                        wcisniety_6 = True
        if zdarzenie.type == pygame.JOYBUTTONUP:
            if joystick is not None and zdarzenie.instance_id == joystick.get_instance_id():
                if zdarzenie.button == 9:
                    wcisniety_R3 = False
                if zdarzenie.button == 6:
                    wcisniety_6 = False

    klawisze = pygame.key.get_pressed()
    wejscie_przod_tyl, wejscie_lewo_prawo, wejscie_gora_dol = 0.0, 0.0, 0.0
    wejscie_odchylenie, wejscie_pochylenie, wejscie_przechylenie = 0.0, 0.0, 0.0
    wejscie_zoom = 0.0
    czy_sprint = False
    if klawisze[pygame.K_w]: wejscie_przod_tyl += 1.0
    if klawisze[pygame.K_s]: wejscie_przod_tyl -= 1.0
    if klawisze[pygame.K_a]: wejscie_lewo_prawo -= 1.0
    if klawisze[pygame.K_d]: wejscie_lewo_prawo += 1.0
    if klawisze[pygame.K_SPACE]: wejscie_gora_dol += 1.0
    if klawisze[pygame.K_f] or klawisze[pygame.K_LCTRL]: wejscie_gora_dol -= 1.0
    if klawisze[pygame.K_RIGHT]: wejscie_odchylenie -= 1.0
    if klawisze[pygame.K_LEFT]: wejscie_odchylenie += 1.0
    if klawisze[pygame.K_DOWN]: wejscie_pochylenie -= 1.0
    if klawisze[pygame.K_UP]: wejscie_pochylenie += 1.0
    if klawisze[pygame.K_e]: wejscie_przechylenie += 1.0
    if klawisze[pygame.K_q]: wejscie_przechylenie -= 1.0
    if klawisze[pygame.K_EQUALS] or klawisze[pygame.K_PLUS] or klawisze[pygame.K_KP_PLUS]: wejscie_zoom -= 1.0
    if klawisze[pygame.K_MINUS] or klawisze[pygame.K_KP_MINUS]: wejscie_zoom += 1.0
    if klawisze[pygame.K_LSHIFT]: czy_sprint = True

    if joystick is not None:
        wejscie_lewo_prawo += odczytaj_os(0)
        wejscie_przod_tyl -= odczytaj_os(1)
        wejscie_odchylenie -= odczytaj_os(2)
        wejscie_pochylenie -= odczytaj_os(3)
        if liczba_osi > 4:
            trigger_lewy = (odczytaj_os(4) + 1) / 2
            wejscie_zoom += trigger_lewy
        if liczba_osi > 5:
            trigger_prawy = (odczytaj_os(5) + 1) / 2
            wejscie_zoom -= trigger_prawy
        if joystick.get_button(3): wejscie_gora_dol += 1.0
        if joystick.get_button(0): wejscie_gora_dol -= 1.0
        if joystick.get_button(5): wejscie_przechylenie += 1.0
        if joystick.get_button(4): wejscie_przechylenie -= 1.0
        if joystick.get_button(8): czy_sprint = True

    delta_yaw_angle = wejscie_odchylenie * PREDKOSC_OBROTU
    delta_pitch_angle = wejscie_pochylenie * PREDKOSC_OBROTU
    delta_roll_angle = wejscie_przechylenie * PREDKOSC_OBROTU * 2

    if abs(delta_yaw_angle) > 1e-9:
        kam_do_przodu = obroc_wektor(kam_do_przodu, kam_gora, delta_yaw_angle)
        kam_prawo = obroc_wektor(kam_prawo, kam_gora, delta_yaw_angle)

    if abs(delta_pitch_angle) > 1e-9:
        kam_do_przodu = obroc_wektor(kam_do_przodu, kam_prawo, delta_pitch_angle)
        kam_gora = obroc_wektor(kam_gora, kam_prawo, delta_pitch_angle)

    if abs(delta_roll_angle) > 1e-9:
        kam_prawo = obroc_wektor(kam_prawo, kam_do_przodu, delta_roll_angle)
        kam_gora = obroc_wektor(kam_gora, kam_do_przodu, delta_roll_angle)

    kam_do_przodu, kam_gora, kam_prawo = ortonormalizuj(kam_do_przodu, kam_gora, kam_prawo)

    biezaca_predkosc_ruchu = PREDKOSC_RUCHU * 3 if czy_sprint else PREDKOSC_RUCHU
    dx_przod = kam_do_przodu['x'] * wejscie_przod_tyl
    dy_przod = kam_do_przodu['y'] * wejscie_przod_tyl
    dz_przod = kam_do_przodu['z'] * wejscie_przod_tyl
    dx_prawo = kam_prawo['x'] * wejscie_lewo_prawo
    dy_prawo = kam_prawo['y'] * wejscie_lewo_prawo
    dz_prawo = kam_prawo['z'] * wejscie_lewo_prawo
    dx_gora = kam_gora['x'] * wejscie_gora_dol
    dy_gora = kam_gora['y'] * wejscie_gora_dol
    dz_gora = kam_gora['z'] * wejscie_gora_dol
    delta_x = (dx_przod + dx_prawo + dx_gora) * biezaca_predkosc_ruchu
    delta_y = (dy_przod + dy_prawo + dy_gora) * biezaca_predkosc_ruchu
    delta_z = (dz_przod + dz_prawo + dz_gora) * biezaca_predkosc_ruchu
    kam_x += delta_x
    kam_y += delta_y
    kam_z += delta_z

    pole_widzenia += wejscie_zoom * PREDKOSC_ZOOM
    pole_widzenia = max(min(pole_widzenia, MAX_POLE_WIDZENIA), MIN_POLE_WIDZENIA)

    ekran.fill(BIALY)
    pos_kamery_dict = {'x': kam_x, 'y': kam_y, 'z': kam_z}

    if tryb_wypelnienia:
        sciany_do_narysowania = []
        for dane_ksztaltu in dane_sceny:
            wierzcholki = dane_ksztaltu['wierzcholki']
            sciany = dane_ksztaltu['sciany']
            kolory_scian_bryly = dane_ksztaltu['kolory_scian']

            wierzcholki_kamery = [swiat_do_kamery(w, pos_kamery_dict, kam_do_przodu, kam_prawo, kam_gora) for w in
                                  wierzcholki]
            rzutowane_punkty_wszystkie = [rzutuj_wierzcholek(wk) for wk in wierzcholki_kamery]

            for idx_sciany, sciana_indeksy in enumerate(sciany):
                punkty_ekranowe_sciany_float = []
                punkty_ekranowe_sciany_int = []
                czy_sciana_poprawna = True
                suma_z_sciany = 0.0
                min_z_sciany = float('inf')
                max_z_sciany = float('-inf')
                liczba_wierzcholkow_sciany = 0

                for indeks in sciana_indeksy:
                    if not (0 <= indeks < len(rzutowane_punkty_wszystkie) and 0 <= indeks < len(wierzcholki_kamery)):
                        czy_sciana_poprawna = False;
                        break

                    punkt_ekranowy_float = rzutowane_punkty_wszystkie[indeks]
                    wierzcholek_kamery = wierzcholki_kamery[indeks]

                    # Sprawdzenie bliskiego cięcia i poprawności rzutowania
                    if wierzcholek_kamery['z'] < BLISKIE_CIECIE:
                        czy_sciana_poprawna = False;
                        break
                    if punkt_ekranowy_float is None:
                        czy_sciana_poprawna = False;
                        break

                    punkty_ekranowe_sciany_float.append(punkt_ekranowy_float)
                    punkty_ekranowe_sciany_int.append((int(punkt_ekranowy_float[0]), int(punkt_ekranowy_float[1])))

                    # ZMIANA: Aktualizacja sumy, min i max Z
                    z_wierzcholka = wierzcholek_kamery['z']
                    suma_z_sciany += z_wierzcholka
                    min_z_sciany = min(min_z_sciany, z_wierzcholka)
                    max_z_sciany = max(max_z_sciany, z_wierzcholka)
                    liczba_wierzcholkow_sciany += 1

                if not czy_sciana_poprawna or liczba_wierzcholkow_sciany < 3: continue

                pole = pole_ze_znakiem(punkty_ekranowe_sciany_float)
                if pole < 1e-6:
                    continue

                srednie_z_sciany = suma_z_sciany / liczba_wierzcholkow_sciany if liczba_wierzcholkow_sciany > 0 else float(
                    'inf')
                kolor_sciany = kolory_scian_bryly[idx_sciany]
                sciany_do_narysowania.append({
                    'punkty_ekranowe': punkty_ekranowe_sciany_int,
                    'srednie_z': srednie_z_sciany,
                    'min_z': min_z_sciany,
                    'max_z': max_z_sciany,
                    'kolor': kolor_sciany
                })

        if aktualny_tryb_sortowania == 0:  # Średnia Z
            sciany_do_narysowania.sort(key=lambda s: s['srednie_z'], reverse=True)
        elif aktualny_tryb_sortowania == 1:  # Minimalna Z (Najbliższy punkt)
            # Sortujemy malejąco wg min Z, aby najpierw rysować te, których najbliższy punkt jest najdalej
            sciany_do_narysowania.sort(key=lambda s: s['min_z'], reverse=True)
        elif aktualny_tryb_sortowania == 2:  # Maksymalna Z (Najdalszy punkt)
            # Sortujemy malejąco wg max Z, aby najpierw rysować te, których najdalszy punkt jest najdalej
            sciany_do_narysowania.sort(key=lambda s: s['max_z'], reverse=True)

        for sciana_dane in sciany_do_narysowania:
            if sciana_dane['punkty_ekranowe'] and len(sciana_dane['punkty_ekranowe']) >= 3:
                pygame.draw.polygon(ekran, sciana_dane['kolor'], sciana_dane['punkty_ekranowe'])
                pygame.draw.polygon(ekran, CZARNY, sciana_dane['punkty_ekranowe'], 1)


    else:
        for dane_ksztaltu in dane_sceny:
            wierzcholki = dane_ksztaltu['wierzcholki']
            krawedzie = dane_ksztaltu['krawedzie']
            kolor = dane_ksztaltu['kolor']

            wierzcholki_kamery = [swiat_do_kamery(w, pos_kamery_dict, kam_do_przodu, kam_prawo, kam_gora) for w in wierzcholki]

            for krawedz in krawedzie:
                indeks_p1, indeks_p2 = krawedz
                if not (0 <= indeks_p1 < len(wierzcholki_kamery) and 0 <= indeks_p2 < len(wierzcholki_kamery)): continue

                wk1 = wierzcholki_kamery[indeks_p1]
                wk2 = wierzcholki_kamery[indeks_p2]
                z1, z2 = wk1['z'], wk2['z']
                widoczny1 = z1 >= BLISKIE_CIECIE
                widoczny2 = z2 >= BLISKIE_CIECIE

                if widoczny1 and widoczny2:
                    p1_proj = rzutuj_wierzcholek(wk1)
                    p2_proj = rzutuj_wierzcholek(wk2)
                    if p1_proj and p2_proj:
                         p1_int = (int(p1_proj[0]), int(p1_proj[1]))
                         p2_int = (int(p2_proj[0]), int(p2_proj[1]))
                         pygame.draw.line(ekran, kolor, p1_int, p2_int, 2)
                elif widoczny1 or widoczny2:
                    if not widoczny1:
                        wk1, wk2 = wk2, wk1
                        z1, z2 = z2, z1

                    if abs(z2 - z1) < 1e-9: continue
                    t = (BLISKIE_CIECIE - z1) / (z2 - z1)
                    if not (0.0 <= t <= 1.0): continue

                    x_clip = wk1['x'] + t * (wk2['x'] - wk1['x'])
                    y_clip = wk1['y'] + t * (wk2['y'] - wk1['y'])
                    w_clip = {'x': x_clip, 'y': y_clip, 'z': BLISKIE_CIECIE}

                    p1_proj = rzutuj_wierzcholek(wk1)
                    p_clip_proj = rzutuj_wierzcholek(w_clip)

                    if p1_proj and p_clip_proj:
                         p1_int = (int(p1_proj[0]), int(p1_proj[1]))
                         p_clip_int = (int(p_clip_proj[0]), int(p_clip_proj[1]))
                         pygame.draw.line(ekran, kolor, p1_int, p_clip_int, 2)

    pygame.display.flip()
    zegar.tick(60 * mnoznik)

pygame.quit()
sys.exit()